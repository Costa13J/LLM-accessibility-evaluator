import dspy
from dsp.utils import deduplicate
from dspy.datasets import HotPotQA
import os
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.evaluate import Evaluate

counter = 0  # Initialize the global counter

# Set up the API key
os.environ["MISTRAL_API_KEY"] = "vZYsFYM6r2E9JWyD3GYPdLfR34kI2EcO"

# Configure DSPy with the model
mini = dspy.LM('mistral/open-mistral-nemo-2407')
rm = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(lm=mini, rm=rm)

# Load the dataset
dataset = HotPotQA(train_seed=1, train_size=10, eval_seed=2023, dev_size=25, test_size=0)
trainset = [x.with_inputs('question') for x in dataset.train]
devset = [x.with_inputs('question') for x in dataset.dev]

# Define signatures and modules
class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers"""
    context = dspy.InputField(desc="may contain relevant facts.")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words'.")

class GenerateSearchQuery(dspy.Signature):
    """Write a simple search query that will help answer a complex question"""
    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    query = dspy.OutputField(desc="write a simple and concise search query to answer a more complex question")

class SimplifiedBaleen(dspy.Module):
    def __init__(self, passages_per_hop=1, max_hops=3):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.max_hops = max_hops

    def forward(self, question):
        global counter 
        context = []
        queries = []  # List to store queries
        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](context=context, question=question).query
                print(f"Generated Query at Hop {hop + 1}: {query}")  # Print the query
                queries.append(query)  # Store the query in the list
                passages = self.retrieve(query).passages
                context = deduplicate(context + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                counter += 1  # Increment the counter on error
                break  # Exit loop on error, possibly adjust logic here

        # Generate the answer regardless of the retrieval success
        pred = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=pred.answer, queries=queries)  # Return queries with prediction

def validate_context_and_answer_and_hops(example, pred, trace=None):
    try:
        if not dspy.evaluate.answer_exact_match(example, pred):
            return False
        if not dspy.evaluate.answer_passage_match(example, pred):
            return False

        hops = [example.question] + [outputs.query for *_, outputs in trace if 'query' in outputs]
        if max([len(h) for h in hops]) > 100: 
            return False
        if any(dspy.evaluate.answer_exact_match_str(hops[idx], hops[:idx], frac=0.8) for idx in range(2, len(hops))):
            return False

        return True
    except Exception as e:
        print(f"Error during validation: {e}")
        print(f"Example: {example}, Prediction: {pred}, Trace: {trace}")
        return False

# Ask a question to the RAG program
my_question = "How many storeys are in the castle that David Gregory inherited?"

# Compile the model for evaluation
teleprompter = BootstrapFewShot(metric=validate_context_and_answer_and_hops)
compiled_baleen = teleprompter.compile(SimplifiedBaleen(), teacher=SimplifiedBaleen(passages_per_hop=2), trainset=trainset)
pred = compiled_baleen(my_question)

# Define metric to check if we retrieved the correct documents
def gold_passages_retrieved(example, pred, trace=None):
    gold_titles = set(map(dspy.evaluate.normalize_text, example["gold_titles"]))
    found_titles = set(
        map(dspy.evaluate.normalize_text, [c.split(" | ")[0] for c in pred.context])
    )
    return gold_titles.issubset(found_titles)

# Set up the evaluate_on_hotpotqa function. We'll use this many times below.
evaluate_on_hotpotqa = Evaluate(devset=devset, num_threads=1, display_progress=True, display_table=5)
compiled_baleen_retrieval_score = evaluate_on_hotpotqa(compiled_baleen, metric=gold_passages_retrieved)

# Print the results
print(f"Number of topk errors: {counter}")
print(f"## Retrieval Score for compiled Baleen: {compiled_baleen_retrieval_score}")