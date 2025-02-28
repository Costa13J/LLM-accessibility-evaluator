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

# Set up the API key
os.environ["MISTRAL_API_KEY"] = "vZYsFYM6r2E9JWyD3GYPdLfR34kI2EcO"

# Configure DSPy with the model and retriever
mini = dspy.LM('mistral/mistral-large-latest')
rm = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(lm=mini, rm=rm)

def setup_webdriver():
    """Configures and launches a headless Chrome browser."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without UI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())  
    return webdriver.Chrome(service=service, options=chrome_options)


def extract_visible_fields(driver):
    """Extracts visible input fields, labels, and error messages from the form."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fields = []

    for input_field in soup.find_all(['input', 'textarea', 'select']):
        if input_field.get('type') in ['hidden', 'submit', 'button']:
            continue  # Ignore non-user input fields

        label = input_field.find_parent('label')
        field_info = {
            "label": label.text.strip() if label else "No Label",
            "name": input_field.get("name", ""),
            "id": input_field.get("id", ""),
            "type": input_field.get("type", ""),
            "value": input_field.get("value", ""),
            "required": "required" if input_field.has_attr("required") else "not required",
            "disabled": "disabled" if input_field.has_attr("disabled") else "not disabled",
            "readonly": "readonly" if input_field.has_attr("readonly") else "not readonly",
        }
        fields.append(field_info)

    # Extract only the error messages that are visible after submission
    errors = [e.text.strip() for e in soup.select(".error") if e.get('style') != 'display:none;']

    return {"fields": fields, "errors": errors}



def extract_html_with_states(url):
    """Loads a webpage, extracts form fields before and after interaction."""
    driver = setup_webdriver()
    driver.get(url)

    # Extract initial state of relevant fields
    initial_data = extract_visible_fields(driver)

    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "MainContent_FormContent_MainControl_RightSide_SubmitButton"))
        )
        ActionChains(driver).move_to_element(submit_button).click().perform()
        wait_for_error_message(driver)
    except Exception as e:
        print(f"Error interacting with form: {e}")

    # Extract updated state after submission
    updated_data = extract_visible_fields(driver)

    driver.quit()
    return initial_data, updated_data


def wait_for_error_message(driver, timeout=10):
    error_selectors = [
        "label[data-error]",  # Your example
        ".error-message",  # Standard error class
        "span.error",  # Some sites use this
        "div.error",  # Some sites use this
        "p.error",  # Some sites use this
        "input[aria-invalid='true']",  # Accessibility-friendly errors
    ]

    condition = EC.presence_of_element_located
    wait = WebDriverWait(driver, timeout)

    for selector in error_selectors:
        try:
            return wait.until(condition((By.CSS_SELECTOR, selector)))
        except:
            continue  # Try next selector if this one fails

    raise TimeoutException("No error message found within timeout")

def format_for_model(data):
    """Formats extracted fields and errors for model input."""
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
    html_snippet_after = dspy.InputField(desc="HTML after user interaction.")
    retrieved_guidelines = dspy.InputField(desc="Relevant WCAG guidelines and techniques for interactive cues.")
    reasoning = dspy.OutputField(desc="Individual Explanation of whether the attributes were correctly used.")
    evaluation = dspy.OutputField(desc="A structrured list of the elements with Pass/Fail/Inapplicable for each field based on its state before and after interaction.")

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
                    fallback_queries = [
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

        pred = self.evaluate_cues(
            html_snippet_before=html_snippet_before,
            html_snippet_after=html_snippet_after,
            retrieved_guidelines=retrieved_guidelines
        )

        if not pred or not getattr(pred, 'evaluation', None) or not getattr(pred, 'reasoning', None):
            return dspy.Prediction(retrieved_guidelines=retrieved_guidelines, evaluation="Error: No Output", reasoning="LLM did not generate a valid response.")

        return dspy.Prediction(retrieved_guidelines=retrieved_guidelines, evaluation=pred.evaluation, queries=list(queries))

trainset = [
    dspy.Example(
        html_snippet_before="""<label for='username'>*User name:</label><input type='text' name='username' id='username'>""",
        html_snippet_after="""<label for='username'>*User name:</label><input type='text' name='username' id='username' required>""",
        retrieved_guidelines="Required fields should have the 'required' attribute before and after interaction.",
        evaluation="Fail: Required field lacks 'required' attribute initially but gains it dynamically. It should be explicitly set in HTML."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    dspy.Example(
        html_snippet_before="""<input type='text' name='email' id='email'>""",
        html_snippet_after="""<input type='text' name='email' id='email' disabled>""",
        retrieved_guidelines="Disabled fields should be indicated using the 'disabled' attribute in static HTML.",
        evaluation="Fail: Field only becomes disabled after interaction. It should be predefined in HTML."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),

    dspy.Example(
        html_snippet_before="""<input type='text' name='email' id='email' readonly>""",
        html_snippet_after="""<input type='text' name='email' id='email' readonly>""",
        retrieved_guidelines="Readonly attributes should not change after interaction.",
        evaluation="Pass: 'readonly' attribute remains consistent before and after interaction."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines"),
]

teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
compiled_evaluator = teleprompter.compile(InteractiveCuesEvaluator(), teacher=InteractiveCuesEvaluator(passages_per_hop=2), trainset=trainset)

url = "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b"
html_before, html_after = extract_html_with_states(url)

if html_before and html_after:
    formatted_before = format_for_model(html_before)
    formatted_after = format_for_model(html_after)
    
    print("===== FORM BEFORE INTERACTION =====")
    print(formatted_before)
    print("===== FORM AFTER INTERACTION =====")
    print(formatted_after)

    pred = compiled_evaluator(formatted_before, formatted_after)
    print(f"Accessibility Evaluation:\n{pred.evaluation}")
    print(f"Retrieved Information:\n{pred.retrieved_guidelines}")
else:
    print("Failed to retrieve form data from the page.")
