import dspy


trainset = [
    #1  PASS - Required field with an error message when empty.
    dspy.Example(
        html_snippet_before="""<label for='password'>*Password:</label>
                           <input type='password' name='password' id='password' required>""",
        html_snippet_after="""<label for='password'>*Password:</label>
                          <input type='password' name='password' id='password' required>
                          <span class='error' id='password-error'>This field is required.</span>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations=None,
        evaluation="Pass: The form correctly displays an error message when the required field is empty."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #2 FAIL - Missing required attribute but still showing an error message
    dspy.Example(
        html_snippet_before="""<label for='email'>Email:</label>
                           <input type='email' name='email' id='email'>""",
        html_snippet_after="""<label for='email'>Email:</label>
                          <input type='email' name='email' id='email'>
                          <span class='error'>This field is required.</span>""",
        retrieved_guidelines="If an input field raises a required error message, it must provide the 'required' or aria-required='true' cue.",
        mutations=None,
        evaluation="Fail: The field raises an error because it is required but lacks the 'required' attribute."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #3 FAIL - Placeholder as a required indicator
    dspy.Example(
        html_snippet_before="""<input type='text' name='username' id='username' placeholder='Enter your username (required)'>""",
        html_snippet_after="""<input type='text' name='username' id='username' placeholder='Enter your username (required)'>""",
        retrieved_guidelines="Placeholders should not be the only indicator of a required field.",
        mutations=None,
        evaluation="Fail: Placeholder text is not a reliable accessibility cue."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #4 FAIL - No error message for a required field
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='text' name='email' id='email' required>""",
        html_snippet_after="""<label for='email'>*Email:</label>
                          <input type='text' name='email' id='email' required>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations=None,
        evaluation="Fail: The required field does not display an error message when left empty."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #5 FAIL - aria-required="true" used but no error message
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone:</label>
                           <input type='tel' name='phone' id='phone' aria-required='true'>""",
        html_snippet_after="""<label for='phone'>*Phone:</label>
                          <input type='tel' name='phone' id='phone' aria-required='true'>""",
        retrieved_guidelines="ARIA attributes like 'aria-required' should be accompanied by proper error messages.",
        mutations=None,
        evaluation="Fail: The form does not display an error message despite 'aria-required' being set."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #6 PASS - Disabled field does not trigger an error
    dspy.Example(
        html_snippet_before="""<label for='age'>*Age:</label>
                           <input type='number' name='age' id='age' disabled>""",
        html_snippet_after="""<label for='age'>*Age:</label>
                          <input type='number' name='age' id='age' disabled>""",
        retrieved_guidelines="Disabled fields should not trigger required field error messages.",
        mutations=None,
        evaluation="Pass: The field is disabled and does not incorrectly show an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #7 PASS - Read-only field does not trigger an error
    dspy.Example(
        html_snippet_before="""<label for='country'>*Country:</label>
                           <input type='text' name='country' id='country' value='USA' readonly>""",
        html_snippet_after="""<label for='country'>*Country:</label>
                          <input type='text' name='country' id='country' value='USA' readonly>""",
        retrieved_guidelines="Readonly fields should not trigger required field error messages.",
        mutations=None,
        evaluation="Pass: The field is readonly and does not incorrectly show an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #8 FAIL - Required Field with Hidden Error Message, TODO review
    dspy.Example(
        html_snippet_before="""<label for='username'>*Username:</label>
                        <input type='text' name='username' id='username' required>""",
        html_snippet_after="""<label for='username'>*Username:</label>
                        <input type='text' name='username' id='username' required>
                        <span class='error' style='display: none;'>This field is required.</span>""",
        retrieved_guidelines="Error messages should be programmatically visible and not hidden with CSS.",
        mutations=None,
        evaluation="Fail: The error message is present but visually hidden, which is an accessibility issue."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #9 FAIL - aria-invalid="true" Used Without Error Message, TODO review for when i use inputs
    dspy.Example(
        html_snippet_before="""<input type='text' name='email' id='email' aria-invalid='true'>""",
        html_snippet_after="""<input type='text' name='email' id='email' aria-invalid='true'>""",
        retrieved_guidelines="Fields marked with 'aria-invalid' should be accompanied by an error message.",
        mutations=None,
        evaluation="Fail: The field is marked as invalid but lacks an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #10 PASS - Required Checkbox Not Checked
    dspy.Example(
        html_snippet_before="""<label for='terms'>*I agree to the terms:</label>
                        <input type='checkbox' id='terms' name='terms' required>""",
        html_snippet_after="""<label for='terms'>*I agree to the terms:</label>
                        <input type='checkbox' id='terms' name='terms' required>
                        <span class='error'>This field is required.</span>""",
        retrieved_guidelines="Required checkboxes should trigger an error if left unchecked .",
        mutations=None,
        evaluation="Pass: The form correctly displays an error message when the required checkbox is not checked."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

]

#TODO expand
trainset_no_submit = [
    #1  PASS - Required field without submission
    dspy.Example(
        html_snippet_before="""<label for='username'>*Username:</label>
                           <input type='text' name='username' id='username' required>""",
        html_snippet_after=None,
        retrieved_guidelines="Forms should ensure required fields are properly marked.",
        mutations=None,
        evaluation="Pass: The field is properly marked as required"
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #2 FAIL - Required field is missing the required attribute
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone Number:</label>
                           <input type='tel' name='phone' id='phone'>""",
        html_snippet_after=None,
        retrieved_guidelines="Forms should ensure required fields are identificated with the 'required' attribute.",
        mutations=None,
        evaluation="Fail: The form field is not properly identificated as required with 'required attribute'."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #3 FAIL - Asterisk (*) Used Instead of 'required' Attribute
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                        <input type='email' name='email' id='email'>""",
        html_snippet_after=None,
        retrieved_guidelines="Asterisks are not a reliable accessibility cue for required fields.",
        mutations=None,
        evaluation="Fail: The field has an asterisk but lacks the 'required' attribute."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #4 FAIL - Placeholder Text as the Only Required Indicator
    dspy.Example(
        html_snippet_before="""<input type='text' name='username' id='username' placeholder='Enter your username (required)'>""",
        html_snippet_after=None,
        retrieved_guidelines="Placeholder text should not be the only indicator of a required field.",
        mutations=None,
        evaluation="Fail: The field lacks a 'required' attribute and only uses placeholder text to indicate necessity."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #5 FAIL - Disabled Field Has the 'required' Attribute
    dspy.Example(
        html_snippet_before="""<label for='company'>*Company:</label>
                        <input type='text' name='company' id='company' disabled required>""",
        html_snippet_after=None,
        retrieved_guidelines="Disabled fields should not be marked as required .",
        mutations=None,
        evaluation="Fail: The field is disabled but still marked as required, creating conflicting accessibility cues."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    #6 FAIL - Read-Only Field Has an Error Message
    dspy.Example(
        html_snippet_before="""<label for='country'>*Country:</label>
                        <input type='text' name='country' id='country' value='USA' readonly>""",
        html_snippet_after="""<label for='country'>*Country:</label>
                        <input type='text' name='country' id='country' value='USA' readonly>
                        <span class='error'>This field is required.</span>""",
        retrieved_guidelines="Readonly fields should not trigger required field error messages .",
        mutations=None,
        evaluation="Fail: The form incorrectly displays an error message for a read-only field."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),
]