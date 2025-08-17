import dspy

trainset_color = [

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


    dspy.Example(
        html_snippet_before="""
<label for='name' style='color: red;'>Name</label>
<input id='name' name='name'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'name', 'value': 'abc'}]",
        mutations="[ComputedStyle] <label for='name'> color: red (error state)",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
        identification="name",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("fail")""",
        reasoning="""Error cue: label turned red for invalid input, no programmatic error message or text provided. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): name
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("fail")
-Reasoning(explanation of the evaluation result): Error cue: label turned red for invalid input, no programmatic error message or text provided. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 2 PASS + PASS: Proper required cue (asterisk + text), proper error cue (color + text)
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

        
    dspy.Example(
        html_snippet_before="""
<label for='email'>Email <span style='color: red'>*</span> (required)</label>
<input id='email' type='email'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'email', 'value': 'abc@abc'}]",
        mutations="""[ComputedStyle] <label for='email'> color: red (error state)
[Text Added] 'Enter a valid email' after invalid input""",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
        identification="email",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")""",
        reasoning="""Error cue: red color combined with specific text message 'Enter a valid email' ensures error state is not color-only. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): email
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")
-Reasoning(explanation of the evaluation result): Error cue: red color combined with specific text message 'Enter a valid email' ensures error state is not color-only. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 3 INAPPLICABLE + INAPPLICABLE: Optional field, no required or error cues
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


    dspy.Example(
        html_snippet_before="""
<label for='comment'>Comment</label>
<textarea id='comment'></textarea>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'comment', 'value': 'abc'}]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: Criterion not applicable if field is not required and no cues shown.",
        identification="comment",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Error cue: none present. Field is optional and no error validation is triggered, so error evaluation is inapplicable. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): comment
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Error cue: none present. Field is optional and no error validation is triggered, so error evaluation is inapplicable. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 4 FAIL + FAIL: Required & error cues both border-color only
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

    dspy.Example(
        html_snippet_before="""
<label for='dob'>Date of Birth</label>
<input id='dob' type='date' style='border-color: red;'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'dob', 'value': '2025-13-40'}]",
        mutations="""No additional validation mutations detected after submit.
[Static Styling] <input>#dob has inline border-color:red before interaction.
[No Programmatic Error State] aria-invalid not set; no aria-describedby/role=alert; no error text added.""",
        retrieved_guidelines="WCAG 1.4.1: Only evaluate an error cue if a validation error is actually triggered; inapplicable if no error state is presented.",
        identification="dob",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Test input '2025-13-40' was submitted. The red border is a pre-existing inline style and did not change as a result of validation. No programmatic error signal (e.g., aria-invalid) and no error message appeared, so no error state was actually presented to the user. Because this interaction evaluates ERROR cues and none were triggered, the correct classification is inapplicable (not a color-only failure). Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): dob
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Test input '2025-13-40' was submitted. The red border is static pre-interaction styling; no aria-invalid/aria-describedby or error message was added. Since no validation error was presented, this is inapplicable for error cues, not a color-only failure. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 5 PASS + PASS: Proper required cue, proper error cue with guidance
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


    dspy.Example(
        html_snippet_before="""
<label for='password'>Password <span style='color:red'>*</span> (required)</label>
<input id='password' type='password'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'password', 'value': '123'}]",
        mutations="""[ComputedStyle] <label for='password'> color: red (error state)
[Text Added] 'Password must be at least 8 characters' after invalid input""",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
        identification="password",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")""",
        reasoning="""Error cue: red color accompanied by specific password guidance text ensures error state is not conveyed by color alone. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): password
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")
-Reasoning(explanation of the evaluation result): Error cue: red color accompanied by specific password guidance text ensures error state is not conveyed by color alone. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),




    # 6 FAIL + INAPPLICABLE: Required cue color-only, no error cue shown
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


    dspy.Example(
        html_snippet_before="""
<label for='username' style='color:red;'>Username</label>
<input id='username' type='text'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'username', 'value': 'abc'}]",
        mutations="[No error state detected]",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
        identification="username",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Error cue: none shown for invalid input, so error evaluation is inapplicable. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): username
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Error cue: none shown for invalid input, so error evaluation is inapplicable. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),





    # 7 PASS + PASS: No required cue, proper error cue with text
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


    dspy.Example(
        html_snippet_before="""
<label for='zip'>ZIP Code</label>
<input id='zip' type='text'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'zip', 'value': '000'}]",
        mutations="[Text Added] 'Invalid ZIP code' after invalid input",
        retrieved_guidelines="WCAG 1.4.1: Provide text or semantic cues along with color changes.",
        identification="zip",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")""",
        reasoning="""Error cue: text message 'Invalid ZIP code' is provided and programmatically associated, so error state is not conveyed by color alone. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): zip
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")
-Reasoning(explanation of the evaluation result): Error cue: text message 'Invalid ZIP code' is provided and programmatically associated, so error state is not conveyed by color alone. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 8 PASS + FAIL: Proper required cue, error cue color-only
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


     dspy.Example(
        html_snippet_before="""
<label for='phone'>Phone Number</label>
<input id='phone' type='tel'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'phone', 'value': 'abc'}]",
        mutations="""[ComputedStyle] <label for='phone'> color: red (error state)
[No additional error message provided]""",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
        identification="phone",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("fail")""",
        reasoning="""Error cue: invalid input only indicated by red text styling, no error message or semantic association provided. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): phone
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("fail")
-Reasoning(explanation of the evaluation result): Error cue: invalid input only indicated by red text styling, no error message or semantic association provided. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 9 PASS + PASS: Proper required cue, no error cue triggered
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

    dspy.Example(
        html_snippet_before="""
<label for='country'>Country <span style='color:red'>*</span></label>
<select id='country'></select>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'country', 'value': '??'}]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
        identification="country",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Error cue: no error validation triggered for invalid input, so error evaluation is inapplicable. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): country
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Error cue: no error validation triggered for invalid input, so error evaluation is inapplicable. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



        # 10 FAIL + FAIL: Required & error cues both color-only (label turns red)
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

    dspy.Example(
        html_snippet_before="""
<label for='city' style='color:red;'>City</label>
<input id='city'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'city', 'value': '123'}]",
        mutations="""No additional validation mutations detected after submit.
[Static Styling] <label for='city'> is red via inline style before interaction.
[No Programmatic Error State] aria-invalid not set on input; no message or association added.""",
        retrieved_guidelines="WCAG 1.4.1: Error-cue evaluation is only applicable when an error state is presented; static color unrelated to validation is not an error cue.",
        identification="city",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Test input '123' was submitted. The label’s red color is static, defined inline before any interaction. The submission did not trigger a validation state: no aria-invalid, no linked message (aria-describedby/role=alert), and no new visual change attributable to validation. Therefore, no error cue was presented and the correct classification is inapplicable for the error evaluation. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): city
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): The label was already red (static styling) and did not change on submit; no aria-invalid or error text appeared. Since no validation error was presented, error evaluation is inapplicable, not a color-only failure. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 11 INAPPLICABLE + INAPPLICABLE: Optional file input
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

    dspy.Example(
        html_snippet_before="""
<label for='file'>Upload File</label>
<input id='file' type='file'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'file', 'value': 'abc.txt'}]",
        mutations="No visual or semantic changes detected.",
        retrieved_guidelines="WCAG 1.4.1: No cues needed for optional fields.",
        identification="file",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Error cue: none present. Field is optional and no validation triggered, so error evaluation is inapplicable. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): file
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Error cue: none present. Field is optional and no validation triggered, so error evaluation is inapplicable. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 12 PASS + PASS: No required cue, proper error cue with border + text
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

    dspy.Example(
        html_snippet_before="""
<label for='state'>State</label>
<input id='state'>
""",
        interaction_type="invalid_input_submit",
        invalid_inputs="[{'field': 'state', 'value': '??'}]",
        mutations="""[ComputedStyle] <input>#state border-color: red (error state)
[Text Added] 'Invalid state name' after invalid input""",
        retrieved_guidelines="WCAG 1.4.1: Provide text or semantic cues along with color changes.",
        identification="state",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")""",
        reasoning="""Error cue: invalid state marked with red border and explanatory text 'Invalid state name', so error state is not conveyed by color alone. Required cue: not applicable in this pass.""",
        format="""-Identification(label or name of the field): state
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("pass")
-Reasoning(explanation of the evaluation result): Error cue: invalid state marked with red border and explanatory text 'Invalid state name', so error state is not conveyed by color alone. Required cue: not applicable in this pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

]


trainset_color_no_submit = [

    # 1 FAIL + FAIL: Required & error cues both color-only, unlinked message
    dspy.Example(
        html_snippet_before="""
<label for="email">Email</label>
<input id="email" style="border: 2px solid red;" class="error">
<span style="color: red;">Required</span>
""",
        interaction_type="no_submit",
        invalid_inputs="[]",
        mutations="""[ComputedStyle] <input>#email border-color: red
[Visible Message] 'Required' (not programmatically linked)
[No aria attributes or other semantic indicators detected]""",
        retrieved_guidelines="WCAG 1.4.1: Do not rely on color alone to indicate required or error state information.",
        identification="email",
        evaluation="""-Required Cue Evaluation("fail")
-Error Cue Evaluation("fail")""",
        reasoning="""Required cue: red border and red text 'Required', but the message is not programmatically linked and no semantic attributes are present. Error cue: same color-only styling with no semantic support.""",
        format="""-Identification(label or name of the field): email
-Required Cue Evaluation("fail")
-Error Cue Evaluation("fail")
-Reasoning(explanation of the evaluation result): Required cue: red border and red text 'Required', but the message is not programmatically linked and no semantic attributes are present. Error cue: same color-only styling with no semantic support."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 2 PASS + FAIL: Proper required cue (aria-required + asterisk), error cue color-only
    dspy.Example(
        html_snippet_before="""
<label for="zip">ZIP <span aria-hidden="true">*</span></label>
<input id="zip" aria-required="true" style="border: 2px solid red;">
""",
        interaction_type="no_submit",
        invalid_inputs="[]",
        mutations="""[ARIA Attribute] <input>#zip aria-required="true"
[ComputedStyle] <input>#zip border-color: red (error state)
[No error message or semantic error indicators detected]""",
        retrieved_guidelines="WCAG 1.4.1: Use semantic or textual cues in addition to color for both required and error states.",
        identification="zip",
        evaluation="""-Required Cue Evaluation("pass")
-Error Cue Evaluation("fail")""",
        reasoning="""Required cue: visible asterisk plus aria-required attribute. Error cue: only a red border is used, with no associated text or semantic indicators, so it fails.""",
        format="""-Identification(label or name of the field): zip
-Required Cue Evaluation("pass")
-Error Cue Evaluation("fail")
-Reasoning(explanation of the evaluation result): Required cue: visible asterisk plus aria-required attribute. Error cue: only a red border is used, with no associated text or semantic indicators, so it fails."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 3 PASS + PASS: Proper required cue (aria-required), proper error cue (aria-invalid + linked message)
    dspy.Example(
        html_snippet_before="""
<label for="password">Password *</label>
<input id="password" aria-required="true" aria-invalid="true" aria-describedby="pw-err">
<div id="pw-err" class="error" role="alert">Must be 8+ characters</div>
""",
        interaction_type="no_submit",
        invalid_inputs="[]",
        mutations="""[ARIA Attribute] <input>#password aria-required="true"
[ARIA Attribute] <input>#password aria-invalid="true"
[Linked Error Message] 'Must be 8+ characters' linked via aria-describedby""",
        retrieved_guidelines="WCAG 1.4.1: Provide semantic cues such as aria-required and aria-invalid with linked error messages.",
        identification="password",
        evaluation="""-Required Cue Evaluation("pass")
-Error Cue Evaluation("pass")""",
        reasoning="""Required cue: visible asterisk and aria-required attribute. Error cue: aria-invalid and a linked error message ensure the cue is not color-only.""",
        format="""-Identification(label or name of the field): password
-Required Cue Evaluation("pass")
-Error Cue Evaluation("pass")
-Reasoning(explanation of the evaluation result): Required cue: visible asterisk and aria-required attribute. Error cue: aria-invalid and a linked error message ensure the cue is not color-only."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 4 INAPPLICABLE + INAPPLICABLE: Optional field with no cues
    dspy.Example(
        html_snippet_before="""
<label for="nickname">Nickname (optional)</label>
<input id="nickname">
""",
        interaction_type="no_submit",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected after interaction.",
        retrieved_guidelines="WCAG 1.4.1: No required or error cues are needed for optional fields without validation.",
        identification="nickname",
        evaluation="""-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")""",
        reasoning="""Field is optional, and no required or error cues were detected. Criterion not applicable.""",
        format="""-Identification(label or name of the field): nickname
-Required Cue Evaluation("inapplicable")
-Error Cue Evaluation("inapplicable")
-Reasoning(explanation of the evaluation result): Field is optional, and no required or error cues were detected. Criterion not applicable."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),
]

