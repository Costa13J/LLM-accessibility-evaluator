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
from collections import Counter
import re
import logging

logging.getLogger("chromadb").setLevel(logging.ERROR)
counter = 0  #global counter
clicked = False #global"clicked" boolean

#Lança submit
#url = "https://store.steampowered.com/join/?redir=app%2F2669320%2FEA_SPORTS_FC_25%2F%3Fsnr%3D1_4_4__129_1&snr=1_60_4__62"
#url = "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b" #Tem erros de cues e lança submit
#url = "https://www.nba.com/account/sign-up" #Lança submit e tem erros
#url = "https://appserver2.ctt.pt/feapl_2/app/open/stationSearch/stationSearch.jspx?lang=def"
#url = "https://www.amazon.com/ap/register?openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fap%2Fcnep%3Fie%3DUTF8%26orig_return_to%3Dhttps%253A%252F%252Fwww.amazon.com%252Fyour-account%26openid.assoc_handle%3Dusflex%26pageId%3Dusflex&prevRID=05AYRRNGN9PBHQCYWN7S&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=usflex&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
#url = "https://www.ilovepdf.com/contact"
#url = "https://support.fandango.com/fandangosupport/s/contactsupport"


# NÃO lança submit
#url = "https://www.continente.pt/loja-online/contactos/" #Tem erros de cues 
#url = "https://www.continente.pt/checkout/entrega/" 
#url = "https://www.ipma.pt/pt/siteinfo/contactar.jsp"
#url = "https://suporte.decathlon.pt/hc/pt/requests/new?ticket_form_id=4421041894417" #REFRESH DA PAGINA AO SUBMETER
#url = "https://appserver2.ctt.pt/femgu/app/open/enroll/showUserEnrollAction.jspx?lang=def&redirect=https://www.ctt.pt/ajuda/particulares/receber/gerir-correio-e-encomendas/reter-tudo-que-recebo-numa-loja-ctt#fndtn-panel2-2" #BOTAO BLOQUEADO SE NAO SELCIONAR UMA CHECKBOX ANTES
#url = "https://www.ctt.pt/feapl_2/app/open/postalCodeSearch/postalCodeSearch.jspx?lang=def#fndtn-postalCodeSearchPanel"
#url = "https://business.quora.com/contact-us/"
#url = "https://cookpad.com/us/premium_signup/unified_subscription_purchases/new?web_subscription_plan_id=47" #Resultados estranhos para a pagina que é
#url = "https://cam.merriam-webster.com/registration?utm_source=mw&utm_medium=global-nav-join&utm_campaign=evergreen&partnerCode=default_partner&_gl=1*s07wn2*_ga*NjcwNzY4MzE2LjE3MzkwMzc0NzA.*_ga_821K16B669*MTczOTAzNzQ3MC4xLjAuMTczOTAzNzQ3MC4wLjAuMA..&offerCode=mwu-monthly-free-trial"
url = "https://www.medicalnewstoday.com/articles/323586#bmi-calculators"
#url = "https://www.gsmarena.com/tipus.php3"
#url = "https://www.istockphoto.com/customer-support"
#url = "https://www.infinite.media/bible-gateway/"


#Não funciona
#url = "https://www.net-empregos.com/" #NO labels just placeholders  DA ERRO A CORRER NORMAL TODO PERCEBER PQQ DA ERRO
#url = "https://www.cricbuzz.com/info/contact"
#url = "https://doctor.webmd.com/learnmore/profile"
#url = "https://www.accuweather.com/en/contact"
#url = "https://business.trustpilot.com/signup?cta=free-signup_header_home"
#url = "https://support.discord.com/hc/en-us/requests/new?ticket_form_id=360006586013"




#Preciso estar logged - nao funciona
#url = "https://loja.meo.pt/compra?modalidade-compra=pronto-pagamento" 
#url = "https://www.decathlon.pt/p-r/calcado-de-caminhada-merrell-crosslander-mulher/_/R-p-X8761333?mc=8761333&offer=8761333" 
#url = "https://www.decathlon.pt/checkout/shipping" 
#url = "https://www.amazon.com/checkout/p/p-106-8712704-0157058/address?pipelineType=Chewbacca&referrer=address" 
#url = "https://contribute.imdb.com/updates/edit?update=title&ref_=czone_ra_new_title"
#url = "https://www.etsy.com/your/shops/me/onboarding/listing-editor/create#about"
#url = "https://genius.com/new"

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


#Extracts the fields from the form, with their attributes and also errors  TODO doesnt exclude visibility:hidden as of now
def extract_fields(driver):

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    fields = []

    for input_field in soup.find_all(['input', 'textarea', 'select']):
        # Skip non-user inputs
        if input_field.get('type') in ['hidden', 'submit', 'button']:
            continue

        # Skip inline styles that hide the field
        style = input_field.get("style", "").lower()
        if any(s in style for s in ["display: none", "display:none", "visibility:hidden", "visibility: hidden"]):
            continue

        # Skip fields inside visually hidden containers
        hidden_parent = input_field.find_parent(
            style=lambda s: s and any(x in s.lower() for x in ["display: none", "visibility: hidden"])
        )
        if hidden_parent:
            continue

        # === Label Extraction ===
        label_text = None

        # 1. label[for=id]
        if input_field.has_attr("id"):
            label_elem = soup.find("label", {"for": input_field["id"]})
            if label_elem:
                label_text = label_elem.text.strip()

        # 2. <label> wrapper
        if not label_text:
            wrapping_label = input_field.find_parent("label")
            if wrapping_label:
                label_text = wrapping_label.text.strip()

        # 3. aria-labelledby
        if not label_text and input_field.has_attr("aria-labelledby"):
            ids = input_field["aria-labelledby"].split()
            parts = []
            for ref_id in ids:
                label_ref = soup.find(id=ref_id)
                if label_ref:
                    parts.append(label_ref.text.strip())
            if parts:
                label_text = " ".join(parts)

        # 4. placeholder fallback
        if not label_text and input_field.has_attr("placeholder"):
            label_text = f"[placeholder] {input_field['placeholder'].strip()}"

        if not label_text:
            label_text = "No Label"

        # === Value Extraction ===
        value = input_field.get("value", "")
        if input_field.name == "select":
            selected_option = input_field.find("option", selected=True)
            value = selected_option.text.strip() if selected_option else ""

        if input_field.get("type") in ["checkbox", "radio"]:
            value = "checked" if input_field.has_attr("checked") else "unchecked"

        # === Field Metadata ===
        field_info = {
            "label": label_text,
            "name": input_field.get("name", ""),
            "id": input_field.get("id", ""),
            "type": input_field.get("type", input_field.name),  # fallback to tag
            "value": value,
            "required": "yes" if input_field.has_attr("required") else "no required attribute",
            "disabled": "yes" if input_field.has_attr("disabled") else "no disabled attribute",
            "readonly": "yes" if input_field.has_attr("readonly") else "no read-only attribute",
            "autocomplete": input_field.get("autocomplete", "no autocomplete"),
            "inputmode": input_field.get("inputmode", "no inputmode")
        }

        fields.append(field_info)

    print("===== FIELDS PASSED TO LM =====")
    print(fields)

    return {"fields": fields}



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
    predicted_button_id = dspy.OutputField(desc="The exact XPATH of the button that is the most likely submit or advance button of the form, only one (or 'None' if no such button exists).")

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
    global clicked

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

# Formats extracted fields for model input.
def format_for_model(data):
    field_descriptions = [
        f"{field['label']} ({field['type']}): "
        f"required={field['required']}, disabled={field['disabled']}, readonly={field['readonly']}, "
        f"autocomplete={field['autocomplete']}"
        for field in data["fields"]
    ]

    return "\n".join(field_descriptions)


def save_to_json(prediction, url, submit_clicked, filename="results.json"):
    field_blocks = re.split(r"-Identification:", prediction.format)[1:]  # Skip empty first part
    structured_fields = []

    for block in field_blocks:
        try:
            identification_match = re.search(r"^(.*?)\n", block.strip())
            evaluation_match = re.search(r"-Evaluation:\s*(.*?)\n", block)
            reasoning_match = re.search(r"-Reasoning:\s*(.*)", block, re.DOTALL)

            field_info = {
                "identification": identification_match.group(1).strip() if identification_match else "Unknown",
                "evaluation": evaluation_match.group(1).strip() if evaluation_match else "Unknown",
                "reasoning": reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
            }

            structured_fields.append(field_info)
        except Exception as e:
            print(f"Error parsing field block: {e}\nBlock content:\n{block}")

    result_entry = {
        "url": url,
        "submit_clicked": submit_clicked,
        "fields": structured_fields
    }

    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append(result_entry)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        print(f"Structured results saved to {filename}")
    except Exception as e:
        print(f"Error saving structured results: {e}")


# Signature for evaluation
class EvaluateInteractiveCues(dspy.Signature):
    """Check if form fields use appropriate required attributes if they adopt that state."""
    #html_snippet_before = dspy.InputField(desc="Form HTML snippet before user interaction.") #Use this for full form
    html_snippet_before = dspy.InputField(desc="A list of the fields from the form to evaluate before user interaction.") #Use this for fields
    mutations = dspy.InputField(desc="List of DOM mutations detected after submission of the form when left empty, capturing error messages and attribute changes.")
    retrieved_guidelines = dspy.InputField(desc="Relevant examples and best practices for the use of required attributes in form fields.")
    identification = dspy.OutputField(desc="For each field, extract and list its identification (preferably its label or name attribute) from the HTML snippet.")
    evaluation = dspy.OutputField(desc="""For each field, assess whether it correctly uses the 'required' attribute when appropriate based on the field’s behavior after submission (using the provided DOM mutations and best practice guidelines).
Assign a simple result: 'pass', 'fail', or 'inapplicable' for each field.""")
    reasoning = dspy.OutputField(desc="""For each field, explain briefly why the evaluation was 'pass', 'fail', or 'inapplicable'. 
Focus the reasoning on accessibility concerns related to form validation cues (such as missing required attributes, inappropriate required attributes, or use of other mechanisms instead of HTML5 native required attribute).""")
    format = dspy.OutputField(desc="""After filling Identification, Evaluation, and Reasoning individually for each field, assemble the final output with this structure for each field:
-Identification(label or name of the field): <identification> 
-Evaluation("pass" or "fail" or "inapplicable"): <evaluation>
-Reasoning(explanation of the evaluation result): <reasoning>
    Ensure this exact structure is followed without any additional commentary.""")

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

            warning_notes = []

            if m.get("type") == "attributes":
                attr = m.get("attributeChanged")
                val = m.get("newValue")
                note = "Validation-related attribute changed." if m.get("validationFlag") else ""

                if attr in ["style", "class"] and not m.get("validationFlag"):
                    warning_notes.append("Style change not accompanied by semantic cues (e.g., ARIA).")

                if attr in ["aria-invalid", "aria-describedby"]:
                    note = "Semantic attribute updated."

                for msg in m.get("possibleErrorMessages", []):
                    summary.append(f"[Message Revealed] {msg}{field_info}")
                    if not field_label and not field_name:
                        warning_notes.append("Unlinked message: not programmatically associated with any input field.")

                summary.append(f"[Attribute Change] {target} → '{attr}' updated to '{val}'{field_info}. {note}".strip())
                if warning_notes:
                    for w in warning_notes:
                        summary.append(f"[Warning] {w}")

            elif m.get("type") == "childList":
                added = m.get("addedNodes", [])
                removed = m.get("removedNodes", [])
                messages = m.get("possibleErrorMessages", [])

                for msg in messages:
                    summary.append(f"[Visible Message] {msg}{field_info}")
                    if not field_label and not field_name:
                        summary.append(f"[Warning] Message not programmatically linked to any input field.")

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
            identification=pred.identification,
            reasoning=pred.reasoning,
            format=pred.format,
            mutation_summary=mutation_summary,
            queries=list(queries)
        )

teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
html_before, mutations = extract_html_with_states(url)

#Output
if html_before:
    formatted_html = format_for_model(html_before) #Use this for fields
    #formatted_html = html_before #Use this for full html

    if clicked or mutations:
        print("Evaluating dynamic form interaction.")
        compiled_evaluator_submit = teleprompter.compile(
            InteractiveCuesEvaluator(), 
            teacher=InteractiveCuesEvaluator(passages_per_hop=2), 
            trainset=trainset
        )
        pred = compiled_evaluator_submit(formatted_html, mutations)
        save_to_json(pred, url, submit_clicked=True)

    else:
        print("Submit button unclickable. Evaluating static form.")
        compiled_evaluator_no_submit = teleprompter.compile(
            InteractiveCuesEvaluator(), 
            teacher=InteractiveCuesEvaluator(passages_per_hop=2), 
            trainset=trainset_no_submit
        )
        pred = compiled_evaluator_no_submit(formatted_html, None)  # Evaluate only HTML
        save_to_json(pred, url, submit_clicked=False)

    
    #print(f"===== EVALUATION =====\n{pred.evaluation}")
    #print(f"===== RETRIEVED INFO =====\n{pred.retrieved_guidelines}")
    #print(f"===== MUTATIONS OBSERVED =====\n{pred.mutation_summary}")
    print(f"===== EVALUATION ===== {url} =====\n{pred.format}")

else:
    print("Failed to retrieve form data from the page.")
