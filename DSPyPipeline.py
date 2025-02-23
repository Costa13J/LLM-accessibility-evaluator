import dspy
from dsp.utils import deduplicate
import os
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.evaluate import Evaluate
counter = 0  # Initialize the global counter

# Set up the API key
os.environ["MISTRAL_API_KEY"] = "vZYsFYM6r2E9JWyD3GYPdLfR34kI2EcO"

# Configure DSPy with the model and retriever
mini = dspy.LM('mistral/mistral-large-latest')
rm = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(lm=mini, rm=rm)

def read_html_file(file_path):
    """Reads an HTML file and returns its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

# Define signatures for evaluation
class EvaluateAccessibility(dspy.Signature):
    """Check if form fields have valid autocomplete attribute AND ALSO if it is appropriate for the label its matched with."""
    html_snippet = dspy.InputField(desc="Extracted text from an HTML form snippet.")
    retrieved_guidelines = dspy.InputField(desc="Relevant information for WCAG 1.3.5 guideline AND Input Purposes for User Interface Components.")
    evaluation = dspy.OutputField(desc="Structured and simple compliance report with identified issues, giving a passed, failed or inapplicable value for each example.")

class GenerateSearchQuery(dspy.Signature):
    """Generate a search query to find relevant information for input purpose identification evaluation (WCAG 1.3.5)"""
    html_snippet = dspy.InputField(desc="Form field HTML snippet containing an input element.")
    query = dspy.OutputField(desc="Search query focusing on correct input autocomplete values for this input type.")

class AccessibilityEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=1, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_accessibility = dspy.ChainOfThought(EvaluateAccessibility)
        self.max_hops = max_hops

    def forward(self, html_snippet, retrieved_guidelines=None):
        global counter
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet).query
                if query in queries:
                    print(f"Skipping redundant query at Hop {hop + 1}: {query}")
                    query = f"Best practices for WCAG 1.3.5 input purpose identification: correct autocomplete for this field in forms" #TO DO Verify
                queries.add(query)

                passages = self.retrieve(query).passages
                if not passages:
                    print(f"Fallback: No results for query at Hop {hop + 1}, trying a reformulated query.")
                    fallback_queries = [
                        "WCAG 1.3.5 correct autocomplete values for form fields",
                        "Common WCAG mistakes in autocomplete attributes",
                        "Best practices for autocomplete use in web forms"
                    ]
                    for fallback in fallback_queries:
                        passages = self.retrieve(fallback).passages
                        if passages:
                            print(f"Using fallback query: {fallback}")
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                counter += 1
                continue

        pred = self.evaluate_accessibility(html_snippet=html_snippet, retrieved_guidelines=retrieved_guidelines)
        return dspy.Prediction(retrieved_guidelines=retrieved_guidelines, evaluation=pred.evaluation, queries=list(queries))

trainset = [
    # Pass cases
    dspy.Example(
        html_snippet="<label>Username<input autocomplete='username'/></label>",
        retrieved_guidelines="Autocomplete attribute value must contain a valid autocomplete token.",
        evaluation="Pass: Autocomplete value 'username' is valid."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    dspy.Example(
        html_snippet="<label> Street address<textarea autocomplete='Street-Address'></textarea></label>",
        retrieved_guidelines=" Mixing upper and lower case letters is allowed for autocomplete attributes.",
        evaluation="Pass: Autocomplete value 'Street-Address' is valid."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    dspy.Example(
        html_snippet="<label>Work email<input autocomplete='work email'/></label>",
        retrieved_guidelines="Autocomplete must contain an acceptable modifier before the field type.",
        evaluation="Pass: 'work email' is a valid combination."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    # Fail: Invalid cases
    dspy.Example(
        html_snippet="<label>Username<input autocomplete='badname'/></label>",
        retrieved_guidelines="Autocomplete attribute must use a valid WCAG token.",
        evaluation="Fail: 'badname' is not a recognized autocomplete value."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    
    dspy.Example(
        html_snippet="<label>Email<input autocomplete='work shipping email'/></label>",
        retrieved_guidelines="'work' must not precede 'shipping'.",
        evaluation="Fail: Order of autocomplete tokens is incorrect."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    # Inapplicable Cases
    dspy.Example(
        html_snippet="<label>Username<input autocomplete=''/></label>",
        retrieved_guidelines="An empty autocomplete attribute is inapplicable.",
        evaluation="Inapplicable: No autocomplete value provided."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Friend's first name<input type='text' autocomplete='off'/></label>",
        retrieved_guidelines="Autocomplete 'off' makes it inapplicable.",
        evaluation="Inapplicable: Autocomplete is disabled explicitly."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<input type='submit' autocomplete='email'/>",
        retrieved_guidelines="Autocomplete does not apply to submit buttons.",
        evaluation="Inapplicable: Autocomplete attribute is ignored on submit buttons."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Friend's first name<input type='text'/></label>",
        retrieved_guidelines="Missing autocomplete attribute makes it inapplicable.",
        evaluation="Inapplicable: Autocomplete is disabled explicitly."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    # Fail: Incorrect cases
    dspy.Example(
        html_snippet="<label>First Name<input autocomplete='family-name'/></label>",
        retrieved_guidelines="The purpose of the form field indicated by the label must correspond with the autocomplete token.",
        evaluation="Fail: 'family-name' should be 'given-name' to match 'First Name' field."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Address identification<input autocomplete='name'/></label>",
        retrieved_guidelines="Autocomplete value must match the expected purpose of the field.",
        evaluation="Fail: 'name' is not appropriate for an input related to address."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Credit Card Number<input autocomplete='name'/></label>",
        retrieved_guidelines="Form fields should use autocomplete values that match their expected user input.",
        evaluation="Fail: 'name' is incorrect for a credit card field. Use 'cc-number'."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

]


# Compile the model for evaluation
teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
compiled_evaluator = teleprompter.compile(AccessibilityEvaluator(), teacher=AccessibilityEvaluator(passages_per_hop=2), trainset=trainset)


html_file_path = "C:\\Users\\Utilizador\\Desktop\\Thesis\\DecathlonAlteracaoMorada-FormHTML.html"
html_snippet = read_html_file(html_file_path)

# Run the accessibility evaluation
if html_snippet:
    pred = compiled_evaluator(html_snippet)
    print(f"Accessibility Evaluation: {pred.evaluation}")
    print(f"Retrieved Information: {pred.retrieved_guidelines}")
    print(f"Number of retrieval errors: {counter}")
else:
    print("No HTML content found.")
