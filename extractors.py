from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

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


#Extracts the fields from the form, with their attributes and also errors 
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

        # === Label Extraction with Source Annotation ===
        label_text = None
        label_source = None

        # 1. label[for=id]
        if input_field.has_attr("id"):
            label_elem = soup.find("label", {"for": input_field["id"]})
            if label_elem and label_elem.text.strip():
                label_text = label_elem.text.strip()
                label_source = "label[for]"

        # 2. <label> wrapper
        if not label_text:
            wrapping_label = input_field.find_parent("label")
            if wrapping_label and wrapping_label.text.strip():
                label_text = wrapping_label.text.strip()
                label_source = "label-wrapper"

        # 3. aria-labelledby
        if not label_text and input_field.has_attr("aria-labelledby"):
            ids = input_field["aria-labelledby"].split()
            parts = []
            for ref_id in ids:
                label_ref = soup.find(id=ref_id)
                if label_ref and label_ref.text.strip():
                    parts.append(label_ref.text.strip())
            if parts:
                label_text = " ".join(parts)
                label_source = "aria-labelledby"

        # 4. aria-label
        if not label_text and input_field.has_attr("aria-label"):
            label_text = input_field["aria-label"].strip()
            label_source = "aria-label"

        # 5. placeholder
        if not label_text and input_field.has_attr("placeholder"):
            label_text = input_field["placeholder"].strip()
            label_source = "placeholder"

        # 6. title
        if not label_text and input_field.has_attr("title"):
            label_text = input_field["title"].strip()
            label_source = "title"

        # 7. fallback
        if not label_text:
            label_text = "No Label"
            label_source = "none"


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
            "label_source": label_source,
            "name": input_field.get("name", ""),
            "id": input_field.get("id", ""),
            "type": input_field.get("type", input_field.name),  # fallback to tag
            "value": value,
            "required": "yes" if input_field.has_attr("required") or input_field.get("aria-required", "").strip().lower() == "true" else "no required attribute",
            "required_source": (
                "required attribute" if input_field.has_attr("required")
                else "aria-required" if input_field.get("aria-required", "").strip().lower() == "true"
                else "none"
            ),
            "disabled": "yes" if input_field.has_attr("disabled") else "no disabled attribute",
            "readonly": "yes" if input_field.has_attr("readonly") else "no read-only attribute",
            "autocomplete": input_field.get("autocomplete", "no autocomplete"),
            "inputmode": input_field.get("inputmode", "no inputmode")
        }

        fields.append(field_info)

    print("===== FIELDS PASSED TO LM =====")
    print(fields)

    return {"fields": fields}


def get_xpath(driver, element):
    # Recursively build XPath from the element up to the root
    def get_element_xpath(el):
        if el.tag_name == 'html':
            return '/html'
        parent = el.find_element(By.XPATH, '..')
        siblings = parent.find_elements(By.XPATH, f"./{el.tag_name}")
        if len(siblings) == 1:
            return get_element_xpath(parent) + f"/{el.tag_name}"
        else:
            index = siblings.index(el) + 1
            return get_element_xpath(parent) + f"/{el.tag_name}[{index}]"
    
    try:
        return get_element_xpath(element)
    except Exception as e:
        return f"Could not determine XPath: {e}"

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def extract_buttons_for_llm(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = []
    button_index = 0

    # Loop through button and input tags
    for tag in ['button', 'input']:
        for elem in soup.find_all(tag):
            text = elem.get_text(strip=True) if tag == "button" else "No Text"
            title = elem.get("title") or elem.get("aria-label") or text
            value = elem.get("value", "No Value")

            # Attempt to locate the same element in the DOM to check visibility
            sel_elem = None
            try:
                if elem.get("id"):
                    sel_elem = driver.find_element(By.ID, elem["id"])
                elif elem.get("name"):
                    sel_elem = driver.find_element(By.NAME, elem["name"])
                elif text:
                    sel_elem = driver.find_element(By.XPATH, f'//{tag}[normalize-space()="{text}"]')
            except:
                pass

            if sel_elem is not None:
                try:
                    if not sel_elem.is_displayed():
                        continue  # Skip hidden buttons
                except:
                    continue  # Skip if visibility check fails
            else:
                continue  # Skip if we couldn't match it in the DOM

            elements.append({
                "button_id": f"button_{button_index}",
                "tag": tag,
                "text": text,
                "title": title,
                "id": elem.get("id", "No ID"),
                "name": elem.get("name", "No Name"),
                "onclick": elem.get("onclick", "No OnClick"),
                "type": elem.get("type", "No Type"),
                "value": value,
                "hidden": False
            })
            button_index += 1

    # Include other clickable elements with onclick (e.g., spans/divs)
    for elem in soup.find_all(onclick=True):
        tag = elem.name
        text = elem.get_text(strip=True)
        title = elem.get("title") or elem.get("aria-label") or text
        value = elem.get("value", "No Value")

        # Try to locate the element in the DOM
        sel_elem = None
        try:
            if elem.get("id"):
                sel_elem = driver.find_element(By.ID, elem["id"])
            elif elem.get("name"):
                sel_elem = driver.find_element(By.NAME, elem["name"])
            elif text:
                sel_elem = driver.find_element(By.XPATH, f'//{tag}[normalize-space()="{text}"]')
        except:
            pass

        if sel_elem is not None:
            try:
                if not sel_elem.is_displayed():
                    continue
            except:
                continue
        else:
            continue

        elements.append({
            "button_id": f"button_{button_index}",
            "tag": tag,
            "text": text or "No Text",
            "title": title,
            "id": elem.get("id", "No ID"),
            "name": elem.get("name", "No Name"),
            "onclick": elem.get("onclick", "No OnClick"),
            "type": tag,
            "value": value,
            "hidden": False
        })
        button_index += 1

    return elements

