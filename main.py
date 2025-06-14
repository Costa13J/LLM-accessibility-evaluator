from driver_utils import setup_webdriver, inject_cookie_dismiss_script
from extractors import extract_fields
from interaction import find_and_click_submit_button
from mutation_utils import extract_mutation_observer_results
from evaluator import run_evaluation
from save_results import save_to_json
from config import url
import logging

logging.getLogger("chromadb").setLevel(logging.ERROR)

def run_pipeline():
    driver = setup_webdriver()
    driver.get(url)
    inject_cookie_dismiss_script(driver)

    html_before = extract_fields(driver)
    action_result = find_and_click_submit_button(driver)
    submit_clicked = (action_result == "clicked")
    mutations = extract_mutation_observer_results(driver) if action_result == "clicked" else None
    driver.quit()

    result = run_evaluation(html_before, mutations, url, submit_clicked)
    save_to_json(result, url, submit_clicked=submit_clicked)


if __name__ == "__main__":
    run_pipeline()
