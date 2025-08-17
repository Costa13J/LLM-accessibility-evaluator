from driver_utils import setup_webdriver, inject_cookie_dismiss_script
from extractors import extract_fields
from interaction import find_and_click_submit_button,    type_invalid_inputs
from mutation_utils import extract_mutation_observer_results
from evaluator import run_evaluation
from save_results import save_to_json
from config import url
import logging
import json
import time
import sys
from interaction import get_invalid_inputs_for_fields, SuggestInvalidInputsForTesting
import dspy

logging.getLogger("chromadb").setLevel(logging.ERROR)

def run_pipeline(evaluation_mode="wcag-3.3.1"):
    driver = setup_webdriver()
    driver.get(url)
    inject_cookie_dismiss_script(driver)
    time.sleep(5)

    html_before = extract_fields(driver)
    print(json.dumps(html_before, indent=2))

    # Special case: WCAG 1.4.1 needs both empty and invalid inputs
    if evaluation_mode == "1.4.1":
        # === PASS 1: Empty Submission ===
        action_result = find_and_click_submit_button(driver)
        submit_clicked = (action_result == "clicked")
        time.sleep(5)
        mutations_empty = extract_mutation_observer_results(driver) if submit_clicked else None

        # === PASS 2: Invalid Inputs Submission ===
        # Reload the page fresh to reset DOM state
        driver.get(url)
        inject_cookie_dismiss_script(driver)
        time.sleep(5)
        html_before_2 = extract_fields(driver)

        llm = dspy.Predict(SuggestInvalidInputsForTesting)
        invalid_suggestions = get_invalid_inputs_for_fields(html_before_2["fields"], llm=llm)
        typed_values = type_invalid_inputs(driver, html_before_2, predefined_values=invalid_suggestions)

        action_result = find_and_click_submit_button(driver)
        submit_clicked = (action_result == "clicked")
        time.sleep(5)
        mutations_invalid = extract_mutation_observer_results(driver) if submit_clicked else None

        driver.quit()
        print("==== MUTATIONS EMPTY=====")
        print(mutations_empty)
        print("==== MUTATIONS INVALID =====")
        #print(mutations_invalid)

        # Evaluate both passes separately
        result_empty = run_evaluation(html_before, mutations_empty, url, True, evaluation_mode, interaction_type="empty_submit")

        result_invalid = run_evaluation(html_before_2, mutations_invalid, url, True, evaluation_mode, invalid_inputs=typed_values, interaction_type="invalid_input_submit")


        combined_result = {
            "empty_submit": result_empty,
            "invalid_input_submit": result_invalid
        }

        model_name = dspy.settings.lm.model if hasattr(dspy.settings.lm, "model") else "unknown"
        save_to_json(combined_result, url, submit_clicked=True, model=model_name, evaluation_mode=evaluation_mode)
        return

    # === Default (single interaction) ===
    if evaluation_mode == "3.3.3":
        llm = dspy.Predict(SuggestInvalidInputsForTesting)
        invalid_suggestions = get_invalid_inputs_for_fields(html_before["fields"], llm=llm)
        typed_values = type_invalid_inputs(driver, html_before, predefined_values=invalid_suggestions)
    else:
        typed_values = None

    action_result = find_and_click_submit_button(driver)
    submit_clicked = (action_result == "clicked")
    time.sleep(5)
    mutations = extract_mutation_observer_results(driver) if submit_clicked else None
    print("==== MUTATIONS =====")
    print(mutations)
    driver.quit()

    if evaluation_mode == "3.3.3":
        result = run_evaluation(html_before, mutations, url, submit_clicked, evaluation_mode, invalid_inputs=typed_values)
    else:
        result = run_evaluation(html_before, mutations, url, submit_clicked, evaluation_mode)

    model_name = dspy.settings.lm.model if hasattr(dspy.settings.lm, "model") else "unknown"
    save_to_json(result, url, submit_clicked=submit_clicked, model=model_name, evaluation_mode=evaluation_mode)




if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "wcag-3.3.1"
    run_pipeline(evaluation_mode=mode)

