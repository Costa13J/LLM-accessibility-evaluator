import dspy
from dspy.dsp.utils import deduplicate
from interaction import SuggestInvalidInputsForTesting, get_invalid_inputs_for_fields

    
def run_evaluation(html_before, mutations, url, submit_clicked, evaluation_mode="wcag-3.3.1", invalid_inputs=None, interaction_type=None):
    from dspy.teleprompt import BootstrapFewShot

    if evaluation_mode == "required":
        from llm_signatures import EvaluateInteractiveCues, GenerateSearchQuery as GenerateSearchRequired
        from trainsets import trainset, trainset_no_submit
        signature_cls = EvaluateInteractiveCues
        search_query_cls = GenerateSearchRequired
        selected_trainset = trainset if submit_clicked else trainset_no_submit 

    elif evaluation_mode == "wcag-3.3.1":
        from llm_signatures import EvaluateErrorIdentification, GenerateSearchQuery as GenerateSearchError
        from trainsets_error import trainset_error_identification, trainset_error_identification_no_submit
        signature_cls = EvaluateErrorIdentification
        search_query_cls = GenerateSearchError
        selected_trainset = trainset_error_identification if submit_clicked else trainset_error_identification_no_submit

    elif evaluation_mode == "3.3.3":
        from llm_signatures import EvaluateErrorClarity, GenerateSearchQueryErrorClarity
        from trainsets_error_clarity import trainset_error_clarity, trainset_error_suggestion_no_submit
        signature_cls = EvaluateErrorClarity
        search_query_cls = GenerateSearchQueryErrorClarity
        selected_trainset = trainset_error_clarity if submit_clicked else trainset_error_suggestion_no_submit

    elif evaluation_mode == "1.4.1":
        from llm_signatures import EvaluateUseOfColor, GenerateSearchQueryUseOfColor
        from trainset_color_errorstate import trainset_color_errorstate, trainset_color_no_submit 
        signature_cls = EvaluateUseOfColor
        search_query_cls = GenerateSearchQueryUseOfColor
        selected_trainset = trainset_color_errorstate if submit_clicked else trainset_color_no_submit  #no submit is fallback

    else:
        raise ValueError(f"Unsupported evaluation_mode: {evaluation_mode}")

    class DynamicEvaluator(dspy.Module):
        def __init__(self, evaluate_signature, search_query_signature, passages_per_hop=2, max_hops=2):
            super().__init__()
            self.generate_query = [dspy.ChainOfThought(search_query_signature) for _ in range(max_hops)]
            self.retrieve = dspy.Retrieve(k=passages_per_hop)
            self.evaluate = dspy.ChainOfThought(evaluate_signature)
            self.max_hops = max_hops

        def forward(self, html_snippet_before, mutations, retrieved_guidelines=None, invalid_inputs=None, interaction_type=None):
            retrieved_guidelines = []
            queries = set()

            for hop in range(self.max_hops):
                try:
                    query = self.generate_query[hop](html_snippet=html_snippet_before).query
                    queries.add(query)

                    passages = self.retrieve(query).passages
                    if not passages:
                        print("No passages retrieved. Using fallback.")
                        passages = []  

                    retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
                except Exception as e:
                    print(f"[Hop {hop+1}] Retrieval error: {e}")
                    continue

            eval_kwargs = {
                "html_snippet_before": html_snippet_before,
                "mutations": mutations or "No form interaction or dynamic changes to analyze.",
                "retrieved_guidelines": retrieved_guidelines
            }
            if invalid_inputs is not None:
                eval_kwargs["invalid_inputs"] = invalid_inputs
            if interaction_type is not None:
                eval_kwargs["interaction_type"] = interaction_type

            pred = self.evaluate(**eval_kwargs)

            print("[DEBUG LLM RAW OUTPUT]")
            print(pred)


            return dspy.Prediction(
                retrieved_guidelines=retrieved_guidelines,
                evaluation=pred.evaluation,
                identification=pred.identification,
                reasoning=pred.reasoning,
                format=pred.format,
                queries=list(queries)
            )

    evaluator = DynamicEvaluator(signature_cls, search_query_cls)
    teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "pass" in pred.evaluation.lower())
    compiled = teleprompter.compile(evaluator, teacher=evaluator, trainset=selected_trainset)

    formatted_html = "\n".join(
        [
            f"{f['label']} ({f['type']}): required={f['required']}, disabled={f['disabled']}, readonly={f['readonly']}, autocomplete={f['autocomplete']}"
            for f in html_before["fields"]
        ]
    )
    print(formatted_html)
    if evaluation_mode in ["3.3.3", "1.4.1"]:
        if invalid_inputs is None:
            llm = dspy.Predict(SuggestInvalidInputsForTesting)
            invalid_inputs = get_invalid_inputs_for_fields(html_before["fields"], llm=llm)

        return compiled(
            html_snippet_before=formatted_html,
            mutations=mutations,
            invalid_inputs=invalid_inputs,
        )

    else:
        return compiled(
            html_snippet_before=formatted_html,
            mutations=mutations,
        )

