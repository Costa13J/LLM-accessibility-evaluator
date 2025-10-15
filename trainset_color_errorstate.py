import dspy

trainset_color_errorstate = [



    dspy.Example(
    html_snippet_before="""
<label for='name'>Name</label>
<input id='name' name='name' type='text'>
""",
    invalid_inputs="[{'field': 'name', 'value': ''}]",
    mutations="""[ComputedStyle] <input>#name border-color: red (error state)
[Style Class Applied] <input>#name received error-related class(es): gfield_error
[No Programmatic Support] aria-invalid not set; no aria-describedby or error message added.""",
    retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
    identification="name",
    evaluation="fail",
    reasoning="""After invalid input, the only changes were a red border and an error class applied to the field. No aria-invalid attribute, no descriptive text, and no programmatic association were detected. Since the error is indicated only through color, this fails WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): name
-Evaluation: fail
-Reasoning(explanation of the evaluation result): After invalid input, the only changes were a red border and an error class applied to the field. No aria-invalid attribute, no descriptive text, and no programmatic association were detected. Since the error is indicated only through color, this fails WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),




    # 2 PASS: Proper required cue (asterisk + text), proper error cue (color + text)
        
    dspy.Example(
    html_snippet_before="""
<label for='email'>Email</label>
<input id='email' type='email'>
""",
    invalid_inputs="[{'field': 'email', 'value': 'abc@abc'}]",
    mutations="""[ComputedStyle] <input>#email border-color: red (error state)
[Style Class Applied] <input>#email received error-related class(es): gfield_error
[Linked Error Message] 'Enter a valid email' associated with field 'email'""",
    retrieved_guidelines="WCAG 1.4.1: Provide text or semantic cues along with color changes.",
    identification="email",
    evaluation="pass",
    reasoning="""The border turns red and an error class is applied, but importantly a visible error message 'Enter a valid email' is added and programmatically associated with the field. Since the error is not conveyed by color alone, this passes WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): email
-Evaluation: pass
-Reasoning(explanation of the evaluation result): The border turns red and an error class is applied, but importantly a visible error message 'Enter a valid email' is added and programmatically associated with the field. Since the error is not conveyed by color alone, this passes WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 3 INAPPLICABLE: Optional field, no required or error cues
    dspy.Example(
    html_snippet_before="""
<label for='comment'>Comment (optional)</label>
<textarea id='comment'></textarea>
""",
    invalid_inputs="[{'field': 'comment', 'value': 'abc'}]",
    mutations="No visual or semantic changes detected after interaction.",
    retrieved_guidelines="WCAG 1.4.1: Criterion not applicable if field is optional and no validation cues are triggered.",
    identification="comment",
    evaluation="inapplicable",
    reasoning="""The field is optional and accepts input without validation. No error cues (color, text, or semantic) were triggered. Since no error state occurred, this case is inapplicable under WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): comment
-Evaluation: inapplicable
-Reasoning(explanation of the evaluation result): The field is optional and accepts input without validation. No error cues (color, text, or semantic) were triggered. Since no error state occurred, this case is inapplicable under WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),



    
# 4 Inapplicable: Required & error cues both border-color only
    dspy.Example(
    html_snippet_before="""
<label for='dob'>Date of Birth</label>
<input id='dob' type='date' style='border-color: red;'>
""",
    invalid_inputs="[{'field': 'dob', 'value': '2025-13-40'}]",
    mutations="""[Static Styling] <input>#dob has inline border-color:red before interaction
[No Programmatic Error State] aria-invalid not set; no aria-describedby or role=alert; no error text added
[No additional changes detected after input submission]""",
    retrieved_guidelines="WCAG 1.4.1: Only evaluate error cues if a validation error is actually triggered; static decoration without new error is inapplicable.",
    identification="dob",
    evaluation="inapplicable",
    reasoning="""The field had a red border from the start (static styling). After invalid input, no new semantic cues or error messages were triggered. Since no dynamic error cue occurred, this case is inapplicable for WCAG 1.4.1 evaluation.""",
    format="""-Identification(label or name of the field): dob
-Evaluation: inapplicable
-Reasoning(explanation of the evaluation result): The field had a red border from the start (static styling). After invalid input, no new semantic cues or error messages were triggered. Since no dynamic error cue occurred, this case is inapplicable for WCAG 1.4.1 evaluation."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


    
# 5 PASS: Proper required cue, proper error cue with guidance

    dspy.Example(
    html_snippet_before="""
<label for='password'>Password <span style='color:red'>*</span> (required)</label>
<input id='password' type='password'>
""",
    invalid_inputs="[{'field': 'password', 'value': '123'}]",
    mutations="""[ComputedStyle] <input>#password border-color: red (error state)
[Style Class Applied] <input>#password received error-related class(es): gfield_error
[Linked Error Message] 'Password must be at least 8 characters' associated with field 'password'""",
    retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
    identification="password",
    evaluation="pass",
    reasoning="""After invalid input, the password field border turns red and an error class is applied. Crucially, a descriptive message 'Password must be at least 8 characters' is added and programmatically associated with the field. Since the error is not conveyed by color alone, this passes WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): password
-Evaluation: pass
-Reasoning(explanation of the evaluation result): After invalid input, the password field border turns red and an error class is applied. Crucially, a descriptive message 'Password must be at least 8 characters' is added and programmatically associated with the field. Since the error is not conveyed by color alone, this passes WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 6 PASS : No required cue, proper error cue with text

    dspy.Example(
    html_snippet_before="""
<label for='zip'>ZIP Code</label>
<input id='zip' type='text'>
""",
    invalid_inputs="[{'field': 'zip', 'value': '000'}]",
    mutations="""[Linked Error Message] 'Invalid ZIP code' associated with field 'zip'
[ARIA Attribute] <input>#zip aria-invalid="true" """,
    retrieved_guidelines="WCAG 1.4.1: Provide text or semantic cues along with color changes.",
    identification="zip",
    evaluation="pass",
    reasoning="""Submitting invalid input added the message 'Invalid ZIP code', which is programmatically associated with the ZIP field via aria-invalid. Since the error is communicated with text and semantics, not color alone, this passes WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): zip
-Evaluation: pass
-Reasoning(explanation of the evaluation result): Submitting invalid input added the message 'Invalid ZIP code', which is programmatically associated with the ZIP field via aria-invalid. Since the error is communicated with text and semantics, not color alone, this passes WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


    #8 FAIL: Border-only error (dynamic after invalid input)
    dspy.Example(
    html_snippet_before="""
<label for='age'>Age</label>
<input id='age' type='number'>
""",
    invalid_inputs="[{'field': 'age', 'value': 'abc'}]",
    mutations="""[ComputedStyle] <input>#age border-color: red (error state)
[Style Class Applied] <input>#age received error-related class(es): gfield_error
[No Programmatic Support] aria-invalid not set; no aria-describedby; no error text displayed""",
    retrieved_guidelines="WCAG 1.4.1: Do not use color alone to indicate error state information.",
    identification="age",
    evaluation="fail",
    reasoning="""After invalid input, the only indicators were a red border and an error class applied to the field. No aria-invalid attribute, no linked error message, and no programmatic association were provided. Since the error is conveyed only through color, this fails WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): age
-Evaluation: fail
-Reasoning(explanation of the evaluation result): After invalid input, the only indicators were a red border and an error class applied to the field. No aria-invalid attribute, no linked error message, and no programmatic association were provided. Since the error is conveyed only through color, this fails WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),



    #9 Icon-only error (no text, no programmatic link)
    dspy.Example(
    html_snippet_before="""
<label for='phone2'>Phone Number</label>
<input id='phone2' type='tel'>
""",
    invalid_inputs="[{'field': 'phone2', 'value': 'abcd'}]",
    mutations="""[Icon Added] Red exclamation icon displayed next to <input>#phone2
[Style Class Applied] <input>#phone2 received error-related class(es): gfield_error
[No Programmatic Support] aria-invalid not set; no aria-describedby; no error text displayed""",
    retrieved_guidelines="WCAG 1.4.1: Do not use icons or color alone to indicate error states without text or programmatic alternatives.",
    identification="phone2",
    evaluation="fail",
    reasoning="""After invalid input, a red exclamation icon appeared next to the field and an error class was applied. However, no descriptive text or semantic attributes (aria-invalid, aria-describedby) were provided. Since the error is conveyed only through icon/color, this fails WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): phone2
-Evaluation: fail
-Reasoning(explanation of the evaluation result): After invalid input, a red exclamation icon appeared next to the field and an error class was applied. However, no descriptive text or semantic attributes (aria-invalid, aria-describedby) were provided. Since the error is conveyed only through icon/color, this fails WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),

    #7 PASS: No required cue, proper error cue with border + text

    dspy.Example(
    html_snippet_before="""
<label for='state'>State</label>
<input id='state'>
""",
    invalid_inputs="[{'field': 'state', 'value': '??'}]",
    mutations="""[ComputedStyle] <input>#state border-color: red (error state)
[Style Class Applied] <input>#state received error-related class(es): gfield_error
[Linked Error Message] 'Invalid state name' associated with field 'state'""",
    retrieved_guidelines="WCAG 1.4.1: Provide text or semantic cues along with color changes.",
    identification="state",
    evaluation="pass",
    reasoning="""The input border turns red and an error class is applied, but a descriptive error message 'Invalid state name' is also added and programmatically associated with the field. Since the error is not conveyed by color alone, this passes WCAG 1.4.1.""",
    format="""-Identification(label or name of the field): state
-Evaluation: pass
-Reasoning(explanation of the evaluation result): The input border turns red and an error class is applied, but a descriptive error message 'Invalid state name' is also added and programmatically associated with the field. Since the error is not conveyed by color alone, this passes WCAG 1.4.1."""
).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


]


trainset_color_no_submit = [

    # 1 FAIL - Required & error cues both rely on color only
    dspy.Example(
        html_snippet_before="""
<label for="email">Email</label>
<input id="email" style="border: 2px solid red;" class="error">
<span style="color: red;">Required</span>
""",
        invalid_inputs="[]",
        mutations="""[ComputedStyle] <input>#email border-color: red
[Visible Message] 'Required' (not programmatically linked)
[No aria attributes or other semantic indicators detected]""",
        retrieved_guidelines="WCAG 1.4.1: Do not rely on color alone to indicate required or error state information.",
        identification="email",
        evaluation="fail",
        reasoning="""Both the required and error cues depend solely on red color styling and an unlinked visible message. No semantic attributes or programmatic associations are present, so this fails WCAG 1.4.1.""",
        format="""-Identification(label or name of the field): email
-Evaluation: fail
-Reasoning(explanation of the evaluation result): Both the required and error cues depend solely on red color styling and an unlinked visible message. No semantic attributes or programmatic associations are present, so this fails WCAG 1.4.1."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 2 FAIL - Proper required cue, but error cue uses color only
    dspy.Example(
        html_snippet_before="""
<label for="zip">ZIP <span aria-hidden="true">*</span></label>
<input id="zip" aria-required="true" style="border: 2px solid red;">
""",
        invalid_inputs="[]",
        mutations="""[ARIA Attribute] <input>#zip aria-required="true"
[ComputedStyle] <input>#zip border-color: red (error state)
[No error message or semantic error indicators detected]""",
        retrieved_guidelines="WCAG 1.4.1: Use semantic or textual cues in addition to color for both required and error states.",
        identification="zip",
        evaluation="fail",
        reasoning="""The required cue is correctly implemented using both a visible asterisk and the aria-required attribute. However, the error cue relies solely on color (red border) with no associated text or semantic indicators, so this fails WCAG 1.4.1.""",
        format="""-Identification(label or name of the field): zip
-Evaluation: fail
-Reasoning(explanation of the evaluation result): The required cue is correctly implemented using both a visible asterisk and the aria-required attribute. However, the error cue relies solely on color (red border) with no associated text or semantic indicators, so this fails WCAG 1.4.1."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 3 PASS - Proper required cue and error cue with semantic support
    dspy.Example(
        html_snippet_before="""
<label for="password">Password *</label>
<input id="password" aria-required="true" aria-invalid="true" aria-describedby="pw-err">
<div id="pw-err" class="error" role="alert">Must be 8+ characters</div>
""",
        invalid_inputs="[]",
        mutations="""[ARIA Attribute] <input>#password aria-required="true"
[ARIA Attribute] <input>#password aria-invalid="true"
[Linked Error Message] 'Must be 8+ characters' linked via aria-describedby""",
        retrieved_guidelines="WCAG 1.4.1: Provide semantic cues such as aria-required and aria-invalid with linked error messages.",
        identification="password",
        evaluation="pass",
        reasoning="""Both required and error cues are conveyed with semantic and visible indicators. The aria-required and aria-invalid attributes are used properly, and the descriptive error message is linked via aria-describedby. This passes WCAG 1.4.1.""",
        format="""-Identification(label or name of the field): password
-Evaluation: pass
-Reasoning(explanation of the evaluation result): Both required and error cues are conveyed with semantic and visible indicators. The aria-required and aria-invalid attributes are used properly, and the descriptive error message is linked via aria-describedby. This passes WCAG 1.4.1."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 4 INAPPLICABLE - Optional field with no validation cues
    dspy.Example(
        html_snippet_before="""
<label for="nickname">Nickname (optional)</label>
<input id="nickname">
""",
        invalid_inputs="[]",
        mutations="No visual or semantic changes detected after interaction.",
        retrieved_guidelines="WCAG 1.4.1: No required or error cues are needed for optional fields without validation.",
        identification="nickname",
        evaluation="inapplicable",
        reasoning="""The field is optional, with no required or error cues detected. Since no validation or error state applies, this case is inapplicable under WCAG 1.4.1.""",
        format="""-Identification(label or name of the field): nickname
-Evaluation: inapplicable
-Reasoning(explanation of the evaluation result): The field is optional, with no required or error cues detected. Since no validation or error state applies, this case is inapplicable under WCAG 1.4.1."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),
]

