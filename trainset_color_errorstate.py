import dspy

trainset_color_errorstate = [


#12 PASS: Required error shown with text
dspy.Example(
    html_snippet_before="""
<label for='email'>Email <span style='color: red'>*</span></label>
<input id='email' type='email'>
""",
    interaction_type="empty_submit",
    invalid_inputs="[]",
    mutations="[Text Added] 'Email is required' after submit",
    retrieved_guidelines="WCAG 1.4.1: Provide textual error messages in addition to color.",
    identification="email",
    evaluation="pass",
    reasoning="""Submitting with the field empty triggered an error state where a clear message 'Email is required' was displayed. This ensures the error is not conveyed by color alone, so it passes.""",
    format="""-Identification(label or name of the field): email
-Evaluation: pass
-Reasoning(explanation of the evaluation result): Submitting with the field empty triggered an error state where a clear message 'Email is required' was displayed. This ensures the error is not conveyed by color alone, so it passes."""
).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


#13 INAPPLICABLE: Optional field, no error triggered
dspy.Example(
    html_snippet_before="""
<label for='comment'>Comment</label>
<textarea id='comment'></textarea>
""",
    interaction_type="empty_submit",
    invalid_inputs="[]",
    mutations="No visual or semantic changes detected.",
    retrieved_guidelines="WCAG 1.4.1: Error evaluation is inapplicable when no error state is triggered.",
    identification="comment",
    evaluation="inapplicable",
    reasoning="""Submitting with the optional field empty did not trigger any error cues. Since no error state was presented, evaluation is inapplicable.""",
    format="""-Identification(label or name of the field): comment
-Evaluation: inapplicable
-Reasoning(explanation of the evaluation result): Submitting with the optional field empty did not trigger any error cues. Since no error state was presented, evaluation is inapplicable."""
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
        evaluation="fail",
        reasoning="""The only change is the label turning red after invalid input. No aria-invalid attribute, no error text, and no programmatic association were detected. Since color alone is used, this fails WCAG 1.4.1.""",
        format="""-Identification(label or name of the field): name
-Evaluation: fail
-Reasoning(explanation of the evaluation result): The only change is the label turning red after invalid input. No aria-invalid attribute, no error text, and no programmatic association were detected. Since color alone is used, this fails WCAG 1.4.1."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 2 PASS: Proper required cue (asterisk + text), proper error cue (color + text)
        
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
        evaluation="pass",
        reasoning="""The label turns red, but also a visible error message 'Enter a valid email' is added and programmatically associated. Since the error is not conveyed by color alone, this passes.""",
        format="""-Identification(label or name of the field): email
-Evaluation: pass
-Reasoning(explanation of the evaluation result): The label turns red, but also a visible error message 'Enter a valid email' is added and programmatically associated. Since the error is not conveyed by color alone, this passes."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 3 INAPPLICABLE: Optional field, no required or error cues
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
        evaluation="inapplicable",
        reasoning="""The field is optional and accepts input without validation. No error cues (color, text, or semantic) were triggered. Since no error state occurred, this case is inapplicable.""",
        format="""-Identification(label or name of the field): comment
-Evaluation: inapplicable
-Reasoning(explanation of the evaluation result): The field is optional and accepts input without validation. No error cues (color, text, or semantic) were triggered. Since no error state occurred, this case is inapplicable."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


#14 PASS: Border + text error
dspy.Example(
    html_snippet_before="""
<label for='password'>Password</label>
<input id='password' type='password'>
""",
    interaction_type="empty_submit",
    invalid_inputs="[]",
    mutations="""[ComputedStyle] <input>#password border-color: red (error state)
[Text Added] 'Password is required' after empty submit""",
    retrieved_guidelines="WCAG 1.4.1: Error cues must not rely on color alone.",
    identification="password",
    evaluation="pass",
    reasoning="""The border turned red after empty submission, but a clear error message 'Password is required' was also displayed. Because the error state is supported with text, it does not rely on color alone and passes.""",
    format="""-Identification(label or name of the field): password
-Evaluation: pass
-Reasoning(explanation of the evaluation result): The border turned red after empty submission, but a clear error message 'Password is required' was also displayed. Because the error state is supported with text, it does not rely on color alone and passes."""
).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations",  "retrieved_guidelines"),

    
# 4 Inapplicable: Required & error cues both border-color only
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
        evaluation="inapplicable",
        reasoning="""The field had a static red border before interaction, and no validation error was triggered (no aria-invalid, no error text). Since no new error cue was presented, this case is inapplicable.""",
        format="""-Identification(label or name of the field): dob
-Evaluation: inapplicable
-Reasoning(explanation of the evaluation result): The field had a static red border before interaction, and no validation error was triggered (no aria-invalid, no error text). Since no new error cue was presented, this case is inapplicable. """
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


#11 FAIL: Required error shown only with color
dspy.Example(
    html_snippet_before="""
<label for='name' style='color: red;'>Name</label>
<input id='name' name='name'>
""",
    interaction_type="empty_submit",
    invalid_inputs="[]",
    mutations="[ComputedStyle] <label for='name'> color: red (error state after empty submit)",
    retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error states.",
    identification="name",
    evaluation="fail",
    reasoning="""Submitting with the field empty triggered an error state where the label turned red. No aria-invalid, no error text, and no programmatic association were present. Error state relies only on color, so this fails.""",
    format="""-Identification(label or name of the field): name
-Evaluation: fail
-Reasoning(explanation of the evaluation result): Submitting with the field empty triggered an error state where the label turned red. No aria-invalid, no error text, and no programmatic association were present. Error state relies only on color, so this fails."""
).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),
    
# 5 PASS: Proper required cue, proper error cue with guidance

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
        evaluation="pass",
        reasoning="""The label turns red after invalid input, and a clear guidance message 'Password must be at least 8 characters' appears. The message provides textual support beyond color, so this passes.""",
        format="""-Identification(label or name of the field): password
- Evaluation: pass
-Reasoning(explanation of the evaluation result): The label turns red after invalid input, and a clear guidance message 'Password must be at least 8 characters' appears. The message provides textual support beyond color, so this passes."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 6 PASS : No required cue, proper error cue with text

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
        evaluation="pass",
        reasoning="""Submitting invalid input added the message 'Invalid ZIP code', programmatically linked to the field. No reliance on color styling was observed. This provides a clear error cue, so the result is a pass.""",
        format="""-Identification(label or name of the field): zip
-Evaluation: pass
-Reasoning(explanation of the evaluation result): Submitting invalid input added the message 'Invalid ZIP code', programmatically linked to the field. No reliance on color styling was observed. This provides a clear error cue, so the result is a pass."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 8 PASS: No required cue, proper error cue with border + text

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
        evaluation="pass",
        reasoning="""The input border turns red, but an explanatory message 'Invalid state name' is also added. The text provides semantic support, so the error is not conveyed by color alone, and this passes.""",
        format="""-Identification(label or name of the field): state
-Evaluation: pass
-Reasoning(explanation of the evaluation result): The input border turns red, but an explanatory message 'Invalid state name' is also added. The text provides semantic support, so the error is not conveyed by color alone, and this passes."""
    ).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),

    #9 FAIL: Border-only error (dynamic after invalid input)
    dspy.Example(
    html_snippet_before="""
<label for='age'>Age</label>
<input id='age' type='number'>
""",
    interaction_type="invalid_input_submit",
    invalid_inputs="[{'field': 'age', 'value': 'abc'}]",
    mutations="""[ComputedStyle] <input>#age border-color: red (error state)
[No error message or semantic attributes detected]""",
    retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
    identification="age",
    evaluation="fail",
    reasoning="""After invalid input, the only change was a red border around the field. No aria-invalid attribute, no descriptive text, and no programmatic association were provided. Since color alone indicates the error, this fails WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): age
-Evaluation: fail
-Reasoning(explanation of the evaluation result): After invalid input, the only change was a red border around the field. No aria-invalid attribute, no descriptive text, and no programmatic association were provided. Since color alone indicates the error, this fails WCAG 1.4.1."""
).with_inputs("html_snippet_before", "interaction_type", "invalid_inputs", "mutations", "retrieved_guidelines"),


    #10 Icon-only error (no text, no programmatic link)
    dspy.Example(
    html_snippet_before="""
<label for='phone2'>Phone Number</label>
<input id='phone2' type='tel'>
""",
    interaction_type="invalid_input_submit",
    invalid_inputs="[{'field': 'phone2', 'value': 'abcd'}]",
    mutations="""[Icon Added] Red exclamation icon displayed next to field
[No aria attributes, no descriptive text, no programmatic association]""",
    retrieved_guidelines="WCAG 1.4.1: Do not use icons or color alone to indicate error states without text or programmatic alternatives.",
    identification="phone2",
    evaluation="fail",
    reasoning="""An exclamation icon in red appeared after invalid input, but no text explanation or semantic link was provided (e.g., aria-describedby). Because the error is conveyed only by color/icon, this fails WCAG 1.4.1""",
    format="""-Identification(label or name of the field): phone2
-Evaluation: fail
-Reasoning(explanation of the evaluation result): An exclamation icon in red appeared after invalid input, but no text explanation or semantic link was provided (e.g., aria-describedby). Because the error is conveyed only by color/icon, this fails WCAG 1.4.1"""
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

