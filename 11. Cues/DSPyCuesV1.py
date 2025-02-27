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
class EvaluateInteractiveCues(dspy.Signature):
    """Check if form fields use appropriate cues (disabled, readonly, and required attributes) if they adopt those states."""
    html_snippet = dspy.InputField(desc="Extracted text from an HTML form snippet.")
    retrieved_guidelines = dspy.InputField(desc="Relevant WCAG guidelines and techniques for interactive cues.")
    evaluation = dspy.OutputField(desc="Structured and simple compliance report indicating if each field uses appropriate cues (disabled, readonly, and required attributes) if they adopt those states, indicating a pass or a fail.")

class GenerateSearchQuery(dspy.Signature):
    """Generate a search query to find relevant WCAG guidelines and techniques for interactive cues."""
    html_snippet = dspy.InputField(desc="Form field HTML snippet containing an input element.")
    query = dspy.OutputField(desc="Search query focusing on proper use of disabled, readonly, and required attributes.")

class InteractiveCuesEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=1, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_cues = dspy.ChainOfThought(EvaluateInteractiveCues)
        self.max_hops = max_hops

    def forward(self, html_snippet, retrieved_guidelines=None):
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet).query
                queries.add(query)
                
                passages = self.retrieve(query).passages
                if not passages:
                    fallback_queries = [
                        "WCAG best practices for disabled, readonly, and required attributes",
                        "How to programmatically convey form field states",
                        "Using labels and legends for accessibility in forms"
                    ]
                    for fallback in fallback_queries:
                        passages = self.retrieve(fallback).passages
                        if passages:
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                continue

        pred = self.evaluate_cues(html_snippet=html_snippet, retrieved_guidelines=retrieved_guidelines)
        return dspy.Prediction(retrieved_guidelines=retrieved_guidelines, evaluation=pred.evaluation, queries=list(queries))

trainset = [
    dspy.Example(
        html_snippet="""<label for='username'>*User name:</label><input type='text' name='username' id='username'>""",
        retrieved_guidelines="Required fields must be programmatically conveyed using the 'required' attribute.",
        evaluation="Fail: The required field is indicated visually but lacks the 'required' attribute."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    dspy.Example(
        html_snippet="""<label for='username'>*User name:</label><input type='text' name='username' id='username' required>""",
        retrieved_guidelines="Required fields must have the 'required' attribute.",
        evaluation="Pass: The required field is programmatically conveyed."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    dspy.Example(
        html_snippet="""<input type='text' name='email' id='email' disabled>""",
        retrieved_guidelines="Disabled elements must use the 'disabled' attribute to be programmatically conveyed.",
        evaluation="Pass: The 'disabled' attribute correctly prevents interaction."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    dspy.Example(
        html_snippet="""<input type='text' name='email' id='email' readonly>""",
        retrieved_guidelines="Readonly fields must use the 'readonly' attribute.",
        evaluation="Pass: The 'readonly' attribute is correctly used."
    ).with_inputs("html_snippet", "retrieved_guidelines"),

    dspy.Example(
        html_snippet="""<input type='submit' required>""",
        retrieved_guidelines="The 'required' attribute does not apply to submit buttons.",
        evaluation="Inapplicable: Required attribute is ignored on submit buttons."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
]

teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
compiled_evaluator = teleprompter.compile(InteractiveCuesEvaluator(), teacher=InteractiveCuesEvaluator(passages_per_hop=2), trainset=trainset)

html_file_path = "C:\\Users\\Utilizador\\Desktop\\Thesis\\11. Cues\\CTTCriarConta-FormHTML.html"
html_snippet = read_html_file(html_file_path)

# Run the accessibility evaluation
if html_snippet:
    pred = compiled_evaluator(html_snippet)
    print(f"Accessibility Evaluation: {pred.evaluation}")
    print(f"Retrieved Information: {pred.retrieved_guidelines}")
    print(f"Number of retrieval errors: {counter}")
else:
    print("No HTML content found.")
