import dspy
from dspy.dsp.utils import deduplicate
from dspy.teleprompt import BootstrapFewShot
from llm_signatures import EvaluateInteractiveCues, GenerateSearchQuery, EvaluateErrorIdentification
from constants import FALLBACK_QUERIES, FALLBACK_QUERIES_ERROR_IDENTIFICATION
from trainsets import trainset, trainset_no_submit

class InteractiveCuesEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=3, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_cues = dspy.ChainOfThought(EvaluateErrorIdentification) # Change this for different issues
        self.max_hops = max_hops

    #Formats mutation records into a structured text summary
    def process_mutations(self, mutations):
        if not mutations:
            return "No dynamic changes detected after form interaction."

        summary = []

        for m in mutations:
            if not isinstance(m, dict):
                summary.append(f"[Warning] Unexpected mutation format: {m}")
                continue  # skip invalid mutation entries

            target_tag = m.get('targetTag', '?')
            target_id = m.get('targetId', '')
            target = f"<{target_tag}>#{target_id}" if target_id else f"<{target_tag}>"

            field_label = m.get("fieldLabel", "")
            field_name = m.get("fieldName", "")
            field_info = f" (Field: '{field_label}' | name='{field_name}')" if field_label or field_name else ""

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


    def forward(self, html_snippet_before, mutations, retrieved_guidelines=None):
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet_before).query
                queries.add(query)
                
                passages = self.retrieve(query).passages
                if not passages:
                    for fallback in FALLBACK_QUERIES_ERROR_IDENTIFICATION:
                        passages = self.retrieve(fallback).passages
                        print("used fallback")
                        if passages:
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                continue

        mutation_summary = self.process_mutations(mutations) if mutations else "No form interaction or dynamic changes to analyze."

        pred = self.evaluate_cues(
            html_snippet_before=html_snippet_before,
            mutations=mutation_summary,
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
    
def run_evaluation(html_before, mutations, url, submit_clicked):
    teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
    evaluator = InteractiveCuesEvaluator(passages_per_hop=2)
    compiled = teleprompter.compile(evaluator, teacher=evaluator, trainset=(trainset if submit_clicked else trainset_no_submit))

    formatted_html = "\n".join(
        [
            f"{f['label']} ({f['type']}): required={f['required']}, disabled={f['disabled']}, readonly={f['readonly']}, autocomplete={f['autocomplete']}"
            for f in html_before["fields"]
        ]
    )
    return compiled(formatted_html, mutations)