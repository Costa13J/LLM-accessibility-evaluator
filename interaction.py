import re
import dspy
from extractors import extract_buttons_for_llm
from constants import fallback_invalid_input
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# LLM call to identify the submit button 
class IdentifySubmitButton(dspy.Signature):

    buttons_info = dspy.InputField(desc="List of button elements on the page, including tag, text, title, id, name, type, value and onclick.")
    predicted_button_id = dspy.OutputField(desc="The button_id (e.g., 'button_3') of the button that is most likely the submit or advance button for the form. Return only one Xpath (or 'None' if no such button exists).")

identify_submit_button = dspy.ChainOfThought(IdentifySubmitButton)

def get_submit_button_id_from_llm(buttons):

    response = identify_submit_button(buttons_info=str(buttons))
    #print("====BUTTON XPATH GIVEN BY THE LLM====") # debug print
    #print(response.predicted_button_id) # debug print
    return response.predicted_button_id if response.predicted_button_id != "None" else None 

# Loads and injects mutation observer
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

# Finds and clicks the submit button with the response from LLM
def find_and_click_submit_button(driver):
    global clicked

    try:
        
        buttons = extract_buttons_for_llm(driver)
        #print ("=============BUTTONS FOR LLM TO SELECT==============") # debug print
        #print(buttons) # debug print
        if not buttons:
            print("No buttons found on the page.")
            return None  # No interaction possible

        # Use func that retrieves the response of LLM for which button is the submit button
        submit_button_id = get_submit_button_id_from_llm(buttons)

        if not submit_button_id or submit_button_id == "None":
            print("LLM could not identify a submit button. Skipping interaction.")
            return None  # Skip interaction

        # Find the matching button entry
        selected = next((b for b in buttons if b["button_id"] == submit_button_id), None)

        if not selected:
            print(f"No button found for id {submit_button_id}")
            return None

        # Try to find the real Selenium element to compute XPath
        try:
            xpath = None

            # Best effort match: by id, name, class, text, etc.
            if selected.get("id") and selected["id"] != "No ID":
                xpath = f'//*[@id="{selected["id"]}"]'
            elif selected.get("name") and selected["name"] != "No Name":
                xpath = f'//*[@name="{selected["name"]}"]'
            else:
                # fallback: find element by tag and visible text (for button)
                text = selected.get("text", "").strip()
                if text:
                    xpath = f'//{selected["tag"]}[normalize-space()="{text}"]'

            if not xpath:
                print("Could not determine XPath for selected button.")
                return None

            # Try to click the element
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            submit_button.click()
            print("Submit button clicked!")
            clicked = True
            return "clicked"

        except Exception as e:
            print(f"Error clicking submit button: {e}")
            print("Trying JavaScript click...")

            try:
                driver.execute_script("arguments[0].click();", submit_button) #fallback click attempt
                print("JavaScript click executed successfully!")
                clicked = True
                return "clicked"

            except Exception as js_e:
                print(f"JavaScript click failed: {js_e}")
                print("Skipping interaction, testing only pre-submission state.")
                return None

    except Exception as e:
        print(f"Unexpected error in find_and_click_submit_button: {e}")
        return None
    


# LLM call to suggest invalid inputs for the specific form's fields 
class SuggestInvalidInputsForTesting(dspy.Signature):
    """Suggest invalid input values tailored to each field type, in order to trigger meaningful error messages."""

    html_snippet_before = dspy.InputField(desc=(
        "A list of form fields before user interaction. Includes their labels, input types (e.g., text, email, password), and any visible hints."
    ))

    query_goal = dspy.InputField(desc=(
        "Explain that the goal is to test error messages shown when users enter invalid data. The model should suggest realistic invalid values."
    ))

    suggestions = dspy.OutputField(desc=(
        "For each field, return a test input that is intentionally incorrect. Tailor the value based on the field type, and try to variate if there are similar fields:\n"
        "- Email: missing '@' or domain (e.g., 'user.com')\n"
        "- Password: too short, too simple, or missing required characters\n"
        "- Date: wrong format or invalid date (e.g., '32/13/2023')\n"
        "- Numeric: letters instead of numbers\n"
        "- Radio or checkbox: leave unselected\n\n"
        "Return one suggested invalid value per field in a structured format:\n"
        "- Field(label or name): <field>\n"
        "- Suggested invalid input: <value>\n"
    ))

def get_invalid_inputs_for_fields(fields, llm):
    prompt = "\n".join(
        [f"- Label: {f['label']}, Type: {f['type']}" for f in fields]
    )
    input_example = {
        "html_snippet_before": prompt,
        "query_goal": "Suggest invalid inputs to trigger helpful or ambiguous error messages."
    }
    result = llm(**input_example)
    lines = result.suggestions.strip().split("\n")
    parsed = []
    field = None
    value = None

    for line in lines:
        if line.strip().startswith("- Field"):
            match = re.search(r"- Field.*?:\s*(.+)", line)
            if match:
                field = match.group(1).strip()
        elif line.strip().startswith("- Suggested invalid input"):
            match = re.search(r"- Suggested invalid input:\s*(.+)", line)
            if match:
                value = match.group(1).strip()
                if field and value:
                    parsed.append({"field": field, "value": value})
                    field = None
                    value = None

    #print("================[DEBUG parsed suggestions]==================") # debug print
    #print(parsed) # debug print
    return parsed
    



#Type suggested (or fallback) values into the form's fields
def type_invalid_inputs(driver, html_before, predefined_values=None):
    typed_inputs = []

    #print("==========[DEBUG: Predefined Invalid Values]==========") # debug print
    #print(predefined_values)# debug print

    for field in html_before["fields"]:
        label = field.get("label", "")
        field_id = field.get("id")
        field_name = field.get("name")
        field_type = field.get("type", "").lower()
        is_disabled = str(field.get("disabled", "")).lower() in ["true", "1"]
        is_readonly = str(field.get("readonly", "")).lower() in ["true", "1"]


        print(f"\n[FIELD] {label} ({field_type})")
        print(f"- disabled={is_disabled}, readonly={is_readonly}")

        if is_disabled or is_readonly:
            print(f"- Skipping: disabled or readonly")
            continue

        if field_type in ["hidden", "submit", "button", "fieldset", "file", "select", "checkbox"]:
            print(f"- Skipping: unsupported field type")
            continue

        if predefined_values:
            match = next((item for item in predefined_values if item["field"].strip().lower() == label.strip().lower()), None)
            invalid_value = match["value"] if match else fallback_invalid_input(field_type, label)
        else:
            invalid_value = fallback_invalid_input(field_type, label)

        if not invalid_value.strip():
            print(f"- Skipping: no invalid input generated")
            continue

        element = None
        try:
            if field_id:
                print(f"- Trying ID: {field_id}")
                element = driver.find_element(By.ID, field_id)
            elif field_name:
                print(f"- Trying NAME: {field_name}")
                elements = driver.find_elements(By.NAME, field_name)
                for el in elements:
                    if el.is_enabled() and el.is_displayed():
                        element = el
                        break
            else:
                print("- Skipping: no locator (id or name)")
                continue

            if not element:
                print("- Skipping: element not found")
                continue

            if not element.is_enabled() or not element.is_displayed():
                print("- Skipping: element not visible")
                continue

            try:
                element.clear()
            except WebDriverException as e:
                print(f"- Warning: clear() failed: {e}")

            try:
                element.send_keys(invalid_value)
                driver.execute_script("arguments[0].blur();", element)
                print(f"- Typed: '{invalid_value}'")
                typed_inputs.append({
                    "field": label or field_name or field_id,
                    "value": invalid_value
                })
            except WebDriverException as e:
                print(f"- Typing failed: {e}")

        except WebDriverException as e:
            print(f"- Not interactable: {e}")

    print(f"\nTyped invalid values: {typed_inputs}")
    return typed_inputs
