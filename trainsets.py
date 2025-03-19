import dspy

#TODO Falta testar inputs por causa do read only e disabled e há casos aqui para outros testes , tudo há base do required
trainset = [
    # Error message appears when required field is left empty (valid behavior).
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

    # Asterisk.
    dspy.Example(
        html_snippet_before="""<label for='password'>*Password:</label>
                           <input type='password' name='password' id='password'>""",
        html_snippet_after=None,
        retrieved_guidelines="Fields with '*' usually means the field is required",
        mutations=None,
        evaluation="Fail: The Field has an asterisk that symbolizes its requirement, but has no required attribute ."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    # Error message appears but field not marked as required (incorrect behavior).
    dspy.Example(
        html_snippet_before="""<label for='password'>Password:</label>
                           <input type='password' name='password' id='password'>""",
        html_snippet_after="""<label for='password'>Password:</label>
                          <input type='password' name='password' id='password'>
                          <span class='error' id='password-error'>This field is required.</span>""",
        retrieved_guidelines="If an input field raises a required error message, it must provide the 'required' or aria-required='true' cue.",
        mutations=None,
        evaluation="Fail: The field raises an error because it is required but it has no required."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    # No error message appears for a required field (incorrect behavior).
    dspy.Example(
        html_snippet_before="""<label for='email'>*Email:</label>
                           <input type='text' name='email' id='email' required>""",
        html_snippet_after="""<label for='email'>*Email:</label>
                          <input type='text' name='email' id='email' required>""",
        retrieved_guidelines="Forms should provide error messages when required fields are left empty.",
        mutations=None,
        evaluation="Fail: The required field does not display an error message when left empty."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    

    # Required field is marked with 'aria-required' but lacks an error message after submission.
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone:</label>
                           <input type='tel' name='phone' id='phone' aria-required='true'>""",
        html_snippet_after="""<label for='phone'>*Phone:</label>
                          <input type='tel' name='phone' id='phone' aria-required='true'>""",
        retrieved_guidelines="ARIA attributes like 'aria-required' should be accompanied by proper error messages.",
        mutations=None,
        evaluation="Fail: The form does not display an error message despite 'aria-required' being set."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    dspy.Example(
        html_snippet_before="""<label for='age'>*Age:</label>
                           <input type='number' name='age' id='age' disabled>""",
        html_snippet_after="""<label for='age'>*Age:</label>
                          <input type='number' name='age' id='age' disabled>""",
        retrieved_guidelines="Disabled fields should not trigger required field error messages.",
        mutations=None,
        evaluation="Pass: The field is disabled and does not incorrectly show an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    dspy.Example(
        html_snippet_before="""<label for='country'>*Country:</label>
                           <input type='text' name='country' id='country' value='USA' readonly>""",
        html_snippet_after="""<label for='country'>*Country:</label>
                          <input type='text' name='country' id='country' value='USA' readonly>""",
        retrieved_guidelines="Readonly fields should not trigger required field error messages.",
        mutations=None,
        evaluation="Pass: The field is readonly and does not incorrectly show an error message."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

]

#TODO expand
trainset_no_submit = [
    # Example where a required field is present, but no error appears since the submit button is unclickable.
    dspy.Example(
        html_snippet_before="""<label for='username'>*Username:</label>
                           <input type='text' name='username' id='username' required>""",
        html_snippet_after=None,
        retrieved_guidelines="Forms should ensure required fields are properly marked.",
        mutations=None,
        evaluation="Pass: The field is properly marked as required"
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),

    # Example where an optional field exists, but since submission isn't possible, it can't generate an error.
    dspy.Example(
        html_snippet_before="""<label for='phone'>*Phone Number:</label>
                           <input type='tel' name='phone' id='phone'>""",
        html_snippet_after=None,
        retrieved_guidelines="Forms should ensure required fields are identificated with the 'required' attribute.",
        mutations=None,
        evaluation="Fail: The form field is not properly identificated as required with 'required attribute'."
    ).with_inputs("html_snippet_before", "html_snippet_after", "retrieved_guidelines", "mutations"),
]