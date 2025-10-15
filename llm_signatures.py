import dspy

# Signature for evaluation of Missing Programmatic Cues – Required
class EvaluateInteractiveCues(dspy.Signature):
    """Evaluate whether form fields correctly use the 'required' attribute based on their behavior after submission."""
    html_snippet_before = dspy.InputField(desc=(
        "A list of the form fields before user interaction. This includes relevant HTML elements, attributes (e.g., 'required'), and labels."
    ))
    mutations = dspy.InputField(desc=(
        "List of DOM mutations observed after submitting the form with empty fields. "
        "This includes changes that indicate which fields were treated as required—such as added error messages, styling changes, or validation-related attributes like 'aria-invalid'."
    ))
    retrieved_guidelines = dspy.InputField(desc=(
        "Relevant WCAG techniques and best practices specifically focused on the correct use of the HTML 'required' attribute or equivalent cues to indicate mandatory fields."
    ))
    identification = dspy.OutputField(desc=(
        "Individually identify each field by its visible label (preferred), or by its name/id attribute if no label is available."
    ))
    evaluation = dspy.OutputField(desc=(
        "For each field, determine only whether the 'required' attribute (or an equivalent mechanism) is used appropriately, based on whether the field behaves as required after submission. Classify each field as:\n"
        "- pass: The field is required and clearly uses the 'required' attribute or an equivalent semantic cue (e.g., aria-required).\n"
        "- fail: The field is required but lacks the 'required' attribute or any equivalent semantic indicator (e.g., aria-required).\n"
        "- inapplicable: The field is optional (not marked as required in behavior) or not subject to required validation.\n\n"
        "Do not fail a field for unrelated issues such as missing error messages or lack of ARIA descriptions. This evaluation is only about required status and how it is declared."
    ))
    reasoning = dspy.OutputField(desc=(
        "For each field, explain why it was marked 'pass', 'fail', or 'inapplicable'.\n"
        "- Describe what cues (if any) suggested the field is required after submission.\n"
        "- Indicate whether the field had the 'required' attribute or equivalent (e.g., aria-required).\n"
        "- Do not include reasoning about error messages, linking, or general accessibility unless it directly relates to the required status.\n"
        "- If marked 'inapplicable', justify why the field is optional."
    ))
    format = dspy.OutputField(desc=(
        "Provide a separate evaluation for each field, using exactly this structure:\n\n"
        "-Identification(label or name of the field): <identification>\n"
        "-Evaluation(\"pass\" or \"fail\" or \"inapplicable\"): <evaluation>\n"
        "-Reasoning(explanation of the evaluation result): <reasoning>\n\n"
        "Only evaluate whether the 'required' attribute (or equivalent) is appropriately used. Do not evaluate error messaging or other accessibility criteria.\n"
        "Do not group multiple fields together. Each must be assessed individually.\n"
        "Do not include extra commentary or summaries."
    ))






# Signature for evaluation of Failure to Identify Errors or Invalid Identification
class EvaluateErrorIdentification(dspy.Signature):
    """Evaluate whether each form field provides accessible error identification, individually."""

    html_snippet_before = dspy.InputField(desc=(
        "A list of form fields and their HTML structure before user interaction. This includes input elements, labels, and validation-related attributes."
    ))
    mutations = dspy.InputField(desc=(
        "List of DOM mutations after form submission with empty inputs. Includes all observed error messages, added attributes like 'aria-invalid' or 'aria-describedby', and any other changes to the fields or surrounding markup."
    ))
    retrieved_guidelines = dspy.InputField(desc=(
        "Relevant WCAG techniques and accessibility best practices for identifying input errors and associating error messages with individual fields."
    ))
    identification = dspy.OutputField(desc=(
        "Individually identify each field by its visible label (preferred), or by its name/id attribute if no label is available. Each field must be listed separately."
    ))
    evaluation = dspy.OutputField(desc=(
        "Individually assess each field for accessible error identification after submission, and classify each one as 'pass', 'fail', or 'inapplicable':\n"
        "- pass: A specific error message is shown for this field, programmatically and visually associated.\n"
        "- fail: No specific error message is shown, or the or the message is not programmatically or visually associated with the field.\n"
        "- inapplicable: The field is optional or does not require validation when left empty."
    ))
    reasoning = dspy.OutputField(desc=(
        "For each individual field, explain briefly why it received its evaluation:\n"
        "- Mention if an error message appeared after submission.\n"
        "- Specify if it was visually or programmatically linked (e.g., via aria-describedby, label 'for').\n"
        "- Mention if indicators like 'aria-invalid' were used.\n"
        "- If marked 'inapplicable', justify why."
    ))
    format = dspy.OutputField(desc=(
        "List each field individually and follow this exact structure for each one:\n\n"
        "-Identification(label or name of the field): <identification>\n"
        "-Evaluation(\"pass\" or \"fail\" or \"inapplicable\"): <evaluation>\n"
        "-Reasoning(explanation of the evaluation result): <reasoning>\n\n"
        "Never group multiple fields together. Each field must be evaluated and explained on its own.\n"
        "Do not include extra commentary or summaries."
    ))


# Signature for evaluation of Ambiguous or Generic Error Messages
class EvaluateErrorClarity(dspy.Signature):
    """Evaluate whether error messages clearly explain the input problem and guide the user toward correction (WCAG 3.3.3)."""

    html_snippet_before = dspy.InputField(desc=(
        "HTML structure of the form fields before user interaction. This includes each input’s label, type, constraints (e.g., pattern, minlength), and attributes like aria-describedby."
    ))
    invalid_inputs = dspy.InputField(desc=(
        "List of values submitted into specific fields to test error handling. These values are intentionally unusual, malformed, or nonstandard — but not necessarily guaranteed to trigger validation."
    ))
    mutations = dspy.InputField(desc=(
        "List of DOM mutations after form submission. Includes error messages shown, updated attributes (e.g., aria-invalid), and other relevant visual or programmatic feedback."
    ))
    retrieved_guidelines = dspy.InputField(desc=(
        "Relevant WCAG techniques and best practices for ensuring clear and actionable error messages (especially for WCAG 3.3.3)."
    ))
    identification = dspy.OutputField(desc=(
        "Identify each field by its visible label (preferred), or by name/id if no label is available. Each field must be evaluated separately."
    ))
    evaluation = dspy.OutputField(desc=(
        "Assess whether the system provided clear guidance when a validation error was triggered. Use these options per field:\n"
        "- pass: A validation error was triggered, and the message clearly explains the problem and how to fix it.\n"
        "- fail: A validation error was triggered, but the message was missing, vague, or unhelpful.\n"
        "- inapplicable: No validation was triggered, or no error was expected for the given input."
    ))
    reasoning = dspy.OutputField(desc=(
        "For each field, explain the evaluation:\n"
        "- What test input was used?\n"
        "- Was a validation error triggered (e.g., aria-invalid=true, message shown)?\n"
        "- What message (if any) was shown?\n"
        "- Justify the evaluation:\n"
        "  - For 'pass': show how the message helped the user fix the input\n"
        "  - For 'fail': explain what was missing or unclear\n"
        "  - For 'inapplicable': explain why no validation was expected or triggered"
    ))
    format = dspy.OutputField(desc=(
        "Provide a structured evaluation per field using exactly this format:\n\n"
        "-Identification(label or name of the field): <identification>\n"
        "-Evaluation(\"pass\" or \"fail\" or \"inapplicable\"): <evaluation>\n"
        "-Reasoning(explanation of the evaluation result): <reasoning>\n"
        "Do not group multiple fields together. Do not add summaries or extra commentary."
    ))


# Signature for evaluation of Error States Indicated Only by Color
class EvaluateUseOfColor(dspy.Signature):
    """Evaluate whether error states in form fields rely solely on color"""
    html_snippet_before = dspy.InputField(desc=(
        "A list of form fields and their HTML structure before user interaction. "
        "This includes input elements, labels, and validation-related attributes."
    ))
    invalid_inputs = dspy.InputField(desc=(
        "List of intentionally malformed input values submitted to trigger errors."
    ))
    mutations = dspy.InputField(desc=(
        "List of DOM mutations observed after submitting invalid input. Includes any visual changes "
        "(e.g., red border, background color), attribute changes (e.g., aria-invalid), "
        "and added messages (e.g., 'Enter a valid email')."
    ))
    retrieved_guidelines = dspy.InputField(desc=(
        "Relevant WCAG techniques and best practices for ensuring that errors are "
        "not communicated using color alone."
    ))
    identification = dspy.OutputField(desc=(
        "Individually identify each field by its visible label (preferred) or its name/id if no label is available. "
        "Each field must be listed separately."
    ))
    evaluation = dspy.OutputField(desc=(
        "For each field, classify the ERROR cue based only on invalid input submissions.\n\n"
        "Error cue classification:\n"
        "   - PASS: Error is indicated with programmatic/textual support such as `aria-invalid=\"true\"`, "
        "an error message linked via `aria-describedby`, a role=\"alert\" message associated with the input, "
        "or visible text programmatically linked to the field.\n"
        "   - FAIL: The only error indicator is a visual treatment (red border, color change) "
        "with no textual or programmatic indication that there was an error\n"
        "   - INAPPLICABLE: No error was triggered for invalid input.\n\n"
        "**Only evaluate error cues in terms of reliance on color versus programmatic or textual alternatives. "
        "Don't evaluate wether there is programmatic association cues and other unrelated accessibility issues.**"
    ))
    reasoning = dspy.OutputField(desc=(
        "For each field, briefly explain why the error cue received its evaluation:\n"
        "- State what indicators were detected for the error cue (e.g., aria-invalid, linked error message, red text).\n"
        "- Connect each indicator to the classification (pass, fail, inapplicable).\n"
        "- Explicitly say if the error cue relies only on color, or why it is inapplicable.\n"
        "- If the error message is not programmatically associated, mention it here\n"
        "Keep explanations short and focused only on error cues and their use of color."
    ))
    format = dspy.OutputField(desc=(
        "For each field, provide output in this exact format:\n\n"
        "-Identification(label or name of the field): <identification>\n"
        "-Evaluation(\"pass\" or \"fail\" or \"inapplicable\"): <eval>"
        "-Reasoning(explanation of the evaluation result): <reasoning>\n\n"
        "Do not combine multiple fields. Each field must be evaluated and explained independently."
    ))



# Generate a search query to find relevant WCAG guidelines and techniques for Missing Programmatic Cues – Required
class GenerateSearchRequired(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured HTML snippet representing form field attributes before user interaction. "
        "This includes relevant states such as `required`, `disabled`, `readonly`, and associated validation feedback."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant examples from wcag and best practices. "
        "The query should focus on accessibility issues related to form cues, ensuring proper use of `required` attributes."
    ))

# Generate a search query to find relevant WCAG guidelines and techniques for Failure to Identify Errors or Invalid Identification
class GenerateSearchQuery(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured representation of form fields and their behavior before user interaction. "
        "This includes validation-related attributes (e.g., `aria-invalid`, `aria-describedby`) and observed error messages."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant WCAG techniques and accessibility best practices. "
        "The query should focus on how error messages should be identified and associated with form fields. "
    ))

# Generate a search query to find relevant WCAG guidelines and techniques for Ambiguous or Generic Error Messages
class GenerateSearchQueryErrorClarity(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured list of form fields with types and invalid inputs used for testing error message clarity."
    ))
    query = dspy.OutputField(desc=(
        "Search query focused on WCAG 3.3.3 and how error messages should guide users to correct mistakes."
    ))

# Generate a search query to find relevant WCAG guidelines and techniques for Error States Indicated Only by Color
class GenerateSearchQueryUseOfColor(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured list of form fields with labels, types, and attributes before user interaction. "
        "Used to generate queries focused on how required or error cues may rely solely on color."
    ))
    query = dspy.OutputField(desc=(
        "Search query focused on WCAG 1.4.1 and how forms must not rely only on color to convey required fields or validation errors."
    ))

