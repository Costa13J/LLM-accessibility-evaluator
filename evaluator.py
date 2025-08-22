import dspy
from dspy.dsp.utils import deduplicate
from dspy.teleprompt import BootstrapFewShot
from llm_signatures import EvaluateInteractiveCues, GenerateSearchQuery, EvaluateErrorIdentification
from constants import FALLBACK_QUERIES_MAP
from trainsets import trainset, trainset_no_submit
from trainsets_error import trainset_error_identification, trainset_error_identification_no_submit
from interaction import SuggestInvalidInputsForTesting, get_invalid_inputs_for_fields

class InteractiveCuesEvaluator(dspy.Module):  
    def __init__(self, passages_per_hop=3, max_hops=2, evaluation_mode="wcag-3.3.1"):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_cues = dspy.ChainOfThought(EvaluateErrorIdentification) # Change this for different issues
        self.max_hops = max_hops
        self.evaluation_mode = evaluation_mode

    #Formats mutation records into a structured text summary
    def process_mutations(self, mutations):
        if not mutations:
            return "No dynamic changes detected after form interaction."

        summary = []

        def format_css_for_llm(m):
            props = m.get("computedColorStyles", []) + m.get("colorProperties", [])
            if props:
                return f"CSS Visual Cues: {', '.join(props)}"
            return ""

        for m in mutations:
            if not isinstance(m, dict):
                summary.append(f"[Warning] Unexpected mutation format: {m}")
                continue  # skip invalid mutation entries

            field_label = m.get("fieldLabel", "")
            field_name = m.get("fieldName", "")
            field_info = f" (Field: '{field_label}' | name='{field_name}')" if field_label or field_name else ""

            target_tag = m.get('targetTag', '?')
            target_id = m.get('targetId', '')
            target = f"<{target_tag}>#{target_id}" if target_id else f"<{target_tag}>"

            # Log color-based visual cues 
            color_props = m.get("colorProperties", [])
            if (color_props or error_classes) and not m.get("validationFlag"):
                summary.append(f"[SC 1.4.1] Potential failure: visual change ({', '.join(color_props + error_classes)}) without semantic support (e.g., no ARIA or error message).")


            style_cues = m.get("computedColorStyles", [])
            if style_cues:
                summary.append(f"[Computed Style Cue] {target} rendered with: {', '.join(style_cues)}{field_info}")

            css_desc = format_css_for_llm(m)
            if css_desc:
                summary.append(f"[CSS Style Summary] {target}: {css_desc}{field_info}")


            error_classes = m.get("errorClasses", [])
            if error_classes:
                summary.append(f"[Style Class Applied] {target} received error-related class(es): {', '.join(error_classes)}{field_info}")

            if (color_props or error_classes) and not m.get("validationFlag"):
                summary.append(f"[Warning] Color or class-based visual cue detected without semantic support (e.g., no ARIA or text message).")

            

            warning_notes = []

            if m.get("attributeChanged") == "aria-invalid" and m.get("newValue") == "true":
                summary.append(f"[ARIA Invalid] {target} marked as invalid")

            for msg in m.get("possibleErrorMessages", []):
                if field_label or field_name:
                    summary.append(f"[Linked Error Message] {msg} for field '{field_label or field_name}'")
                else:
                    summary.append(f"[Unlinked Error Message] {msg} (not associated with any field)")


            if m.get("type") == "attributes":
                attr = m.get("attributeChanged")
                val = m.get("newValue")
                note = "Validation-related attribute changed." if m.get("validationFlag") else ""

                if attr in ["style", "class"] and not m.get("validationFlag"):
                    warning_notes.append("Style change not accompanied by semantic cues (e.g., ARIA).")

                if attr in ["aria-invalid", "aria-describedby"]:
                    note = "Semantic attribute updated."

                for msg in m.get("possibleErrorMessages", []):
                    summary.append(f"[Message Revealed] {msg}{field_info}")
                    if not field_label and not field_name:
                        warning_notes.append("Unlinked message: not programmatically associated with any input field.")

                summary.append(f"[Attribute Change] {target} → '{attr}' updated to '{val}'{field_info}. {note}".strip())
                if warning_notes:
                    for w in warning_notes:
                        summary.append(f"[Warning] {w}")

            elif m.get("type") == "childList":
                added = m.get("addedNodes", [])
                removed = m.get("removedNodes", [])
                messages = m.get("possibleErrorMessages", [])

                for msg in messages:
                    summary.append(f"[Visible Message] {msg}{field_info}")
                    if not field_label and not field_name:
                        summary.append(f"[Warning] Message not programmatically linked to any input field.")

                for node_html in added:
                    snippet = node_html.strip().replace("\n", " ")[:200]
                    summary.append(f"[DOM Node Added] Snippet: {snippet}...{field_info}")

                for node_html in removed:
                    snippet = node_html.strip().replace("\n", " ")[:200]
                    summary.append(f"[DOM Node Removed] Snippet: {snippet}...{field_info}")

        cleaned_summary = deduplicate(summary)
        return "\n".join(cleaned_summary)


    def forward(self, html_snippet_before, mutations, retrieved_guidelines=None, invalid_inputs=None, interaction_type=None):
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet_before).query
                queries.add(query)
                
                passages = self.retrieve(query).passages
                if not passages:
                    for fallback in FALLBACK_QUERIES_MAP.get(self.evaluation_mode, []):
                        passages = self.retrieve(fallback).passages
                        print(f"Used fallback: {fallback}")
                        if passages:
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                continue

        mutation_summary = self.process_mutations(mutations) if mutations else "No form interaction or dynamic changes to analyze."

        if invalid_inputs is not None and interaction_type is not None:
            pred = self.evaluate(
                html_snippet_before=html_snippet_before,
                mutations=mutations or "No form interaction or dynamic changes to analyze.",
                retrieved_guidelines=retrieved_guidelines,
                invalid_inputs=invalid_inputs,
                interaction_type=interaction_type
            )
        elif invalid_inputs is not None:
            pred = self.evaluate(
                html_snippet_before=html_snippet_before,
                mutations=mutations or "No form interaction or dynamic changes to analyze.",
                retrieved_guidelines=retrieved_guidelines,
                invalid_inputs=invalid_inputs
            )
        elif interaction_type is not None:
            pred = self.evaluate(
                html_snippet_before=html_snippet_before,
                mutations=mutations or "No form interaction or dynamic changes to analyze.",
                retrieved_guidelines=retrieved_guidelines,
                interaction_type=interaction_type
            )
        else:
            pred = self.evaluate(
                html_snippet_before=html_snippet_before,
                mutations=mutations or "No form interaction or dynamic changes to analyze.",
                retrieved_guidelines=retrieved_guidelines
            )



        return dspy.Prediction(
            retrieved_guidelines=retrieved_guidelines,
            evaluation=pred.evaluation,
            identification=pred.identification,
            reasoning=pred.reasoning,
            format=pred.format,
            mutation_summary=mutation_summary,
            queries=list(queries)
        )
    
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
    if evaluation_mode == "3.3.3":
        if invalid_inputs is None:
            llm = dspy.Predict(SuggestInvalidInputsForTesting)
            invalid_inputs = get_invalid_inputs_for_fields(html_before["fields"], llm=llm)

        return compiled(
            html_snippet_before=formatted_html,
            mutations=mutations,
            invalid_inputs=invalid_inputs,
        )
    elif evaluation_mode == "1.4.1":
        return compiled(
            html_snippet_before=html_before,
            mutations=mutations,
            interaction_type=interaction_type, 
            invalid_inputs=invalid_inputs or [],  
        )

    else:
        return compiled(
            html_snippet_before=formatted_html,
            mutations=mutations,
        )

