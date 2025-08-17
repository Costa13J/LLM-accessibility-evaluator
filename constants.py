FALLBACK_QUERIES = [
    "Best practices for the 'required' attribute in forms under WCAG.",
    "Ensuring error messages are programmatically linked to form inputs for accessibility.",
    "How should the 'disabled' attribute be used to comply with accessibility standards?",
    "What ARIA attributes can be used to enhance form cues?"
]


FALLBACK_QUERIES_ERROR_IDENTIFICATION = [
    "WCAG techniques for identifying form errors",
    "how to programmatically associate error messages in forms",
    "ARIA attributes for validation error feedback",
    "accessible error identification in web forms"
]


FALLBACK_QUERIES_ERROR_CLARITY = [
    "wcag 3.3.3 error suggestion examples",
    "how to make error messages clear in web forms",
    "accessible validation feedback for incorrect inputs",
    "best practices for helpful error messages in forms"
]

FALLBACK_QUERIES_USE_OF_COLOR = [
    "color-only feedback accessibility",
    "WCAG 1.4.1 required field color only",
    "visual error without text accessibility"
]


FALLBACK_QUERIES_MAP = {
    "wcag-3.3.1": FALLBACK_QUERIES_ERROR_IDENTIFICATION,
    "1.4.1": FALLBACK_QUERIES_USE_OF_COLOR,
    "required": FALLBACK_QUERIES,
    "3.3.3": FALLBACK_QUERIES_ERROR_CLARITY,
}

def fallback_invalid_input(field_type, label):
    label = label.lower()
    if "email" in label or field_type == "email":
        return "userexample.com"
    if "password" in label or field_type == "password":
        return "1234"
    if "date" in label or field_type in ["date", "datetime-local"]:
        return "32/13/2023"
    if "phone" in label or field_type == "tel":
        return "abc123"
    if "number" in label or field_type == "number":
        return "abc"
    if field_type == "url":
        return "htp:/invalid"
    return "!"

