import dspy

trainset_error_clarity = [

    # 1 PASS: Clear, specific message with aria-describedby
    dspy.Example(
        html_snippet_before="""<label for="email">Email</label><input type="email" id="email" aria-describedby="email-error">""",
        invalid_inputs="[{'field': 'Email', 'value': 'userexample.com'}]",
        mutations="[Linked Error Message] Please enter a valid email address in the format user@example.com",
        retrieved_guidelines="Error messages should clearly describe the issue and how to fix it (WCAG 3.3.3).",
        identification="Email",
        evaluation="pass",
        reasoning="The error message clearly explains that the email format is invalid and provides an example of the correct format.",
        format="""-Identification: Email
-Evaluation: pass
-Reasoning: The error message clearly explains that the email format is invalid and provides an example of the correct format."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


    # 2 FAIL: Vague message
    dspy.Example(
        html_snippet_before="""<label for="email">Email</label><input type="email" id="email">""",
        invalid_inputs="[{'field': 'Email', 'value': 'userexample.com'}]",
        mutations="[Linked Error Message] Invalid input",
        retrieved_guidelines="Messages should describe the problem and suggest a fix.",
        identification="Email",
        evaluation="fail",
        reasoning="The message 'Invalid input' is too vague and does not guide the user to correct the format.",
        format="""-Identification: Email
-Evaluation: fail
-Reasoning: The message 'Invalid input' is too vague and does not guide the user to correct the format."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),

        dspy.Example(
        html_snippet_before="""<label for="password">Password</label><input type="password" id="password" required>""",
        invalid_inputs="[{'field': 'Password', 'value': '1234'}]",
        mutations="[Linked Error Message] Invalid password",
        retrieved_guidelines="The message should explain what makes the password invalid and how to fix it.",
        identification="Password",
        evaluation="fail",
        reasoning="The message 'Invalid password' does not inform the user of the specific password rules.",
        format="""-Identification: Password
-Evaluation: fail
-Reasoning: The message 'Invalid password' does not inform the user of the specific password rules."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 4 PASS: Password rule explained
    dspy.Example(
        html_snippet_before="""<label for="password">Password</label><input type="password" id="password">""",
        invalid_inputs="[{'field': 'Password', 'value': '1234'}]",
        mutations="[Linked Error Message] Password must be at least 8 characters and include a number and a special character.",
        retrieved_guidelines="Explain the password rules clearly in the message.",
        identification="Password",
        evaluation="pass",
        reasoning="The message describes exactly what the user needs to fix, including length and character requirements.",
        format="""-Identification: Password
-Evaluation: pass
-Reasoning: The message describes exactly what the user needs to fix, including length and character requirements."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),



    # 5 INAPPLICABLE: Optional phone field, no message expected
    dspy.Example(
        html_snippet_before="""<label for="phone">Phone (optional)</label><input type="tel" id="phone">""",
        invalid_inputs="[{'field': 'Phone (optional)', 'value': ''}]",
        mutations="[]",
        retrieved_guidelines="No suggestion needed if the field is optional and no validation is triggered.",
        identification="Phone (optional)",
        evaluation="inapplicable",
        reasoning="The field is optional and no validation was triggered, so no error message is expected.",
        format="""-Identification: Phone (optional)
-Evaluation: inapplicable
-Reasoning: The field is optional and no validation was triggered, so no error message is expected."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),

#6
    dspy.Example(
        html_snippet_before="""
            <label for="name">Nome *</label>
            <input type="text" id="name" name="name" required>
        """,
        invalid_inputs="[{'field': 'Nome*', 'value': '55555'}]",
        mutations="[]",
        retrieved_guidelines="WCAG 3.3.3 applies only when a validation error is triggered. Unusual input alone is not enough to require error messaging.",
        identification="Nome *",
        evaluation="inapplicable",
        reasoning="Although '12345' is not a typical name, no validation error was triggered and the form accepted the value. Since WCAG 3.3.3 only applies when an error is detected, the lack of a message is acceptable.",
        format="""-Identification: Nome*
-Evaluation: inapplicable
-Reasoning: Although '55555' is not a typical name, no validation error was triggered and the form accepted the value. Since WCAG 3.3.3 only applies when an error is detected, the lack of a message is acceptable."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),

    # 7 INAPPLICABLE: Read-only field
    dspy.Example(
        html_snippet_before="""<label for="id">User ID</label><input id="id" readonly value="12345">""",
        invalid_inputs="[{'field': 'User ID', 'value': '12345'}]",
        mutations="[]",
        retrieved_guidelines="Read-only fields are not subject to validation.",
        identification="User ID",
        evaluation="inapplicable",
        reasoning="The field is read-only and not user-editable, so no error messaging is applicable.",
        format="""-Identification: User ID
-Evaluation: inapplicable
-Reasoning: The field is read-only and not user-editable, so no error messaging is applicable."""
    ).with_inputs("html_snippet_before", "invalid_inputs", "mutations", "retrieved_guidelines"),


]



trainset_error_suggestion_no_submit = [

    # 1 FAIL: Error message visible but vague and unlinked
    dspy.Example(
        html_snippet_before="""<label for='email'>Email</label>
<input id='email'>
<span class='error'>Invalid input</span>""",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Error messages should describe the problem and guide the user to correct it.",
        identification="email",
        evaluation="fail",
        reasoning="The message 'Invalid input' is visible in the DOM but too vague to help the user fix the error. It is also not linked to the input.",
        format="""-Identification: email
-Evaluation: fail
-Reasoning: The message 'Invalid input' is visible in the DOM but too vague to help the user fix the error. It is also not linked to the input."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),


    # 2 PASS: Descriptive pre-written error with aria-describedby
    dspy.Example(
        html_snippet_before="""<label for='password'>Password</label>
<input id='password' aria-describedby='pw-error'>
<div id='pw-error' class='error'>Must be 8+ characters, include a number and a symbol.</div>""",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Descriptive error messages in containers linked via aria-describedby can be considered helpful.",
        identification="password",
        evaluation="pass",
        reasoning="The message is pre-written, specific, and linked to the field with aria-describedby, which makes it accessible and actionable.",
        format="""-Identification: password
-Evaluation: pass
-Reasoning: The message is pre-written, specific, and linked to the field with aria-describedby, which makes it accessible and actionable."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),


    # 3 INAPPLICABLE: Field does not seem to require validation
    dspy.Example(
        html_snippet_before="""<label for='nickname'>Nickname (optional)</label>
<input id='nickname'>""",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Optional fields that do not expect validation errors are not subject to error suggestion requirements.",
        identification="nickname",
        evaluation="inapplicable",
        reasoning="The field is labeled as optional and shows no indication of validation or error suggestion being needed.",
        format="""-Identification: nickname
-Evaluation: inapplicable
-Reasoning: The field is labeled as optional and shows no indication of validation or error suggestion being needed."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),


    # 4 FAIL: Message warns of error but lacks actionable guidance
    dspy.Example(
        html_snippet_before="""<label for='username'>Username</label>
<input id='username' aria-describedby='username-hint'>
<div id='username-hint' class='error'>Something went wrong.</div>""",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Error text should explain what caused the failure and how to fix it.",
        identification="username",
        evaluation="fail",
        reasoning="Although linked via aria-describedby, the message 'Something went wrong' is too vague to guide a correction.",
        format="""-Identification: username
-Evaluation: fail
-Reasoning: Although linked via aria-describedby, the message 'Something went wrong' is too vague to guide a correction."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

]

