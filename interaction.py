import dspy
from extractors import extract_buttons_for_llm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# LLM identifies the actual submit button 
class IdentifySubmitButton(dspy.Signature):

    buttons_info = dspy.InputField(desc="List of button elements on the page, including tag, text, title, id, name, type, value and onclick.")
    predicted_button_id = dspy.OutputField(desc="The button_id (e.g., 'button_3') of the button that is most likely the submit or advance button for the form. Return only one Xpath (or 'None' if no such button exists).")

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
        print ("=============BUTTONS FOR LLM TO SELECT==============")
        print(buttons)
        if not buttons:
            print("No buttons found on the page.")
            return None  # No interaction possible

        # Ask LLM which button is the submit button
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
                driver.execute_script("arguments[0].click();", submit_button)
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
    
class IdentifyPopupDismissButton(dspy.Signature):
    buttons_info = dspy.InputField(desc="List of visible button elements on the page (text, id, name, onclick, type).")
    predicted_button_xpath = dspy.OutputField(desc="The exact XPATH of the button that is most likely a accept/continue/agree/dismiss button for a popup or cookie banner (or 'None' if no such popup or alert exists).")

identify_popup_dismiss_button = dspy.ChainOfThought(IdentifyPopupDismissButton)


def find_and_dismiss_popup(driver):
    try:
        from extractors import extract_buttons_for_llm

        print("🔍 [PopupHandler] Extracting all visible buttons...")
        buttons = extract_buttons_for_llm(driver)
        if not buttons:
            print("⚠️ [PopupHandler] No visible buttons found on the page.")
            return False
        
        # 🔍 Print extracted button info
        print("🧵 [PopupHandler] Extracted buttons:")
        for i, b in enumerate(buttons):
            print(f"  {i+1}. {b}")

        print(f"📦 [PopupHandler] {len(buttons)} buttons found. Sending to LLM for popup dismiss prediction.")
        response = identify_popup_dismiss_button(buttons_info=str(buttons))

        dismiss_button_xpath = response.predicted_button_xpath
        print(f"🤖 [PopupHandler] LLM Response: {dismiss_button_xpath}")

        if not dismiss_button_xpath or dismiss_button_xpath.strip().lower() == "none":
            print("🚫 [PopupHandler] LLM did not identify any popup dismiss button.")
            return False

        # Try native click
        try:
            print(f"🎯 [PopupHandler] Trying to click button with XPath: {dismiss_button_xpath}")
            dismiss_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, dismiss_button_xpath))
            )
            dismiss_button.click()
            print("✅ [PopupHandler] Click succeeded (normal click).")
            return True

        except Exception as e:
            print(f"⚠️ [PopupHandler] Normal click failed: {e}")
            print("🧪 [PopupHandler] Attempting fallback JavaScript click...")
            try:
                driver.execute_script("arguments[0].click();", dismiss_button)
                print("✅ [PopupHandler] Click succeeded (JavaScript fallback).")
                return True
            except Exception as js_e:
                print(f"❌ [PopupHandler] JavaScript click also failed: {js_e}")
                return False

    except Exception as e:
        print(f"🔥 [PopupHandler] Unexpected error: {e}")
        return False
