from bs4 import BeautifulSoup

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