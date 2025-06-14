import dspy

# Signature for evaluation
class EvaluateInteractiveCues(dspy.Signature):
    """Check if form fields use appropriate required attributes if they adopt that state."""
    #html_snippet_before = dspy.InputField(desc="Form HTML snippet before user interaction.") #Use this for full form
    html_snippet_before = dspy.InputField(desc="A list of the fields from the form to evaluate before user interaction.") #Use this for fields
    mutations = dspy.InputField(desc="List of DOM mutations detected after submission of the form when left empty, capturing error messages and attribute changes.")
    retrieved_guidelines = dspy.InputField(desc="Relevant examples and best practices for the use of required attributes in form fields.")
    identification = dspy.OutputField(desc="For each field, extract and list its identification (preferably its label or name attribute) from the HTML snippet.")
    evaluation = dspy.OutputField(desc="""For each field, assess whether it correctly uses the 'required' attribute when appropriate based on the field’s behavior after submission (using the provided DOM mutations and best practice guidelines).
Assign a simple result: 'pass', 'fail', or 'inapplicable' for each field.""")
    reasoning = dspy.OutputField(desc="""For each field, explain briefly why the evaluation was 'pass', 'fail', or 'inapplicable'. 
Focus the reasoning on accessibility concerns related to form validation cues (such as missing required attributes, inappropriate required attributes, or use of other mechanisms instead of HTML5 native required attribute).""")
    format = dspy.OutputField(desc="""After filling Identification, Evaluation, and Reasoning individually for each field, assemble the final output with this structure for each field:
-Identification(label or name of the field): <identification> 
-Evaluation("pass" or "fail" or "inapplicable"): <evaluation>
-Reasoning(explanation of the evaluation result): <reasoning>
    Ensure this exact structure is followed without any additional commentary.""")

# Generate a search query to find relevant WCAG guidelines and techniques for interactive cues.
"""class GenerateSearchQuery(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured HTML snippet representing form field attributes before and after user interaction. "
        "This includes relevant states such as `required`, `disabled`, `readonly`, and associated validation feedback."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant examples from wcag and best practices. "
        "The query should focus on accessibility issues related to form cues, ensuring proper use of `required` attributes."
    ))"""

# Generate a search query to find relevant WCAG guidelines and techniques for error identification.
class GenerateSearchQuery(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured representation of form fields and their behavior before and after user interaction. "
        "This includes validation-related attributes (e.g., `aria-invalid`, `aria-describedby`) and observed error messages."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant WCAG techniques and accessibility best practices. "
        "The query should focus on how error messages should be identified and associated with form fields. "
    ))


#Failure to identify errors
class EvaluateErrorIdentification(dspy.Signature):
    html_snippet_before = dspy.InputField(desc=(
        "List of form fields with their attributes before user interaction. "
        "Each field includes label, type, required status, and any accessibility attributes."
    ))

    mutations = dspy.InputField(desc=(
        "Summary of DOM mutations after form submission. Includes error messages, attribute changes "
        "like aria-invalid or aria-describedby, and whether messages are linked to input fields."
    ))

    retrieved_guidelines = dspy.InputField(desc=(
        "Relevant examples and best practices for identifying input errors and associating messages with fields."
    ))

    identification = dspy.OutputField(desc=(
        "For each field, identify it by its label (preferred), or name/id if no label is available."
    ))

    evaluation = dspy.OutputField(desc=(
        "For each field, state one of: 'pass', 'fail', or 'inapplicable'.\n"
        "- pass: A visible error message is shown when the field is left empty, and it is programmatically or visually linked to the field.\n"
        "- fail: No error message is shown, or it appears but is not clearly or programmatically linked to the field (e.g., missing aria-describedby, visual proximity, or clear label reference).\n"
        "- inapplicable: The field is not expected to trigger a validation message (e.g., optional field)."
    ))

    reasoning = dspy.OutputField(desc=(
        "For each field, explain why it passed, failed, or was inapplicable. "
        "- Specify if an error message appeared after submission.\n"
    "- State whether the message was programmatically linked (e.g., via aria-describedby, 'for' attributes) or visually associated with the input.\n"
    "- Mention if semantic indicators like aria-invalid were added.\n"
    "- If the field is inapplicable, explain why it is considered optional or not expected to show errors."
    ))

    format = dspy.OutputField(desc=(
    "Present the results for each field using this exact format. Repeat it once per field:\n\n"
    "-Identification(label or name of the field): <identification>\n"
    "-Evaluation(\"pass\" or \"fail\" or \"inapplicable\"): <evaluation>\n"
    "-Reasoning(explanation of the evaluation result): <reasoning>\n\n"
    "Do not include any other comments or summaries. Follow this structure exactly."
    ))




