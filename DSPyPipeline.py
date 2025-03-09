import dspy
from dsp.utils import deduplicate
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

import time
counter = 0  # Initialize the global counter

url = "https://www.continente.pt/loja-online/contactos/"

# Set up the API key
os.environ["MISTRAL_API_KEY"] = "vZYsFYM6r2E9JWyD3GYPdLfR34kI2EcO"

# Configure DSPy with the model and retriever
mini = dspy.LM('mistral/mistral-large-latest')
rm = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(lm=mini, rm=rm)

def setup_webdriver():
    """Configures and launches a headless Chrome browser."""
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run without UI
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
            "required": "required" if input_field.has_attr("required") else "not required",
            "disabled": "disabled" if input_field.has_attr("disabled") else "not disabled",
            "readonly": "readonly" if input_field.has_attr("readonly") else "not readonly",
            "errors": error_messages
        }
        fields.append(field_info)
        
    # Extract error messages from elements with class 'error' that are visibly rendered
    errors = [e.text.strip() for e in soup.select(".error") if e.get('style') != 'display:none;']
    
    # Also collect non-empty error messages from the extracted fields
    field_errors = [msg for f in fields for msg in f["errors"] if msg] #TODO verificar se não e melhor so este

    return {"fields": fields, "errors": errors + field_errors}

def extract_buttons_for_llm(driver):
    """Extracts all buttons and any element with an onclick event to pass to the LLM."""
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
    predicted_button_id = dspy.OutputField(desc="The string of the ID of the button that is the most likely submit button of the form (or 'None' if no ID exists).")

identify_submit_button = dspy.ChainOfThought(IdentifySubmitButton)

# Uses an LLM to predict which button is the submit button.
def get_submit_button_id_from_llm(buttons):

    response = identify_submit_button(buttons_info=str(buttons))
    return response.predicted_button_id if response.predicted_button_id != "None" else None

# Finds and clicks the submit button using an LLM to identify it.
def find_and_click_submit_button(driver):

    try:
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
                EC.element_to_be_clickable((By.ID, submit_button_id))
            )
            submit_button.click()
            print("Submit button clicked!")
            return "clicked"

        except Exception as e:
            print(f"Error clicking submit button: {e}")
            print("Trying JavaScript click...")
    
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

# Loads a webpage, extracts form fields before and after interaction.
def extract_html_with_states(url):

    driver = setup_webdriver()
    driver.get(url)

    # Extract initial state of relevant fields
    initial_data = extract_visible_fields(driver)

    action_result = find_and_click_submit_button(driver)

    if action_result == "clicked":
        time.sleep(2)  # Allow errors to appear
        updated_data = extract_visible_fields(driver)
    else:
        updated_data = None  # No post-submission state available

    driver.quit()
    return initial_data, updated_data

# Formats extracted fields and errors for model input.
def format_for_model(data):

    field_descriptions = [
        f"{field['label']} ({field['type']}): required={field['required']}, disabled={field['disabled']}, readonly={field['readonly']}"
        for field in data["fields"]
    ]
    error_messages = " | ".join(data["errors"]) if data["errors"] else "None"

    return "\n".join(field_descriptions) + f"\nErrors: {error_messages}"


# Define signatures for evaluation
class EvaluateInteractiveCues(dspy.Signature):
    """Check if form fields use appropriate cues (disabled, readonly, and required attributes) if they adopt those states."""
    html_snippet_before = dspy.InputField(desc="HTML before user interaction.")
    html_snippet_after = dspy.InputField(desc="HTML after user interaction (if available, else None)..")
    retrieved_guidelines = dspy.InputField(desc="Relevant WCAG guidelines and techniques for interactive cues.")
    reasoning = dspy.OutputField(desc="Individual Explanation of whether the disabled, readonly, and required attributes were correctly used or not.")
    evaluation = dspy.OutputField(desc="A structrured list of all the elements evaluating, with Pass/Fail/Inapplicable, each field based on its interactive cues (considering raised error messages after interaction).")

class GenerateSearchQuery(dspy.Signature):
    """Generate a search query to find relevant WCAG guidelines and techniques for interactive cues."""
    html_snippet = dspy.InputField(desc="Form field attributes before and after user interaction.")
    query = dspy.OutputField(desc="Search query focusing on accessibility best practices for required, disabled, and readonly attributes.")

class InteractiveCuesEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=1, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_cues = dspy.ChainOfThought(EvaluateInteractiveCues)
        self.max_hops = max_hops

    def forward(self, html_snippet_before, html_snippet_after, retrieved_guidelines=None):
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet_before).query
                queries.add(query)
                
                passages = self.retrieve(query).passages
                if not passages:
                    fallback_queries = [ #TODO review fallback queries
                        "WCAG best practices for required, disabled, and readonly attributes",
                        "Ensuring error messages are programmatically linked to input fields",
                        "Improving accessibility of dynamic form validation messages"
                    ]
                    for fallback in fallback_queries:
                        passages = self.retrieve(fallback).passages
                        if passages:
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                continue

#TODO
        if html_snippet_after is None:
            reasoning = "No post-interaction state available. Evaluating only initial form attributes."
        else:
            reasoning = None
        
        pred = self.evaluate_cues(
            html_snippet_before=html_snippet_before,
            html_snippet_after=html_snippet_after,
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


#TODO Falta testar inputs por causa do read only e disabled e há casos aqui para outros testes diferentes
trainset = [
    # Error message appears when required field is left empty (valid behavior).
    dspy.Example(
        html_snippet_before="""<label for='password'>*Password:</label>
                           <input type='password' name='password' id='password' required>""",
        html_snippet_after="""<label for='password'>*Password:</label>
                          <input type='password' name='password' id='password' required>
                          <span class='error' id='password-error'>This field is required.</span>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        evaluation="Pass: The form correctly displays an error message when the required field is empty."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    # Asterisk.
    dspy.Example(
        html_snippet_before="""<label for='password'>*Password:</label>
                           <input type='password' name='password' id='password'>""",
        html_snippet_after=None,
        retrieved_guidelines="Fields with '*' usually means the field is required",
        evaluation="Fail: The Field has an asterisk that symbolizes its requirement, but has no required attribute ."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    # Error message appears but field not marked as required (incorrect behavior).
    dspy.Example(
        html_snippet_before="""<label for='password'>Password:</label>
                           <input type='password' name='password' id='password'>""",
        html_snippet_after="""<label for='password'>Password:</label>
                          <input type='password' name='password' id='password'>
                          <span class='error' id='password-error'>This field is required.</span>""",
        retrieved_guidelines="If an input field raises a required error message, it must provide the 'required' or aria-required='true' cue.",
        evaluation="Fail: The field raises an error because it is required but it has no required."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    # No error message appears for a required field (incorrect behavior).
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='text' name='email' id='email' required>""",
        html_snippet_after="""<label for='email'>*Email:</label>
                          <input type='text' name='email' id='email' required>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        evaluation="Fail: The required field does not display an error message when left empty."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    

    # Required field is marked with 'aria-required' but lacks an error message after submission.
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone:</label>
                           <input type='tel' name='phone' id='phone' aria-required='true'>""",
        html_snippet_after="""<label for='phone'>*Phone:</label>
                          <input type='tel' name='phone' id='phone' aria-required='true'>""",
        retrieved_guidelines="ARIA attributes like 'aria-required' should be accompanied by proper error messages.",
        evaluation="Fail: The form does not display an error message despite 'aria-required' being set."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    dspy.Example(
        html_snippet_before="""<label for='age'>*Age:</label>
                           <input type='number' name='age' id='age' disabled>""",
        html_snippet_after="""<label for='age'>*Age:</label>
                          <input type='number' name='age' id='age' disabled>""",
        retrieved_guidelines="Disabled fields should not trigger required field error messages.",
        evaluation="Pass: The field is disabled and does not incorrectly show an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    dspy.Example(
        html_snippet_before="""<label for='country'>*Country:</label>
                           <input type='text' name='country' id='country' value='USA' readonly>""",
        html_snippet_after="""<label for='country'>*Country:</label>
                          <input type='text' name='country' id='country' value='USA' readonly>""",
        retrieved_guidelines="Readonly fields should not trigger required field error messages.",
        evaluation="Pass: The field is readonly and does not incorrectly show an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),


]

teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
compiled_evaluator = teleprompter.compile(InteractiveCuesEvaluator(), teacher=InteractiveCuesEvaluator(passages_per_hop=2), trainset=trainset)


html_before, html_after = extract_html_with_states(url)

if html_before:
    formatted_before = format_for_model(html_before)
    
    if html_after:
        formatted_after = format_for_model(html_after)
        #print("===== FORM BEFORE INTERACTION =====")
        #print(formatted_before)
        #print("===== FORM AFTER INTERACTION =====")
        #print(formatted_after)

        pred = compiled_evaluator(formatted_before, formatted_after)
    else:
        #print("===== FORM WITHOUT INTERACTION =====")
        #print(formatted_before)
        #print("Submit button missing or unclickable. Evaluating static form.")

        pred = compiled_evaluator(formatted_before, None)  # Evaluate only "before" HTML

    print(f"Accessibility Evaluation:\n{pred.evaluation}")
    print(f"Retrieved Information:\n{pred.retrieved_guidelines}")

else:
    print("Failed to retrieve form data from the page.")
