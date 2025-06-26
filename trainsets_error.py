import dspy

trainset_error_identification = [
    # 1 PASS: Error visible + aria-describedby
    dspy.Example(
        html_snippet_before="""<input type='text' id='username' aria-describedby='username-error'>
<span id='username-error' class='error'>Username is required.</span>""",
        mutations="[Message Revealed] Username is required. (Field: 'username')",
        retrieved_guidelines="Error messages must be programmatically associated with the input using aria-describedby or similar mechanisms.",
        identification="username",
        evaluation="pass",
        reasoning="The field is associated with a visible error message via aria-describedby, fulfilling WCAG 3.3.1.",
        format="""-Identification: username
-Evaluation: pass
-Reasoning: The field is associated with a visible error message via aria-describedby, fulfilling WCAG 3.3.1."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 2 FAIL: No message shown
    dspy.Example(
        html_snippet_before="<input type='email' id='email' required>",
        mutations="No dynamic changes detected after form interaction.",
        retrieved_guidelines="A field must show a visible error message when validation fails.",
        identification="email",
        evaluation="fail",
        reasoning="The required email field does not display any error message when left empty.",
        format="""-Identification: email
-Evaluation: fail
-Reasoning: The required email field does not display any error message when left empty."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 3 FAIL: Message shown, not associated
    dspy.Example(
        html_snippet_before="""<input type='text' id='phone'>
<span class='error'>Phone number is required.</span>""",
        mutations="[Message Revealed] Phone number is required.",
        retrieved_guidelines="Error messages must be clearly linked visually or programmatically to the input field.",
        identification="phone",
        evaluation="fail",
        reasoning="The error message is shown but not programmatically linked to the input field via aria-describedby or proximity.",
        format="""-Identification: phone
-Evaluation: fail
-Reasoning: The error message is shown but not programmatically linked to the input field via aria-describedby or proximity."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 4 INAPPLICABLE: Optional field
    dspy.Example(
        html_snippet_before="<input type='text' id='middle-name'>",
        mutations="No dynamic changes detected after form interaction.",
        retrieved_guidelines="Optional fields are not expected to produce validation feedback.",
        identification="middle-name",
        evaluation="inapplicable",
        reasoning="This field is optional and does not trigger validation errors.",
        format="""-Identification: middle-name
-Evaluation: inapplicable
-Reasoning: This field is optional and does not trigger validation errors."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 5 FAIL (error message hidden in attribute)
    dspy.Example(
        html_snippet_before="""
    <div class="textbox-ui input-ui">
    <label error="Defina uma password.">
        <span>Password</span>
        <input id="password" type="password">
    </label>
    </div>
    """,
        retrieved_guidelines="Error messages must be visually and programmatically associated with the input field using mechanisms like aria-describedby or visible content.",
        mutations="[Attribute Change] Label now includes error='Defina uma password.'",
        identification="password",
        evaluation="fail",
        reasoning="The error message is stored in a non-standard attribute ('error') and is not visible in the DOM or exposed to assistive technologies. This fails WCAG 3.3.1 and its ACT Rule, which require programmatic association using visible content or standard ARIA.",
        format="""-Identification: password
-Evaluation: pass
-Reasoning: The error message is stored in a non-standard attribute ('error') and is not visible in the DOM or exposed to assistive technologies. This fails WCAG 3.3.1 and its ACT Rule, which require programmatic association using visible content or standard ARIA."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 6  FAIL (error in sibling, not associated)
    dspy.Example(
        html_snippet_before="""
    <div class="textbox-ui input-ui">
    <label>
        <span>Email</span>
        <input id="email" type="email">
    </label>
    <span class="error">Campo obrigatório</span>
    </div>
    """,
        retrieved_guidelines="Error messages must be linked to the field either visually (e.g., adjacent) or programmatically (e.g., via aria-describedby or label wrapping).",
        mutations="[DOM Node Added] Error span shown with text 'Campo obrigatório'",
        identification="email",
        evaluation="fail",
        reasoning="The error message is visible, but is not programmatically linked and is only a sibling element. Without aria-describedby or label wrapping, this fails 3.3.1.",
        format="""-Identification: email
-Evaluation: fail
-Reasoning: The error message is visible, but is not programmatically linked and is only a sibling element. Without aria-describedby or label wrapping, this fails 3.3.1."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #7 PASS (label wraps input, text dynamically added)
    dspy.Example(
        html_snippet_before="""
    <label>
    <span>Username</span>
    <input id="username" type="text">
    <span class="error" id="username-error">Please enter a username.</span>
    </label>
    """,
        retrieved_guidelines="Label-wrapped inputs can satisfy error association if error messages are added within the label or referenced by id.",
        mutations="[DOM Node Added] Error span inserted inside label with text 'Please enter a username.'",
        identification="username",
        evaluation="pass",
        reasoning="The error is inserted inside the label wrapping the input, which provides strong programmatic and visual association.",
        format="""-Identification: username
-Evaluation: pass
-Reasoning: The error is inserted inside the label wrapping the input, which provides strong programmatic and visual association."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"), 

    #8 FAIL: Error message not programmatically associated
    dspy.Example(
        html_snippet_before="""
    <div class="form-group">
    <label data-error="Please enter your name">
        <span>Name</span>
        <input id="user-name" name="username" type="text" placeholder="">
    </label>
    <span id="username-required-msg" class="error" style="display:none;">Please enter your name</span>
    </div>
    """,
        mutations="[Message Revealed] Please enter your name (Field: 'Name')",
        retrieved_guidelines="Error messages must be programmatically associated with form fields using mechanisms such as aria-describedby, aria-errormessage, or by placing the error text inside the label.",
        identification="user-name",
        evaluation="fail",
        reasoning="The error message becomes visible after user interaction, but it is not programmatically associated with the input. The message is outside the label and the input lacks aria-describedby or any semantic reference. The data-error attribute is not exposed to assistive technologies.",
        format="""-Identification: user-name
-Evaluation: fail
-Reasoning: The error message becomes visible after user interaction, but it is not programmatically associated with the input. The message is outside the label and the input lacks aria-describedby or any semantic reference. The data-error attribute is not exposed to assistive technologies."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"), 

    #9 FAIL: Hidden error message not exposed to AT
    dspy.Example(
        html_snippet_before="""
    <div class="form-group">
    <label for="email">Email address</label>
    <input
        type="email"
        id="email"
        name="userEmail"
        aria-describedby="email-error">
    
    <div id="email-error" style="display: none;">
        Please enter a valid email address.
    </div>
    </div>
    """,
        mutations="[Message Hidden] Please enter a valid email address (Field: 'Email address')",
        retrieved_guidelines="Error messages must be perceivable by assistive technologies. Elements referenced by aria-describedby must be included in the accessibility tree. Hidden elements using display:none are not read by screen readers.",
        identification="email",
        evaluation="fail",
        reasoning="The input references an error message via aria-describedby, but the referenced element is hidden using display:none. As a result, the error is not exposed to screen readers, violating WCAG 3.3.1 and ACT Rule 36b590.",
        format="""-Identification: email
-Evaluation: fail
-Reasoning: The input references an error message via aria-describedby, but the referenced element is hidden using display:none. As a result, the error is not exposed to screen readers, violating WCAG 3.3.1 and ACT Rule 36b590."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    #10 PASS
    dspy.Example(
        html_snippet_before="""
    <div class="form-group">
    <label id="label-lastname" for="lastname">Last Name (Required)</label>
    <input
        type="text"
        id="lastname"
        name="Last_Name"
        aria-required="true"
        aria-invalid="true"
        aria-labelledby="label-lastname"
        aria-describedby="lastname-error">
    <div id="lastname-error" role="status">Please enter some valid input. Input is not optional.</div>
    </div>
    """,
        mutations="[Message Revealed] Please enter some valid input. Input is not optional. (Field: 'Last Name')",
        retrieved_guidelines="Error messages must be programmatically associated with input fields using aria-describedby or similar mechanisms, and must be perceivable in the accessibility tree.",
        identification="lastname",
        evaluation="pass",
        reasoning="The field is linked to the visible error message using aria-describedby, and the message is rendered in the accessibility tree. This satisfies WCAG 3.3.1 and ACT Rule 36b590.",
        format="""-Identification: lastname
-Evaluation: pass
-Reasoning: The field is linked to the visible error message using aria-describedby, and the message is rendered in the accessibility tree. This satisfies WCAG 3.3.1 and ACT Rule 36b590."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations")
]


trainset_error_identification_no_submit = [
    # 1 FAIL: Error message present but not linked
    dspy.Example(
        html_snippet_before="""<input type='text' id='username'>
<span class='error'>Username required</span>""",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Messages should be programmatically associated using aria-describedby.",
        identification="username",
        evaluation="fail",
        reasoning="An error message exists in the HTML but is not linked to the input with aria-describedby or 'for' attributes.",
        format="""-Identification: username
-Evaluation: fail
-Reasoning: An error message exists in the HTML but is not linked to the input with aria-describedby or 'for' attributes."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 2 PASS: Pre-linked error container
    dspy.Example(
        html_snippet_before="""<input id='email' aria-describedby='email-error'>
<span id='email-error' class='error' style='display:none'>Please enter your email.</span>""",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Pre-linked containers via aria-describedby are acceptable as long as linkage exists.",
        identification="email",
        evaluation="pass",
        reasoning="The field is linked to a message container via aria-describedby, even if it's not visible yet.",
        format="""-Identification: email
-Evaluation: pass
-Reasoning: The field is linked to a message container via aria-describedby, even if it's not visible yet."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    # 3 INAPPLICABLE: Readonly field
    dspy.Example(
        html_snippet_before="<input id='country' value='Portugal' readonly>",
        mutations="Unavailable: Submit interaction not possible.",
        retrieved_guidelines="Readonly fields are not expected to trigger validation feedback.",
        identification="country",
        evaluation="inapplicable",
        reasoning="This field is readonly and not expected to trigger an error message.",
        format="""-Identification: country
-Evaluation: inapplicable
-Reasoning: This field is readonly and not expected to trigger an error message."""
    ).with_inputs("html_snippet_before", "retrieved_guidelines", "mutations"),

    

]
