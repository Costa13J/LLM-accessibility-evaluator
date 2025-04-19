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
from selenium.common.exceptions import JavascriptException
from bs4 import BeautifulSoup


import time

counter = 0  #global counter
clicked = False #global"clicked" boolean

url = "https://store.steampowered.com/join/?redir=app%2F2669320%2FEA_SPORTS_FC_25%2F%3Fsnr%3D1_4_4__129_1&snr=1_60_4__62"
#url = "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b" #Tem erros de cues e lança submit
#url = "https://www.continente.pt/loja-online/contactos/" #Tem erros de cues mas não lança submit
#url = "https://business.quora.com/contact-us/" #NAO FUNCIONA formulario so abre quando clickado um botao para abrir modal dialog
#url = "https://www.nba.com/account/sign-up"
#url = "https://www.gsmarena.com/tipus.php3"

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

def extract_form_html(driver):
    """Extracts raw HTML of all <form> elements as strings."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    forms = soup.find_all("form")
    if forms:
        html_list = [str(form) for form in forms]
        for idx, html in enumerate(html_list, 1):
            print(f"--- FORM #{idx} ---\n{html}\n")
        return html_list
    else:
        print("No forms found on the page.")
        return []


#Extracts the fields from the form, with their attributes and also errors 
def extract_fields(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fields = []

    #Just captures input related fields
    for input_field in soup.find_all(['input', 'textarea', 'select']):
        if input_field.get('type') in ['hidden', 'submit', 'button']:
            continue  # Ignore non-user input fields

        # Find the associated label, can be in 'for' attribute
        label = None
        if input_field.has_attr("id"):
            label = soup.find("label", {"for": input_field["id"]})  # Look for associated label
        if not label:
            label = input_field.find_parent("label")  # Look for wrapped label

        # Extract error messages from elements associated with the field
        error_messages = []
        
        # Check aria-describedby for error messages
        if input_field.has_attr("aria-describedby"):
            error_refs = input_field["aria-describedby"].split()
            for ref in error_refs:
                error_element = soup.find(id=ref)
                if error_element:
                    error_messages.append(error_element.text.strip())

        # Extract error messages from elements with 'error' class near the input
        for error_element in input_field.find_next_siblings():
            if "error" in error_element.get("class", []):
                error_messages.append(error_element.text.strip())

        # Extract additional error-related attributes
        if input_field.has_attr("aria-invalid") and input_field["aria-invalid"] == "true":
            error_messages.append("Invalid input")

        # Special handling for select elements (extract selected option)
        value = input_field.get("value", "")
        if input_field.name == "select":
            selected_option = input_field.find("option", selected=True)
            value = selected_option.text.strip() if selected_option else ""

        # Special handling for checkboxes and radio buttons
        if input_field.get("type") in ["checkbox", "radio"]:
            value = "checked" if input_field.has_attr("checked") else "unchecked"

        field_info = {
            "label": label.text.strip() if label else "No Label",
            "name": input_field.get("name", ""),
            "id": input_field.get("id", ""),
            "type": input_field.get("type", ""),
            "value": value,
            "required": "yes" if input_field.has_attr("required") else "no required attribute",
            "disabled": "yes" if input_field.has_attr("disabled") else "no disabled attribute",
            "readonly": "yes" if input_field.has_attr("readonly") else "no read-only attribute",
            "errors": list(set(error_messages))  # Remove duplicates
        }
        fields.append(field_info)

    # Extract global error messages
    errors = [e.text.strip() for e in soup.select(".error") if e.get('style') != 'display:none;']

    # Collect non-empty field-specific errors
    field_errors = [msg for f in fields for msg in f["errors"] if msg]

    print("===== FIELDS PASSED TO LM =====")
    print(fields + list(set(errors + field_errors)))

    return {"fields": fields, "errors": list(set(errors + field_errors))}  # Remove duplicate errors


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
            clicked = True
            return "clicked"

        except Exception as e:
            print(f"Error clicking submit button: {e}")
            print("Trying JavaScript click...")
    
            #TODO should be removed because to fall into this click can mean button is disabled or not available
            try:
                driver.execute_script("arguments[0].click();", submit_button)
                print("JavaScript click executed successfully!")
                clicked = True
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
    raw_mutations = driver.execute_script("return window.mutationRecords || []")

    structured_mutations = []
    for m in raw_mutations:
        structured_mutations.append({
            "type": m.get("type"),
            "target": m.get("target", ""),
            "targetTag": m.get("targetTag", ""),
            "targetId": m.get("targetId", ""),
            "targetClass": m.get("targetClass", ""),
            "attributeChanged": m.get("attributeChanged", ""),
            "newValue": m.get("newValue", ""),
            "validationFlag": m.get("validationFlag", False),
            "addedNodes": m.get("addedNodes", []),
            "removedNodes": m.get("removedNodes", []),
            "possibleErrorMessages": m.get("possibleErrorMessages", []),
            "timestamp": m.get("timestamp", None),
        })

    return structured_mutations

# Loads a webpage, extracts form fields before interaction.
def extract_html_with_states(url):

    driver = setup_webdriver()
    driver.get(url)

    #initial_data = extract_form_html(driver) #Use this for full form
    initial_data = extract_fields(driver) #Use this for fields

    action_result = find_and_click_submit_button(driver)

    if action_result == "clicked":
        time.sleep(2)  # Allow errors to appear
        mutations = extract_mutation_observer_results(driver)
    else:
        mutations = None

    driver.quit()
    return initial_data, mutations

# Formats extracted fields and errors for model input.
def format_for_model(data):

    field_descriptions = [
        f"{field['label']} ({field['type']}): required={field['required']}, disabled={field['disabled']}, readonly={field['readonly']}"
        for field in data["fields"]
    ]
    error_messages = " | ".join(data["errors"]) if data["errors"] else "None"

    return "\n".join(field_descriptions) + f"\nErrors: {error_messages}"


# Signature for evaluation
class EvaluateInteractiveCues(dspy.Signature):
    """Check if form fields use appropriate required attributes if they adopt that state."""
    html_snippet_before = dspy.InputField(desc="Form HTML snippet before user interaction.")
    mutations = dspy.InputField(desc="List of DOM mutations detected after submission of the form when left empty, capturing error messages and attribute changes.")
    retrieved_guidelines = dspy.InputField(desc="Relevant examples and best practices for the use of required attributes in form fields.")
    evaluation = dspy.OutputField(desc="An individual evaluation of each field based on their use of the required attribute, assigning Pass/Fail/Inapplicable to each of them with a brief explanation on the accessibility evaluation performed.")
    format = dspy.OutputField(desc="""Use this exact structure for each evaluated field without the information in brackets:
        -Identification(label or name of the field): <extracted info> 
        -Evaluation("pass" or "fail" or "inapplicable"): <result>
        -Reasoning(explanation of the evaluation result): <reason>
        Ensure this format is followed exactly with no additional explanation.""")

# Generate a search query to find relevant WCAG guidelines and techniques for interactive cues.
class GenerateSearchQuery(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured HTML snippet representing form field attributes before and after user interaction. "
        "This includes relevant states such as `required`, `disabled`, `readonly`, and associated validation feedback."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant examples from wcag and best practices. "
        "The query should focus on accessibility issues related to form cues, ensuring proper use of `required` attributes."
    ))


class InteractiveCuesEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=3, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_cues = dspy.ChainOfThought(EvaluateInteractiveCues)
        self.max_hops = max_hops

    #Formats mutation records into a structured text summary
    from collections import Counter

    def process_mutations(self, mutations):
        if not mutations:
            return "No dynamic changes detected after form interaction."

        summary = []

        for m in mutations:
            if not isinstance(m, dict):
                summary.append(f"[Warning] Unexpected mutation format: {m}")
                continue  # skip invalid mutation entries

            target_tag = m.get('targetTag', '?')
            target_id = m.get('targetId', '')
            target = f"<{target_tag}>#{target_id}" if target_id else f"<{target_tag}>"

            field_label = m.get("fieldLabel", "")
            field_name = m.get("fieldName", "")
            field_info = f" (Field: '{field_label}' | name='{field_name}')" if field_label or field_name else ""


            if m.get("type") == "attributes":
                attr = m.get("attributeChanged")
                val = m.get("newValue")
                note = "Validation-related attribute changed." if m.get("validationFlag") else ""

                if attr in ["style", "class"] and m.get("possibleErrorMessages"):
                    for msg in m["possibleErrorMessages"]:
                        summary.append(f"[Visible Error Message Revealed] {msg}{field_info}")
                else:
                    summary.append(f"[Attribute Change] {target} → '{attr}' updated to '{val}'{field_info}. {note}".strip())

            elif m.get("type") == "childList":
                added = m.get("addedNodes", [])
                removed = m.get("removedNodes", [])
                error_msgs = m.get("possibleErrorMessages", [])

                for msg in error_msgs:
                    summary.append(f"[Error Message Added] {msg}{field_info}")

                for node_html in added:
                    snippet = node_html.strip().replace("\n", " ")[:200]
                    summary.append(f"[DOM Node Added] Snippet: {snippet}...{field_info}")

                for node_html in removed:
                    snippet = node_html.strip().replace("\n", " ")[:200]
                    summary.append(f"[DOM Node Removed] Snippet: {snippet}...{field_info}")

        cleaned_summary = deduplicate(summary)
        return "\n".join(cleaned_summary)



    def forward(self, html_snippet_before, mutations, retrieved_guidelines=None):
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
                        "What ARIA attributes can be used to enhance form cues?"
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
        print("===== QUERY =====")
        print(queries)

        mutation_summary = self.process_mutations(mutations) if mutations else "No form interaction or dynamic changes to analyze."

        pred = self.evaluate_cues(
            html_snippet_before=html_snippet_before,
            mutations=mutation_summary,
            retrieved_guidelines=retrieved_guidelines
        )   

        return dspy.Prediction(
            retrieved_guidelines=retrieved_guidelines,
            evaluation=pred.evaluation,
            mutation_summary=mutation_summary,
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


html_before, mutations = extract_html_with_states(url)

#Output
if html_before:
    formatted_html = format_for_model(html_before) #Use this for fields
    #formatted_html = html_before #Use this for full html

    if clicked or mutations:
        print("Evaluating dynamic form interaction.")
        pred = compiled_evaluator_submit(formatted_html, mutations)
    else:
        print("Submit button unclickable. Evaluating static form.")
        pred = compiled_evaluator_no_submit(formatted_html, None)  # Evaluate only HTML

    
    print(f"===== EVALUATION =====\n{pred.evaluation}")
    #print(f"===== RETRIEVED INFO =====\n{pred.retrieved_guidelines}")
    #print(f"===== MUTATIONS OBSERVED =====\n{pred.mutation_summary}")

else:
    print("Failed to retrieve form data from the page.")
