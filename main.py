from driver_utils import setup_webdriver, inject_cookie_dismiss_script
from extractors import extract_fields
from interaction import find_and_click_submit_button, find_and_dismiss_popup
from mutation_utils import extract_mutation_observer_results
from evaluator import run_evaluation
from save_results import save_to_json
from config import url
import logging
import json
import time
import sys

logging.getLogger("chromadb").setLevel(logging.ERROR)

def run_pipeline(evaluation_mode="wcag-3.3.1"):
    driver = setup_webdriver()
    driver.get(url)
    inject_cookie_dismiss_script(driver)

    time.sleep(5)
    html_before = extract_fields(driver)
    print(json.dumps(html_before, indent=2))
    action_result = find_and_click_submit_button(driver)
    submit_clicked = (action_result == "clicked")
    mutations = extract_mutation_observer_results(driver) if action_result == "clicked" else None
    print(mutations)
    driver.quit()

    result = run_evaluation(html_before, mutations, url, submit_clicked, evaluation_mode)
    save_to_json(result, url, submit_clicked=submit_clicked, evaluation_mode=evaluation_mode)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "wcag-3.3.1"
    run_pipeline(evaluation_mode=mode)

