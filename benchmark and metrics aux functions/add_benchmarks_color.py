import json
import difflib
import os
from collections import defaultdict

valid_values = {"pass", "fail", "inapplicable"}

with open("results_1.4.1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Define your benchmarks here
benchmarks = {
    "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b": {
        "Nome": "inapplicable",
        "Email": "pass",
        "(+)351 (Portugal) (select)": "inapplicable",
        'Telemóvel': "pass",
        "Password": "pass",
        "Checkbox:Li e aceito as condições de utilização.": "inapplicable"
    },
    "https://store.steampowered.com/join/": {
        "Email Address": "pass",
        "Confirm your address": "pass",
        "Country of Residence (select)": "inapplicable",
        "I am 13 years of age or older and agree to the terms of the Steam Subscriber Agreement and the Valve Privacy Policy.  (checkbox)": "inapplicable"
    },
    "https://www.nba.com/account/sign-up": {
        "Search Players or Teams (search)": "inapplicable",
        "Email": "pass",
        "I agree to the terms(checkbox)" : "inapplicable"
    },    
    "https://www.amazon.com/ap/register?openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fap%2Fcnep%3Fie%3DUTF8%26orig_return_to%3Dhttps%253A%252F%252Fwww.amazon.com%252Fyour-account%26openid.assoc_handle%3Dusflex%26pageId%3Dusflex&prevRID=05AYRRNGN9PBHQCYWN7S&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=usflex&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0": {
        "Your name": "inapplicable",
        "Mobile number or email": "pass",
        "Password": "pass",
        "Re-enter password": "pass",
    },
    "https://www.staples.pt/pt/pt/registo": {
        "Nome": "inapplicable",
        "Email": "pass",
        "Password": "inapplicable",
        "Divulgação a terceiros (checkbox)": "inapplicable",
        "Sim, eu gostaria de receber as comunicações comerciais da Staples Portugal, como descrito na Política de Privacidade. (checkbox)": "inapplicable",
        "Eu concordo com os Termos e Condições da Staples e todos os outros Termos e Políticas que possam ser aplicáveis. (checkbox)": "pass"
    },
    "https://www.infinite.media/bible-gateway/": {
        "First Name": "pass",
        "last Name": "pass",
        "Email": "pass",
        "Organization": "inapplicable",
        "Website": "inapplicable"
    },
    "https://ads.reddit.com/register?utm_source=web3x_consumer&utm_name=left_nav_cta": {
        "Email": "pass",
        "Enter your website to explore": "inapplicable"
    },
    "https://www.ipma.pt/pt/siteinfo/contactar.jsp":{
        "Nome": "inapplicable",
        "Organização": "inapplicable",
        "Email": "pass",
        "Telefone": "inapplicable",
        "Assunto": "inapplicable",
        "Tema": "inapplicable",
        "Mensagem": "inapplicable"
    },
    "https://www.ctt.pt/feapl_2/app/open/postalCodeSearch/postalCodeSearch.jspx?lang=def#fndtn-postalCodeSearchPanel":{
        "Distrito": "inapplicable",
        "Concelho": "inapplicable",
        "Localidade": "inapplicable",
        "Arruamento": "inapplicable",
        "NºPorta": "pass"
    },
    "https://www.cricbuzz.com/info/contact":{
        "Name": "pass",
        "Email": "pass",
        "Subject": "pass",
        "Message": "pass",
        "Upload Screenshot (jpg,png,gif,bmp) (file)": "inapplicable"
    },
    "https://uh.edu/undergraduate-admissions/apply/index":{
        "Search Field": "inapplicable",
        "First Name": "inapplicable",
        "Last Name": "inapplicable",
        "Date of Birth (Month)(select)": "fail",
        "Date of Birth (Day)(select)": "fail",
        "Date of Birth (Year)(select)": "fail",
        "Email Address": "fail",
        "Mobile Phone Number": "fail",
        "You plan to enroll as a:(select)": "fail",
        "When would you like to start classes at UH?(select)": "fail"
    },
    "https://blog.collinsdictionary.com/contact-us/":{
        "First (Name)": "inapplicable",
        "Last (Name)": "inapplicable",
        "Email": "pass",
        "Subject (select)": "pass",
        "Add more subject detail": "inapplicable",
        "Comment or Message": "inapplicable"
    },
    "https://www.livescore.com/en/contact/":{
        "Email Address": "pass",
        "Subject (select)": "pass",
        "Message": "inapplicable"
    },
    "https://www.pexels.com/join-contributor/?redirect_to=%2F":{
        "First name": "pass",
        "Last name": "pass",
        "Email": "pass",
        "Password": "pass"
    },
    "https://www.adsmartfromsky.co.uk/contact-us/":{
        "Your first name": "inapplicable",
        "Your surname": "inapplicable",
        "Company name": "inapplicable",
        "Location": "inapplicable",
        "Telephone": "pass",
        "Email": "pass",
        "Phone (radio)": "pass",
        "Email (radio)": "pass",
        "Agency (radio)": "pass",
        "Direct advertiser (radio)": "pass",
        "Other (radio)": "pass",
        "How did you hear about AdSmart? (select)": "pass",
        "Any comments regarding AdSmart or your business?": "inapplicable",
        "AdSmart from Sky updates (checkbox)": "inapplicable",
    },
    "https://www.zomato.com/deliver-food/":{
        "Please enter phone number": "pass",
        "Please enter name": "inapplicable",
        "Select city": "inapplicable",
        "I hereby consent to receiving communications from Zomato for any relevant opportunities.": "inapplicable"
    }




}

unmatched_fields_by_url = {}
summary_stats = {}
grouped_by_url = defaultdict(list)

# Match benchmark values to each run entry
for entry in data:
    url = entry["url"]
    benchmark_map = benchmarks.get(url, {})
    matched_benchmark_keys = set()
    matched_field_keys = set()

    for field in entry["fields"]:
        ident = field["identification"]
        eval_ = field["evaluation"].strip().lower()

        # Find closest benchmark label
        closest = difflib.get_close_matches(ident, benchmark_map.keys(), n=1, cutoff=0.5)
        if closest:
            matched_benchmark = closest[0]
            benchmark_val = benchmark_map[matched_benchmark].strip().lower()
            field["benchmark"] = benchmark_val

            if eval_ in valid_values and benchmark_val in valid_values:
                field["match"] = "✅" if eval_ == benchmark_val else "❌"
            else:
                field["match"] = ""

            field["reasoning_mismatch"] = False

            matched_benchmark_keys.add(matched_benchmark)
            matched_field_keys.add(ident)
        else:
            field["benchmark"] = "N/A"
            field["match"] = ""
            field["reasoning_mismatch"] = False

    # Identify unmatched predictions and benchmark entries
    predicted_fields = {field["identification"] for field in entry["fields"]}
    benchmark_fields = set(benchmark_map.keys())

    unmatched_predictions = predicted_fields - matched_field_keys
    unmatched_benchmark = benchmark_fields - matched_benchmark_keys

    unmatched_fields_by_url.setdefault(url, {
        "extra_model_fields": [],
        "missing_model_fields": []
    })
    unmatched_fields_by_url[url]["extra_model_fields"].extend(list(unmatched_predictions))
    unmatched_fields_by_url[url]["missing_model_fields"].extend(list(unmatched_benchmark))
    unmatched_fields_by_url[url]["missing_model_fields"].extend([
        {"label": key, "expected": benchmark_map[key]} for key in unmatched_benchmark
    ])
    
    # Add "absent" placeholder for fields missing from model output
    for label in unmatched_benchmark:
        entry["fields"].append({
            "identification": label,
            "evaluation": "absent",
            "benchmark": benchmark_map[label],
            "match": "absent",
            "reasoning_mismatch": False
        })

    matched = sum(1 for f in entry["fields"] if f.get("match") == "✅")
    mismatched = sum(1 for f in entry["fields"] if f.get("match") == "❌")
    absent = sum(1 for f in entry["fields"] if f.get("match") == "absent")
    no_benchmark = len(entry["fields"]) - matched - mismatched - absent

    summary_stats.setdefault(url, []).append({
        "evaluated_fields": len(entry["fields"]),
        "matched": matched,
        "mismatched": mismatched,
        "absent": absent,
        "no_benchmark_found": no_benchmark,
        "submit_clicked": entry.get("submit_clicked", False)
    })

    grouped_by_url[url].append(entry)

# Aggregate field stats
aggregated_results = {}

for url, runs in grouped_by_url.items():
    benchmark_map = benchmarks.get(url, {})
    field_stats = {}

    for run in runs:
        for field in run["fields"]:
            ident = field["identification"]
            eval_ = field["evaluation"].strip().lower()
            match = field.get("match", "")
            benchmark_val = field.get("benchmark", "N/A")
            reasoning_mismatch = field.get("reasoning_mismatch", False)

            if ident not in field_stats:
                field_stats[ident] = {
                    "total_evaluations": 0,
                    "matches": 0,
                    "mismatches": 0,
                    "absent": 0,
                    "reasoning_mismatches": 0,
                    "benchmark": benchmark_val,
                    "evaluations": []
                }

            field_stats[ident]["total_evaluations"] += 1
            if match == "✅":
                field_stats[ident]["matches"] += 1
            elif match == "❌":
                field_stats[ident]["mismatches"] += 1
            elif match == "absent":
                field_stats[ident]["absent"] += 1

            if reasoning_mismatch:
                field_stats[ident]["reasoning_mismatches"] += 1

            field_stats[ident]["evaluations"].append(eval_)

    aggregated_results[url] = field_stats

# Save updated results
with open("results_with_benchmarks_1.4.1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

#with open("unmatched_fields_report.json", "w", encoding="utf-8") as f:
#    json.dump(unmatched_fields_by_url, f, indent=4, ensure_ascii=False)