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


counter = 0  #global counter
clicked = False #global"clicked" boolean












# Loads a webpage, extracts form fields before interaction.
def extract_html_with_states(url):

    driver = setup_webdriver()
    driver.get(url)
    time.sleep(2)  # give time for banners to appear
    inject_cookie_dismiss_script(driver)

    # Wait up to 10 seconds for a form element to be present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        print("Form loaded.")
    except Exception as e:
        print(f"Form did not load within timeout: {e}")


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
