import dspy
from extractors import extract_buttons_for_llm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                EC.element_to_be_clickable((By.XPATH, submit_button_id))
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