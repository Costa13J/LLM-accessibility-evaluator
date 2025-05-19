import json
import difflib

valid_values = {"pass", "fail", "inapplicable"}

with open("results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Define your benchmarks here
benchmarks = {
    "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b": {
        "Nome": "fail",
        "Email": "fail",
        "(+)351 (Portugal) (select)": "pass",
        'Telemóvel': "pass",
        "Password": "fail",
        "Checkbox:Li e aceito as condições de utilização.": "fail"
    },
    "https://store.steampowered.com/join/?redir=app%2F2669320%2FEA_SPORTS_FC_25%2F%3Fsnr%3D1_4_4__129_1&snr=1_60_4__62": {
        "Endereço de e-mail": "fail",
        "Confirma o teu endereço": "fail",
        "País de residência (select)": "fail",
        "Tenho 13 anos ou mais de idade e concordo com os termos do Acordo de Subscrição Steam e da Política de Privacidade da Valve. (checkbox)": "fail"
    },
    "https://www.nba.com/account/sign-up": {
        "Email": "fail",
        "Password": "fail",
        "First Name (optional)": "pass",
        "Last Name (optional)": "pass",
        "Data de nascimento (MM)": "fail",
        "Data de nascimento (AAAA)": "fail",
        "País/Região/Território (select)": "fail",
        "Termos de responsabilidade (checkbox)" : "fail",
        "Informação pessoal (checkbox)": "pass"
    },
    "https://appserver2.ctt.pt/feapl_2/app/open/stationSearch/stationSearch.jspx?lang=def":{
        "Distrito (select)": "pass",
        "Concelho (select)": "pass",
        "Freguesia (select)": "pass",
        "Localização": "pass",
        "Horário (select)": "pass",
        "Aberto depois das 18h (checkbox)": "pass",
        "Aberto aos sábados e domingos (checkbox)": "pass"
    },
    "https://www.amazon.com/ap/register?openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fap%2Fcnep%3Fie%3DUTF8%26orig_return_to%3Dhttps%253A%252F%252Fwww.amazon.com%252Fyour-account%26openid.assoc_handle%3Dusflex%26pageId%3Dusflex&prevRID=05AYRRNGN9PBHQCYWN7S&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=usflex&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0": {
        "Enter your mobile number or email": "fail"
    },
    "https://www.ilovepdf.com/contact":{
        "Your Name": "pass",
        "Your Email": "pass",
        "Subject (select)": "fail",
        "Message": "fail",
        "I accept Terms & Conditions and Legal & Privacy (checkbox)" : "fail",
        "Informação pessoal (checkbox)": "pass"
    },
    "https://support.fandango.com/fandangosupport/s/contactsupport": {
        "First Name (Required)": "pass",
        "Last Name (Required)": "pass",
        "Email (Required)": "pass",
        "Phone (Required)": "pass",
        "Subject (Required)": "pass",
        "Brand (Required) (select)": "pass",
        "How Can We Help? (Required) (textarea)": "pass"
    }
}

# To store unmatched info
unmatched_fields_by_url = {}

for entry in data:
    url = entry["url"]
    benchmark_map = benchmarks.get(url, {})
    matched_benchmark_keys = set()
    matched_field_keys = set()

    for field in entry["fields"]:
        ident = field["identification"]
        eval_ = field["evaluation"].strip().lower()

        # Try to find a close benchmark label
        closest = difflib.get_close_matches(ident, benchmark_map.keys(), n=1, cutoff=0.5)
        if closest:
            matched_benchmark = closest[0]
            benchmark_val = benchmark_map[matched_benchmark].strip().lower()
            field["benchmark"] = benchmark_val

            if eval_ in valid_values and benchmark_val in valid_values:
                field["match"] = "✅" if eval_ == benchmark_val else "❌"
            else:
                field["match"] = ""

            matched_benchmark_keys.add(matched_benchmark)
            matched_field_keys.add(ident)

        else:
            field["benchmark"] = "N/A"
            field["match"] = ""

    # Identify unmatched predictions and benchmark entries
    predicted_fields = {field["identification"] for field in entry["fields"]}
    benchmark_fields = set(benchmark_map.keys())

    unmatched_predictions = predicted_fields - matched_field_keys
    unmatched_benchmark = benchmark_fields - matched_benchmark_keys

    unmatched_fields_by_url[url] = {
        "extra_model_fields": list(unmatched_predictions),
        "missing_model_fields": list(unmatched_benchmark)
    }

# Save enriched comparison
with open("results_with_benchmarks.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

# Save unmatched field report
with open("unmatched_fields_report.json", "w", encoding="utf-8") as f:
    json.dump(unmatched_fields_by_url, f, indent=4, ensure_ascii=False)