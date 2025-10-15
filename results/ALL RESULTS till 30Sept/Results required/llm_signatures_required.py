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
class GenerateSearchQuery(dspy.Signature):
    html_snippet = dspy.InputField(desc=(
        "A structured HTML snippet representing form field attributes before and after user interaction. "
        "This includes relevant states such as `required`, `disabled`, `readonly`, and associated validation feedback."
    ))
    query = dspy.OutputField(desc=(
        "A well-formed search query designed to retrieve the most relevant examples from wcag and best practices. "
        "The query should focus on accessibility issues related to form cues, ensuring proper use of `required` attributes."
    ))
