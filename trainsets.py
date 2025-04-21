import dspy


trainset = [
    #1  PASS - Required field with an error message when empty.
    dspy.Example(
        html_snippet_before="""<label for='password'>*Password:</label>
                           <input type='password' name='password' id='password' required>""",
        
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations="[Error Message Added] Password is required. (Field: '*Password:' | name='password')&&[DOM Node Added] Snippet: <span class='error' id='error-password'>Password is required.</span>... (Field: '*Password:' | name='password')",
        evaluation="""-Identification: *Password
-Evaluation: pass
-Reasoning: The field is marked with the required attribute and triggers an error message when left empty, meeting accessibility expectations."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #2 FAIL - Missing required attribute but still showing an error message
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='email' name='email' id='email'>""",
       
        retrieved_guidelines="If an input field raises a required error message, it must provide the 'required' or aria-required='true' cue.",
        mutations="[Visible Error Message Revealed] Email is required. (Field: 'Email:' | name='email')&&[DOM Node Added] Snippet: <span class='error' id='error-email'>Email is required.</span>... (Field: 'Email:' | name='email')",
        evaluation="""-Identification: *Email
-Evaluation: fail
-Reasoning: The field raises an error because it is required but lacks the 'required' attribute."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #3 FAIL - Placeholder as a required indicator
    dspy.Example(
        html_snippet_before="""<input type='text' name='username' id='username' placeholder='Enter your username (required)'>""",
        
        retrieved_guidelines="Placeholders should not be the only indicator of a required field.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: username
-Evaluation: fail
-Reasoning: Placeholder text is not a reliable accessibility cue."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #4 FAIL - No error message for a required field
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='text' name='email' id='email' required>""",
        
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: *Email:
-Evaluation: fail
-Reasoning: The required field does not display an error message when left empty."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #5 FAIL - aria-required="true" used but no error message
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone:</label>
                           <input type='tel' name='phone' id='phone' aria-required='true'>""",
        
        retrieved_guidelines="ARIA attributes like 'aria-required' should be accompanied by proper error messages.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: *Phone:
-Evaluation: fail
-Reasoning: The form does not display an error message despite 'aria-required' being set."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #6 PASS - Disabled field does not trigger an error
    dspy.Example(
        html_snippet_before="""<label for='age'>*Age:</label>
                           <input type='number' name='age' id='age' disabled>""",
        
        retrieved_guidelines="Disabled fields should not trigger required field error messages.",
        mutations=None,
        evaluation="""-Identification: *Age:
-Evaluation: pass
-Reasoning: The field is disabled and does not incorrectly show an error message."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #6B FAIL - Incorrectly triggers error on a disabled field
    dspy.Example(
        html_snippet_before="""<label for='zipcode'>*ZIP Code:</label>
    <input type='text' name='zipcode' id='zipcode' disabled>""",
        retrieved_guidelines="Disabled fields should not trigger required field error messages.",
        mutations="[Error Message Added] ZIP Code is required. (Field: '*ZIP Code:' | name='zipcode')",
        evaluation="""-Identification: *ZIP Code
-Evaluation: fail
-Reasoning: The field is disabled but still triggers a required error, which should not happen."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),


    #7 PASS - Read-only field does not trigger an error
    dspy.Example(
        html_snippet_before="""<label for='country'>*Country:</label>
                           <input type='text' name='country' id='country' value='USA' readonly>""",
        
        retrieved_guidelines="Readonly fields should not trigger required field error messages.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: *Country:
-Evaluation: pass
-Reasoning: The field is readonly and does not incorrectly show an error message."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #8 FAIL - Required Field with Hidden Error Message
    dspy.Example(
        html_snippet_before="""<label for='username'>*Username:</label>
                        <input type='text' name='username' id='username' required>""",
        
        retrieved_guidelines="Error messages should be programmatically visible and not hidden with CSS.",
        mutations="[Hidden Error Message Detected] Username is required. (Field: '*Username:' | name='username')",
        evaluation="""-Identification: *Username:
-Evaluation: fail
-Reasoning: The error message is present but visually hidden, which is an accessibility issue."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #9 FAIL - aria-invalid="true" Used Without Error Message, TODO review for when i use inputs
    dspy.Example(
        html_snippet_before="""<input type='text' name='email' id='email' aria-invalid='true'>""",
        retrieved_guidelines="Fields marked with 'aria-invalid' should be accompanied by an error message.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: email
-Evaluation: fail
-Reasoning: The field is marked as invalid but lacks an error message."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #10 PASS - Required Checkbox Not Checked
    dspy.Example(
        html_snippet_before="""<label for='terms'>*I agree to the terms:</label>
                        <input type='checkbox' id='terms' name='terms' required>""",
        
        retrieved_guidelines="Required checkboxes should trigger an error if left unchecked .",
        mutations="[Visible Error Message Revealed] You must agree to the terms. (Field: 'I agree to the terms' | name='terms')&&[DOM Node Added] Snippet: <div class='error'>You must agree to the terms.</div>...(Field: 'I agree to the terms' | name='terms')",
        evaluation="""-Identification: *I agree to the terms:
-Evaluation: pass
-Reasoning: The form correctly displays an error message when the required checkbox is not checked."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #10B FAIL - Required checkbox doesn’t show an error, TODO review because can be misleading 
    dspy.Example(
        html_snippet_before="""<label for='consent'>*I consent to data collection:</label>
    <input type='checkbox' id='consent' name='consent' required>""",
        retrieved_guidelines="Required checkboxes should trigger an error if left unchecked.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: *I consent to data collection
-Evaluation: fail
-Reasoning: The required checkbox does not display an error message when left unchecked."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #11 INAPPLICABLE - Hidden input
    dspy.Example(
        html_snippet_before="""<input type='hidden' name='csrf_token' value='abc123'>""",
        retrieved_guidelines="The 'required' attribute is not applicable to hidden input fields.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: csrf_token
-Evaluation: inapplicable
-Reasoning: Hidden fields are not meant to be user-editable and do not require the 'required' attribute."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #12 INAPPLICABLE - Disabled input
    dspy.Example(
        html_snippet_before="""<label for='promo'>Promo Code:</label>
    <input type='text' name='promo' id='promo' disabled>""",
        retrieved_guidelines="Disabled fields are excluded from validation and should not be evaluated for 'required' logic.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: Promo Code
-Evaluation: inapplicable
-Reasoning: The field is disabled and therefore excluded from validation logic including required checks."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #13 PASS - Optional Field with No Requirement or Error
    dspy.Example(
        html_snippet_before="""<label for='middle-name'>Middle Name (Optional):</label>
    <input type='text' name='middle-name' id='middle-name'>""",
        retrieved_guidelines="Optional fields do not require the 'required' attribute or related validation feedback.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: Middle Name (Optional)
-Evaluation: pass
-Reasoning: The field is intentionally optional and no validation logic is triggered on submit."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #14 INAPPLICABLE - Submit Button
    dspy.Example(
        html_snippet_before="""<input type='submit' value='Submit Form'>""",
        retrieved_guidelines="The 'required' attribute does not apply to submit buttons.",
        mutations="No dynamic changes detected after form interaction.",
        evaluation="""-Identification: Submit Button
-Evaluation: inapplicable
-Reasoning: Buttons are not user-input fields and are unaffected by required validation rules."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations")

]

#TODO expand
trainset_no_submit = [
    #1 INAPPLICABLE - Required field cannot be validated without submit
    dspy.Example(
        html_snippet_before="""<label for='password'>*Password:</label>
                           <input type='password' name='password' id='password' required>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Password:
-Evaluation: innaplicable
-Reasoning: Unable to confirm whether error messages appear for required fields without form submission."""
    ).with_inputs("html_snippet_before","retrieved_guidelines", "mutations"),

    #2 FAIL - Missing required attribute (structural failure, still valid)
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='email' name='email' id='email'>""",
        retrieved_guidelines="If an input field raises a required error message, it must provide the 'required' or aria-required='true' cue.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Email:
-Evaluation: fail
-Reasoning: The field is missing a required attribute, as it has an asterisk"""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #3 FAIL - Placeholder as a required indicator
    dspy.Example(
        html_snippet_before="""<input type='text' name='username' id='username' placeholder='Enter your username (required)'>""",
        retrieved_guidelines="Placeholders should not be the only indicator of a required field.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: username
-Evaluation: fail
-Reasoning: Placeholder text is not a reliable accessibility cue."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #4 INAPPLICABLE - Error message absence cannot be confirmed
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='text' name='email' id='email' required>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Email:
-Evaluation: inapplicable
-Reasoning: Cannot confirm whether the form shows an error message for this required field."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #5 INAPPLICABLE - Cannot verify error feedback on aria-required
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone:</label>
                           <input type='tel' name='phone' id='phone' aria-required='true'>""",
        retrieved_guidelines="ARIA attributes like 'aria-required' should be accompanied by proper error messages.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Phone:
-Evaluation: inapplicable
-Reasoning: Error message behavior cannot be determined without form submission."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #6 PASS - Disabled field does not require submit to evaluate
    dspy.Example(
        html_snippet_before="""<label for='age'>*Age:</label>
                           <input type='number' name='age' id='age' disabled>""",
        retrieved_guidelines="Disabled fields should not trigger required field error messages.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Age:
-Evaluation: pass
-Reasoning: Disabled fields are exempt from required field validation, regardless of interaction."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #7 PASS - Read-only field does not require submit to evaluate
    dspy.Example(
        html_snippet_before="""<label for='country'>*Country:</label>
                           <input type='text' name='country' id='country' value='USA' readonly>""",
        retrieved_guidelines="Readonly fields should not trigger required field error messages.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Country:
-Evaluation: pass
-Reasoning: Readonly fields are correctly excluded from validation requirements."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #8 INAPPLICABLE - Cannot verify visibility of error message
    dspy.Example(
        html_snippet_before="""<label for='username'>*Username:</label>
                        <input type='text' name='username' id='username' required>""",
        retrieved_guidelines="Error messages should be programmatically visible and not hidden with CSS.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *Username:
-Evaluation: inapplicable
-Reasoning: Cannot confirm whether an error message exists or is hidden."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #9 FAIL - aria-invalid used without supporting context (static issue)
    dspy.Example(
        html_snippet_before="""<input type='text' name='email' id='email' aria-invalid='true'>""",
        retrieved_guidelines="Fields marked with 'aria-invalid' should be accompanied by an error message.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: email
-Evaluation: fail
-Reasoning: Field marked as invalid but lacks structural indication of an accompanying error message."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #10 INAPPLICABLE - Required checkbox error behavior cannot be confirmed
    dspy.Example(
        html_snippet_before="""<label for='terms'>*I agree to the terms:</label>
                        <input type='checkbox' id='terms' name='terms' required>""",
        retrieved_guidelines="Required checkboxes should trigger an error if left unchecked.",
        mutations="Unavailable: Submit interaction not possible.",
        evaluation="""-Identification: *I agree to the terms:
-Evaluation: inapplicable
-Reasoning: Cannot confirm whether the form provides feedback when the checkbox is left unchecked."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),
    
]