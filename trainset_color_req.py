import dspy

trainset_color_req = [




    dspy.Example(
        html_snippet_before="""
<label for='name' style='color: red;'>Name</label>
<input id='name' name='name'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="[ComputedStyle] <label for='name'> color: red (required state)",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="name",
        evaluation="""-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: label turned red when empty, no supporting text or programmatic indicator. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): name
-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: label turned red when empty, no supporting text or programmatic indicator. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



        # 2 PASS: Proper required cue (asterisk + text), proper error cue (color + text)
    dspy.Example(
        html_snippet_before="""
<label for='email'>Email <span style='color: red'>*</span> (required)</label>
<input id='email' type='email'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="""[ComputedStyle] <label for='email'> color: red (required state)
[Text Added] '(required)' to label""",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="email",
        evaluation="""-Required Cue Evaluation("pass")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: red asterisk plus '(required)' text provide programmatic/textual indicators beyond color. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): email
-Required Cue Evaluation("pass")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: red asterisk plus '(required)' text provide programmatic/textual indicators beyond color. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

# 3 INAPPLICABLE: Optional field, no required or error cues
        dspy.Example(
        html_snippet_before="""
<label for='comment'>Comment</label>
<textarea id='comment'></textarea>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: Criterion not applicable if field is not required and no cues shown.",
        identification="comment",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: none present. Field is optional, so required evaluation is inapplicable. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): comment
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: none present. Field is optional, so required evaluation is inapplicable. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 4 FAIL: Required & error cues both border-color only
    dspy.Example(
        html_snippet_before="""
<label for='dob'>Date of Birth</label>
<input id='dob' type='date' style='border-color: red;'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="[ComputedStyle] <input>#dob border-color: red (required state)",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="dob",
        evaluation="""-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: border turned red when left empty, no programmatic or textual support (e.g., aria-required, visible text). Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): dob
-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: border turned red when left empty, no programmatic or textual support (e.g., aria-required, visible text). Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 5 PASS : Proper required cue, proper error cue with guidance
    dspy.Example(
        html_snippet_before="""
<label for='password'>Password <span style='color:red'>*</span> (required)</label>
<input id='password' type='password'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="""[ComputedStyle] <label for='password'> color: red (required state)
[Text Added] '(required)' to label""",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="password",
        evaluation="""-Required Cue Evaluation("pass")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: red asterisk plus '(required)' text provide clear programmatic/textual indication beyond color. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): password
-Required Cue Evaluation("pass")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: red asterisk plus '(required)' text provide clear programmatic/textual indication beyond color. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 6 FAIL: Required cue color-only, no error cue shown
    dspy.Example(
        html_snippet_before="""
<label for='username' style='color:red;'>Username</label>
<input id='username' type='text'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="[ComputedStyle] <label for='username'> color: red (required state)",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="username",
        evaluation="""-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: label turned red when empty, no supporting text or programmatic indicator. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): username
-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: label turned red when empty, no supporting text or programmatic indicator. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 7 PASS: No required cue, proper error cue with text
    dspy.Example(
        html_snippet_before="""
<label for='zip'>ZIP Code</label>
<input id='zip' type='text'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: No required cues are needed for optional fields without validation.",
        identification="zip",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: field is not marked as required, so required evaluation is inapplicable. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): zip
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: field is not marked as required, so required evaluation is inapplicable. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 8 PASS : Proper required cue, error cue color-only
    dspy.Example(
        html_snippet_before="""
<label for='phone'>Phone Number</label>
<input id='phone' type='tel'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: No required cues are needed for optional fields without validation.",
        identification="phone",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: field is not marked as required, so required evaluation is inapplicable. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): phone
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: field is not marked as required, so required evaluation is inapplicable. Error cue: not applicable in this pass."""
     ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

     # 9 PASS: Proper required cue, no error cue triggered
    dspy.Example(
        html_snippet_before="""
<label for='country'>Country <span style='color:red'>*</span></label>
<select id='country'></select>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="[Text Added] '(required)' to label",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="country",
        evaluation="""-Required Cue Evaluation("pass")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: asterisk plus '(required)' text provide a non-color indicator. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): country
-Required Cue Evaluation("pass")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: asterisk plus '(required)' text provide a non-color indicator. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 10 FAIL : Required & error cues both color-only (label turns red)
    dspy.Example(
        html_snippet_before="""
<label for='city' style='color:red;'>City</label>
<input id='city'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="[ComputedStyle] <label for='city'> color: red (required state)",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate required state information.",
        identification="city",
        evaluation="""-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: label turned red when left empty, no text or programmatic indicator. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): city
-Required Cue Evaluation("fail")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: label turned red when left empty, no text or programmatic indicator. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 11 INAPPLICABLE: Optional file input
    dspy.Example(
        html_snippet_before="""
<label for='file'>Upload File</label>
<input id='file' type='file'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: No cues needed for optional fields.",
        identification="file",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: none present. Field is optional, so required evaluation is inapplicable. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): file
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: none present. Field is optional, so required evaluation is inapplicable. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 12 PASS: No required cue, proper error cue with border + text
    dspy.Example(
        html_snippet_before="""
<label for='state'>State</label>
<input id='state'>
""",
        interaction_type="empty_submit",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: No required cues are needed for optional fields without validation.",
        identification="state",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Required cue: none present. Field not marked as required, so required evaluation is inapplicable. Error cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): state
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Required cue: none present. Field not marked as required, so required evaluation is inapplicable. Error cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

]