import dspy
from dsp.utils import deduplicate
import os
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.evaluate import Evaluate

counter = 0  # Initialize the global counter

# Set up the API key
os.environ["MISTRAL_API_KEY"] = "vZYsFYM6r2E9JWyD3GYPdLfR34kI2EcO"

# Configure DSPy with the model and retriever
mini = dspy.LM('mistral/mistral-large-latest')
rm = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(lm=mini, rm=rm)

# Define signatures for evaluation
class EvaluateAccessibility(dspy.Signature):
    """Checks if form fields have valid autocomplete attributes."""
    html_snippet = dspy.InputField(desc="HTML form snippet.")
    retrieved_guidelines = dspy.InputField(desc="Relevant information for WCAG 1.3.5 guideline AND Input Purposes for User Interface Components.")
    evaluation = dspy.OutputField(desc="Compliance report with identified issues, giving a passed, failed or inapplicable value for each example.")

class GenerateSearchQuery(dspy.Signature):
    """Generate a search query to find best practices for input purpose identification (WCAG 1.3.5)"""
    html_snippet = dspy.InputField(desc="Form field HTML snippet containing an input element.")
    query = dspy.OutputField(desc="Search query to retrieve WCAG 1.3.5 best practices, valid values, and common autocomplete mistakes.")

class AccessibilityEvaluator(dspy.Module):
    def __init__(self, passages_per_hop=2, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.evaluate_accessibility = dspy.ChainOfThought(EvaluateAccessibility)
        self.max_hops = max_hops

    def forward(self, html_snippet, retrieved_guidelines=None):
        global counter
        retrieved_guidelines = []
        queries = set()

        for hop in range(self.max_hops):
            try:
                query = self.generate_query[hop](html_snippet=html_snippet).query
                if query in queries:
                    print(f"Skipping redundant query at Hop {hop + 1}: {query}")
                    query = f"{query} best practices"
                queries.add(query)

                passages = self.retrieve(query).passages
                if not passages:
                    print(f"Fallback: No results for query at Hop {hop + 1}, trying a reformulated query.")
                    fallback_queries = [
                        "WCAG 1.3.5 form accessibility techniques",
                        "Common mistakes in autocomplete attributes for accessibility",
                        "Input field labeling and WCAG compliance"
                    ]
                    for fallback in fallback_queries:
                        passages = self.retrieve(fallback).passages
                        if passages:
                            print(f"Using fallback query: {fallback}")
                            break
                
                retrieved_guidelines = deduplicate(retrieved_guidelines + passages)
            except Exception as e:
                print(f"Error during retrieval at hop {hop + 1}: {e}")
                counter += 1
                continue

        pred = self.evaluate_accessibility(html_snippet=html_snippet, retrieved_guidelines=retrieved_guidelines)
        return dspy.Prediction(retrieved_guidelines=retrieved_guidelines, evaluation=pred.evaluation, queries=list(queries))

# Define the extracted form snippet
html_snippet = """<form action="/on/demandware.store/Sites-continente-Site/default/Address-SaveAddress?addressId=" class="address-form ct-adress-form-wrapper" method="POST" name="dwfrm_address" id="dwfrm_address">
        
        <div class="ct-address-form--input-group ct-address-form--error-container">
            





<div class="ct-service-error-container pwc-border--radius d-none">
    <div class="ct-service-error-icon">
        






<span class="svg-wrapper col-svg-wrapper svg-icon-close-circle " style="width:16px; height:16px">
    <svg class="svg-inline icon-close-circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="100%"><path fill="#eb0203" fill-rule="evenodd" d="m 249.64374,0 c 66.71728,0 129.34666,26.007349 176.52932,73.239447 47.15146,47.263353 73.11441,109.999833 73.11441,176.831223 0,66.83138 -25.96295,129.56786 -73.11441,176.83122 -47.18266,47.2321 -109.81204,73.23945 -176.52932,73.23945 -66.71729,0 -129.34666,-26.00735 -176.529331,-73.23945 C 25.962948,379.63853 0,316.90205 0,250.07067 0,183.23928 25.962948,120.5028 73.114409,73.239447 120.29708,26.007349 182.92645,0 249.64374,0 Z m 0,28.445538 c -59.04075,0 -114.61768,23.006502 -156.43301,64.924598 -86.2831163,86.399414 -86.2831163,227.001644 0,313.401064 41.81533,41.88684 97.36106,64.95586 156.43301,64.95586 59.04074,0 114.61768,-23.03776 156.433,-64.95586 86.28312,-86.39942 86.28312,-227.00165 0,-313.401064 C 364.26142,51.483299 308.71568,28.41428 249.64374,28.41428 Z m 89.93415,111.437742 c 5.58578,-5.59533 14.51054,-5.59533 20.06512,0 5.58578,5.56407 5.58578,14.5041 0,20.09943 l -89.93416,90.08796 89.74692,90.08796 c 5.55458,5.59533 5.55458,14.53535 0,20.09943 -2.74608,2.84455 -6.33471,4.21994 -9.98575,4.21994 -3.58862,0 -7.27087,-1.46917 -9.98575,-4.21994 l -89.93415,-90.08796 -89.96536,90.08796 c -2.71488,2.84455 -6.39712,4.21994 -9.98575,4.21994 -3.55742,0 -7.23967,-1.46917 -9.98575,-4.21994 -5.55457,-5.56408 -5.55457,-14.5041 0,-20.09943 l 89.99657,-90.08796 -89.96537,-90.08796 c -5.58577,-5.59533 -5.58577,-14.53536 0,-20.09943 5.55458,-5.59533 14.47934,-5.59533 20.06512,0 l 89.93416,90.08796 z"></path></svg>
</span>

    </div>

    <span class="ct-service-error-message"></span>
</div>

        </div>

        
        <div class="ct-address-form--zipcode-container ct-address-form--input-group">
            
                <div class="form-group field-input-label label-animation
                    required">

                    <input type="text" class="form-control pwc-form-input w-100 ct-address-form--zipcode-input js-autofill-enabled is-invalid" id="zipCode" data-missing-error="Campo de preenchimento obrigatório." data-pattern-mismatch="Código postal inválido." data-toggle="tooltip" data-placement="top" data-mask="0000-000" autocomplete="off" title="" name="dwfrm_address_zipCode" required="" aria-required="true" value="" maxlength="8" pattern="^[0-9]{4}(?:-[0-9]{3})?$" data-original-title="Utilize um dos seguintes formatos: 9999 ou 9999-999">
                    <label for="zipCode">
                        * Código postal
                    </label>
                    <span class="invalid-feedback address-form-error-postal-code" data-error-postalcode="Por favor introduza um código postal válido" data-error-apigeo="O seu navegador não suporta a funcionalidade de geolocalização" data-error-allowgeo="Por favor aceite a geolocalização para este site" data-error-general="De momento não é possível efetuar a operação pretendida. Por favor tente novamente. Se o erro persistir, não hesite em contactar-nos." data-error-auth-failed="Código postal não encontrado">Campo de preenchimento obrigatório.</span>
                </div>
            

            <div class="postal-code-get-coordinates-address-form pwc-tooltip-trigger mr-3" data-toggle="tooltip" data-placement="right" title="" data-original-title="Localizar-me">
                






<span class="svg-wrapper col-svg-wrapper svg-icon-clickgo-localization " style="width:16px; height:16px">
    <svg width="12" height="16" viewBox="0 0 12 16" fill="none" xmlns="http://www.w3.org/2000/svg"> <path fill-rule="evenodd" clip-rule="evenodd" d="M0.400391 5.93269C0.400391 2.66768 2.90593 0 6.00057 0C9.09524 0 11.6007 2.66825 11.6007 5.93269C11.6007 6.96046 11.2865 8.07139 10.8417 9.13822C10.3945 10.2111 9.80009 11.2749 9.20617 12.2178C8.0201 14.1008 6.81087 15.541 6.70336 15.668C6.61559 15.7722 6.50765 15.8556 6.3867 15.9129C6.26537 15.9703 6.13374 16 6.00057 16C5.8674 16 5.73576 15.9703 5.61444 15.9129C5.49352 15.8557 5.38561 15.7722 5.29786 15.6681C5.19095 15.5419 3.98136 14.1013 2.79497 12.2178C2.20105 11.2749 1.60667 10.2111 1.15939 9.13822C0.714656 8.07139 0.400391 6.96046 0.400391 5.93269ZM6.00057 1.00418C3.44869 1.00418 1.36042 3.20905 1.36042 5.93269C1.36042 6.76333 1.61891 7.72818 2.0394 8.73685C2.45735 9.73943 3.02067 10.7509 3.59665 11.6653C4.70211 13.4204 5.83107 14.7817 6.00057 14.9834C6.17006 14.7817 7.29903 13.4204 8.40449 11.6653C8.98046 10.7509 9.54378 9.73943 9.96173 8.73685C10.3822 7.72818 10.6407 6.76333 10.6407 5.93269C10.6407 3.20955 8.55241 1.00418 6.00057 1.00418Z" fill="#EB0203"></path> <path fill-rule="evenodd" clip-rule="evenodd" d="M5.99658 4.01663C4.99043 4.01663 4.14948 4.9002 4.14948 6.01401C4.14948 7.12721 4.99037 8.01086 5.99658 8.01086C7.0028 8.01086 7.84368 7.12721 7.84368 6.01401C7.84368 4.9002 7.00273 4.01663 5.99658 4.01663ZM3.18945 6.01401C3.18945 4.37075 4.43651 3.01245 5.99658 3.01245C7.55666 3.01245 8.80371 4.37075 8.80371 6.01401C8.80371 7.65681 7.55659 9.01504 5.99658 9.01504C4.43657 9.01504 3.18945 7.65681 3.18945 6.01401Z" fill="#EB0203"></path> </svg>
</span>

            </div>
        </div>

        <hr class="my-4">

        
        
            <div class="form-group field-input-label label-animation ct-address-form--input-group
                required">
                <input type="text" title="" class="form-control pwc-form-input js-autofill-enabled " id="name" autocomplete="name" pattern="^[ (),0-9A-Za-zÀ-ÖØ-öø-ÿ]*$" data-missing-error="Campo de preenchimento obrigatório." data-pattern-mismatch="Caracteres inválidos." name="dwfrm_address_name" required="" aria-required="true" value="" maxlength="50">
                <label for="name">
                    * Identificação morada
                </label>
                <div class="invalid-feedback"></div>
            </div>
        

        
        
        <div class="form-group field-input-label label-animation ct-address-form--input-group
            required">
            <input type="text" title="" class="form-control pwc-form-input js-autofill-enabled " id="address1" autocomplete="street-address" data-missing-error="Campo de preenchimento obrigatório." data-pattern-mismatch="Caracteres inválidos." data-strict-input="" name="dwfrm_address_address1" required="" aria-required="true" value="" maxlength="128">
            <label for="address1">
                * Rua
            </label>
            <div class="invalid-feedback"></div>
        </div>
        

        <div class="d-flex justify-content-between ct-address-form--input-group ct-address-form--door-flor-side">
            
            
                <div class="ct-address-form--street-details-container">
                    <div class="form-group field-input-label label-animation
                        required">
                        <input type="text" title="" class="form-control pwc-form-input js-autofill-enabled " id="door" data-missing-error="Campo de preenchimento obrigatório." data-pattern-mismatch="Caracteres inválidos." data-strict-input="" name="dwfrm_address_door" required="" aria-required="true" value="" maxlength="10" pattern="^[-\/a-zA-Z0-9 ]+$">
                        <label for="door">
                            * N°
                        </label>
                        <div class="invalid-feedback"></div>
                    </div>
                </div>
            

            
            
                <div class="ct-address-form--street-details-container">
                    <div class="form-group field-input-label label-animation
                        ">
                        <input type="text" data-pattern-mismatch="Caracteres inválidos." data-strict-input="" title="" class="form-control pwc-form-input js-autofill-enabled " id="floor" name="dwfrm_address_floor" value="" maxlength="10" pattern="^[-º\/a-zA-Z0-9 ]+$">
                        <label for="floor">
                            Andar
                        </label>
                        <div class="invalid-feedback"></div>
                    </div>
                </div>
            

            
            
                <div class="ct-address-form--street-details-container">
                    <div class="form-group field-input-label label-animation
                        ">
                        <input type="text" data-pattern-mismatch="Caracteres inválidos." data-strict-input="" title="" class="form-control pwc-form-input js-autofill-enabled " id="side" name="dwfrm_address_side" value="" maxlength="10" pattern="^[-º\/a-zA-Z0-9 ]+$">

                        <label for="side">
                            Lado
                        </label>
                        <div class="invalid-feedback"></div>
                    </div>
                </div>
            
        </div>

        
        
            <div class="form-group field-input-label label-animation ct-address-form--input-group
                required">
                <input type="text" title="" class="form-control pwc-form-input js-autofill-enabled " id="city" autocomplete="locality" data-missing-error="Campo de preenchimento obrigatório." data-pattern-mismatch="Caracteres inválidos." data-strict-input="" name="dwfrm_address_city" required="" aria-required="true" value="" maxlength="80" minlength="2">
                <label for="city">
                    * Localidade
                </label>
                <div class="invalid-feedback"></div>
            </div>
        

        
        
            <div class="form-group field-input-label label-animation ct-address-form--input-group ct-address-form--reference-points-input-container
                ">
                <textarea class="form-control pwc-form-input ct-address-form--reference-points-input js-autofill-enabled " id="referencePoints" rows="3" data-range-error="Limite máximo 255 caracteres." data-toggle="tooltip" data-placement="top" title="" name="dwfrm_address_referencePoints" value="" maxlength="255" data-original-title="Indique um ponto de referência, que nos ajude a encontrar a sua morada, no caso de surgir alguma dificuldade."></textarea>
                <label for="referencePoints">
                    Pontos de referência
                </label>
                <div class="invalid-feedback"></div>
            </div>
        

        
        
            <div class="form-group pwc-form-checkbox ct-address-form--input-group d-flex justify-content-center mt-4 mb-5 mb-sm-3
                
                
            ">
                <div class="d-block">
                    <input type="checkbox" title="" class="form-control ct-address-form--billing-checkbox" id="billingAddress" name="dwfrm_address_billingAddress" value="true">
                    <span class="checkmark"></span>
                    <label class="pwc-form-check-label my-0" for="billingAddress">
                        Usar como morada de faturação
                    </label>
                    <div class="invalid-feedback"></div>

                    
                </div>
            </div>
        

        <input type="hidden" name="csrf_token" value="xefFRsWQ3vcRH4NTLUDCA6TPPO4CQdtPPLO_M654LXuFv7NPonZa3IxqPLsFuF9II5lH1ey1FqhBsTAuthBKrt4cHczsm_-ENUrsiKH535Wj6WBDeDYST0lcGD-_4WbTXDwlsTcWP9lYxr5GkUCsTfnOcMLRedGmxorxE-ymXtEOKm95Qy0=">
        <input type="hidden" name="is_edit_address" value="false">

        
        <div class="flex-column flex-md-row ct-address-form--input-group ct-new-address-addCTA d-flex mt-4 py-sm-2 w-100 ct-address-form--action-wrapper">
            <button type="submit" name="save" class="ct-address-form--submit-btn button button--primary">
                <span class="account-text">
                    Guardar
                </span>
                <span class="shipping-text">
                    Guardar e Selecionar
                </span>
            </button>

            
        </div>
    </form>

"""
trainset = [
    dspy.Example(
        html_snippet="<label>Username<input autocomplete='username'/></label>",
        retrieved_guidelines="Autocomplete attribute value must contain a valid WCAG 1.3.5 token.",
        evaluation="Pass: Autocomplete value 'username' is valid."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label> Street address<textarea autocomplete='Street-Address'></textarea></label>",
        retrieved_guidelines="Autocomplete attributes can be case-insensitive.",
        evaluation="Pass: Autocomplete value 'Street-Address' is valid."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Work email<input autocomplete='work email'/></label>",
        retrieved_guidelines="Autocomplete must contain an acceptable modifier before the field type.",
        evaluation="Pass: 'work email' is a valid combination."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Username<input autocomplete='badname'/></label>",
        retrieved_guidelines="Autocomplete attribute must use a valid WCAG token.",
        evaluation="Fail: 'badname' is not a recognized autocomplete value."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Email<input autocomplete='work shipping email'/></label>",
        retrieved_guidelines="'work' must not precede 'shipping'.",
        evaluation="Fail: Order of autocomplete tokens is incorrect."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Username<input autocomplete=''/></label>",
        retrieved_guidelines="An empty autocomplete attribute is inapplicable.",
        evaluation="Inapplicable: No autocomplete value provided."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Friend's first name<input type='text' autocomplete='off'/></label>",
        retrieved_guidelines="Autocomplete 'off' makes it inapplicable.",
        evaluation="Inapplicable: Autocomplete is disabled explicitly."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<input type='submit' autocomplete='email'/>",
        retrieved_guidelines="Autocomplete does not apply to submit buttons.",
        evaluation="Inapplicable: Autocomplete attribute is ignored on submit buttons."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>First Name<input autocomplete='family-name'/></label>",
        retrieved_guidelines="The purpose of the form field indicated by the label must correspond with the autocomplete token.",
        evaluation="Fail: 'family-name' should be 'given-name' to match 'First Name' field."
    ).with_inputs("html_snippet", "retrieved_guidelines"),
    dspy.Example(
        html_snippet="<label>Address identification<input autocomplete='name'/></label>",
        retrieved_guidelines="Autocomplete value must match the expected purpose of the field.",
        evaluation="Fail: 'name' is not appropriate for an input related to address."
    ).with_inputs("html_snippet", "retrieved_guidelines")
]


# Compile the model for evaluation
teleprompter = BootstrapFewShot(metric=lambda ex, pred, trace=None: "Pass" in pred.evaluation)
compiled_evaluator = teleprompter.compile(AccessibilityEvaluator(), teacher=AccessibilityEvaluator(passages_per_hop=2), trainset=trainset)

# Run the accessibility evaluation
if html_snippet:
    pred = compiled_evaluator(html_snippet)
    print(f"Accessibility Evaluation: {pred.evaluation}")
    print(f"Retrieved Guidelines: {pred.retrieved_guidelines}")
    print(f"Number of retrieval errors: {counter}")
else:
    print("No HTML content found.")
