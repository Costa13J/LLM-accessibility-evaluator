import dspy
from dspy.dsp.utils import deduplicate 
import os
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.evaluate import Evaluate
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from trainsets import trainset, trainset_no_submit
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dspy import Embedder
import chromadb
from chromadb.utils import embedding_functions
from dspy.retrieve.chromadb_rm import ChromadbRM


import time

counter = 0  # Initialize the global counter

#url = "https://store.steampowered.com/join/?redir=app%2F2669320%2FEA_SPORTS_FC_25%2F%3Fsnr%3D1_4_4__129_1&snr=1_60_4__62"
#url = "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b" #Tem erros de cues e lança submit
url = "https://www.continente.pt/loja-online/contactos/" #Tem erros de cues mas não lança submit


load_dotenv()
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY", "")

if not os.environ["MISTRAL_API_KEY"]:
    raise ValueError("MISTRAL_API_KEY not found. Check your .env file.")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="wcag_guidelines")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

crm = ChromadbRM(
    collection_name="wcag_guidelines",
    persist_directory="./chroma_db",
    embedding_function=embedding_model.encode,
    k=8  # top-k
)

# Configure DSPy with the model and retriever
mini = dspy.LM('mistral/mistral-large-latest')
dspy.settings.configure(lm=mini, rm=crm)

def setup_webdriver():
    """Configures and launches a headless Chrome browser."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without UI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())  
    return webdriver.Chrome(service=service, options=chrome_options)

# Extracts visible input fields, labels, and error messages from the form.
def extract_visible_fields(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fields = []

    for input_field in soup.find_all(['input', 'textarea', 'select']):
        if input_field.get('type') in ['hidden', 'submit', 'button']:
            continue  # Ignore non-user input fields

        label = input_field.find_parent('label')
        error_messages = []

        if label:
            # Collect all attributes that contain 'error' in the name
            for attr_name, attr_value in label.attrs.items():
                if "error" in attr_name.lower():
                    error_messages.append(attr_value.strip())

        field_info = {
            "label": label.text.strip() if label else "No Label",
            "name": input_field.get("name", ""),
            "id": input_field.get("id", ""),
            "type": input_field.get("type", ""),
            "value": input_field.get("value", ""),
            "required": "required" if input_field.has_attr("required") else "no",
            "disabled": "disabled" if input_field.has_attr("disabled") else "no",
            "readonly": "readonly" if input_field.has_attr("readonly") else "no",
            "errors": error_messages
        }
        fields.append(field_info)
        
    # Extract error messages from elements with class 'error' that are visibly rendered
    errors = [e.text.strip() for e in soup.select(".error") if e.get('style') != 'display:none;']
    
    # Also collect non-empty error messages from the extracted fields
    field_errors = [msg for f in fields for msg in f["errors"] if msg] #TODO verificar se não e melhor so este

    return {"fields": fields, "errors": errors + field_errors}

# Extracts all buttons and any element with an onclick event to pass to the LLM.
def extract_buttons_for_llm(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = []

    # Find buttons and input elements
    for elem in soup.find_all(['button', 'input']):
        elements.append({
            "text": elem.text.strip() if elem.name == "button" else "No Text",
            "id": elem.get("id", "No ID"),
            "name": elem.get("name", "No Name"),
            "onclick": elem.get("onclick", "No OnClick"),
            "type": elem.get("type", "No Type"),
        })

    # Find any element with an onclick event 
    for elem in soup.find_all(onclick=True):
        elements.append({
            "text": elem.text.strip() or "No Text",
            "id": elem.get("id", "No ID"),
            "name": elem.get("name", "No Name"),
            "onclick": elem.get("onclick", "No OnClick"),
            "type": elem.name
        })
    print(elements)
    return elements

# LLM identifies the actual submit button 
class IdentifySubmitButton(dspy.Signature):

    buttons_info = dspy.InputField(desc="List of all button elements on the form (text, id, name, onclick, type).")
    predicted_button_id = dspy.OutputField(desc="The exact XPATH of the button that is the most likely submit or advance button of the form (or 'None' if no ID exists).")

identify_submit_button = dspy.ChainOfThought(IdentifySubmitButton)

# Uses an LLM to predict which button is the submit button.
def get_submit_button_id_from_llm(buttons):

    response = identify_submit_button(buttons_info=str(buttons))
    print("====BUTTON XPATH GIVEN BY THE LLM====")
    print(response.predicted_button_id)
    return response.predicted_button_id if response.predicted_button_id != "None" else None

# Loads and injects an external JavaScript file for mutation observation
def inject_mutation_observer(driver, script_path="mutationObserver.js"):
    
    try:
        with open(script_path, "r", encoding="utf-8") as file:
            mutation_script = file.read()
        
        driver.execute_script(mutation_script)
        print("Mutation Observer injected successfully.")
    except FileNotFoundError:
        print(f"Error: JavaScript file '{script_path}' not found.")
    except Exception as e:
        print(f"Unexpected error while injecting Mutation Observer: {e}")

# Finds and clicks the submit button using an LLM to identify it.
def find_and_click_submit_button(driver):

    try:
        inject_mutation_observer(driver)
        buttons = extract_buttons_for_llm(driver)
        if not buttons:
            print("No buttons found on the page.")
            return None  # No interaction possible

        # Ask LLM which button is the submit button
        submit_button_id = get_submit_button_id_from_llm(buttons)

        if not submit_button_id or submit_button_id == "None":
            print("LLM could not identify a submit button. Skipping interaction.")
            return None  # Skip interaction

        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, submit_button_id)) #TODO button can have no id 
            )
            submit_button.click()
            print("Submit button clicked!")
            return "clicked"

        except Exception as e:
            print(f"Error clicking submit button: {e}")
            print("Trying JavaScript click...")
    
            #TODO should be removed because to fall into this click can mean button is disabled or not available
            try:
                driver.execute_script("arguments[0].click();", submit_button)
                print("JavaScript click executed successfully!")
                return "clicked"
    
            except Exception as js_e:
                print(f"JavaScript click failed: {js_e}")
                print("Skipping interaction, testing only pre-submission state.")
                return None  # Skip interaction due to unclickable button

    except Exception as e:
        print(f"Unexpected error in find_and_click_submit_button: {e}")
        return None

# Retrieves captured mutations from the Mutation Observer.
def extract_mutation_observer_results(driver):
    return driver.execute_script("return window.mutationRecords;")

# Loads a webpage, extracts form fields before and after interaction.
def extract_html_with_states(url):

    driver = setup_webdriver()
    driver.get(url)

    initial_data = extract_visible_fields(driver)

    action_result = find_and_click_submit_button(driver)

    if action_result == "clicked":
        time.sleep(2)  # Allow errors to appear
        updated_data = extract_visible_fields(driver)
        mutations = extract_mutation_observer_results(driver)
    else:
        updated_data = None  # No post-submission state available
        mutations = None

    driver.quit()
    return initial_data, updated_data, mutations

# Formats extracted fields and errors for model input.
def format_for_model(data):

    field_descriptions = [
        f"{field['label']} ({field['type']}): required={field['required']}, disabled={field['disabled']}, readonly={field['readonly']}"
        for field in data["fields"]
    ]
    error_messages = " | ".join(data["errors"]) if data["errors"] else "None"

    return "\n".join(field_descriptions) + f"\nErrors: {error_messages}"


# Define signatures for evaluation
#TODO maybe split into different signatures
class EvaluateInteractiveCues(dspy.Signature):
    """Check if form fields use appropriate cues (disabled, readonly, and required attributes) if they adopt those states."""
    html_snippet_before = dspy.InputField(desc="HTML before user interaction.")
    html_snippet_after = dspy.InputField(desc="HTML after user interaction (if available, else None)..")
    retrieved_guidelines = dspy.InputField(desc="Relevant WCAG guidelines and techniques for interactive cues.")
    mutations = dspy.InputField(desc="List of DOM mutations detected after submission, capturing error messages and attribute changes.")
    reasoning = dspy.OutputField(desc="Individual Explanation of whether the disabled, readonly, and required attributes were correctly used or not.")
    evaluation = dspy.OutputField(desc="A structrured list of all the elements evaluating, with Pass/Fail/Inapplicable, each field based on its interactive cues (considering raised error messages after interaction).")

# Generate a search query to find relevant WCAG guidelines and techniques for interactive cues.
class GenerateSearchQuery(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured HTML snippet representing form field attributes before and after user interaction. "
        "This includes relevant states such as `required`, `disabled`, `readonly`, and associated validation feedback."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant WCAG guidelines and best practices. "
        "The query should focus on accessibility issues related to form cues, ensuring proper use of `required`, `disabled`, "
        "and `readonly` attributes. It should also prioritize guidelines discussing error messages, validation feedback, "
        "and how assistive technologies interpret these attributes."
    ))


class InteractiveCuesEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=4, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_cues = dspy.ChainOfThought(EvaluateInteractiveCues)
        self.max_hops = max_hops

    def process_mutations(self, mutations):
        """Formats mutation records into a structured text summary."""
        if not mutations:
            return "No dynamic changes detected after form submission."

        summary = []
        for mutation in mutations:
            if mutation["type"] == "childList":
                added = ", ".join(mutation["addedNodes"]) if mutation["addedNodes"] else "None"
                removed = ", ".join(mutation["removedNodes"]) if mutation["removedNodes"] else "None"
                summary.append(f"Added Nodes: {added}, Removed Nodes: {removed}")
            elif mutation["type"] == "attributes":
                summary.append(f"Element Changed: {mutation['target']}, Attribute Modified: {mutation['attributeChanges']}")

        return "\n".join(summary)

    def forward(self, html_snippet_before, html_snippet_after, mutations, retrieved_guidelines=None):
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet_before).query
                queries.add(query)
                
                passages = self.retrieve(query).passages
                if not passages:
                    fallback_queries = [ #TODO review fallback queries
                        "Best practices for the 'required' attribute in forms under WCAG.",
                        "Ensuring error messages are programmatically linked to form inputs for accessibility.",
                        "How should the 'disabled' attribute be used to comply with accessibility standards?",
                        "Impact of dynamically changing form attributes on assistive technology.",
                        "What ARIA attributes can be used to enhance form cues and validation feedback?"
                    ]
                    for fallback in fallback_queries:
                        passages = self.retrieve(fallback).passages
                        print("used fallback")
                        if passages:
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                continue
        print("===== QUERIES =====")
        print(queries)

        
#TODO
        if html_snippet_after is None:
            reasoning = "No post-interaction state available. Evaluating only initial form attributes."
        else:
            reasoning = None

        mutation_summary = self.process_mutations(mutations)
        
        pred = self.evaluate_cues(
            html_snippet_before=html_snippet_before,
            html_snippet_after=html_snippet_after,
            mutations=mutation_summary,
            retrieved_guidelines=retrieved_guidelines
        )   

        # Use pred.reasoning only if html_snippet_after exists
        reasoning = pred.reasoning if html_snippet_after else reasoning

        return dspy.Prediction(
            retrieved_guidelines=retrieved_guidelines,
            evaluation=pred.evaluation,
            reasoning=reasoning,
            queries=list(queries)
        )




teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)


compiled_evaluator_submit = teleprompter.compile(
    InteractiveCuesEvaluator(), 
    teacher=InteractiveCuesEvaluator(passages_per_hop=2), 
    trainset=trainset
)
compiled_evaluator_no_submit = teleprompter.compile(
    InteractiveCuesEvaluator(), 
    teacher=InteractiveCuesEvaluator(passages_per_hop=2), 
    trainset=trainset_no_submit
)


html_before, html_after, mutations = extract_html_with_states(url)

#Output
if html_before:
    formatted_before = format_for_model(html_before)
    
    if html_after:
        formatted_after = format_for_model(html_after)
        #print("===== FORM BEFORE INTERACTION =====")
        #print(formatted_before)
        print("===== FORM AFTER INTERACTION =====")
        print(formatted_after)

        pred = compiled_evaluator_submit(formatted_before, formatted_after, mutations)
    else:
        print("Submit button missing or unclickable. Evaluating static form.")
        pred = compiled_evaluator_no_submit(formatted_before, None, None)  # Evaluate only "before" HTML

    
    print(f"===== EVALUATION =====\n{pred.evaluation}")
    print(f"===== RETRIEVED INFO =====\n{pred.retrieved_guidelines}")
    print(f"===== MUTATIONS OBSERVED =====\n{mutations}")

else:
    print("Failed to retrieve form data from the page.")
