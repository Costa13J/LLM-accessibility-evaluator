import os
import dspy
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from dspy.retrieve.chromadb_rm import ChromadbRM

load_dotenv()
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY", "")

if not os.environ["MISTRAL_API_KEY"]:
    raise ValueError("MISTRAL_API_KEY not found. Check your .env file.")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="wcag_guidelines")


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

crm = ChromadbRM(
    collection_name="wcag_guidelines",
    persist_directory="./chroma_db",
    embedding_function=embedding_model.encode,
    k=8  # top-k
)

# Configure DSPy with the model and retriever
mini = dspy.LM('mistral/mistral-large-latest')
dspy.settings.configure(lm=mini, rm=crm)

#Lança submit
url = "https://store.steampowered.com/join/?redir=app%2F2669320%2FEA_SPORTS_FC_25%2F%3Fsnr%3D1_4_4__129_1&snr=1_60_4__62"
#url = "https://login.telecom.pt/Public/Register.aspx?appKey=Xa6qa5wG2b"
#url = "https://www.nba.com/account/sign-up" #página mudou, agora tem um captcha que é o único a lançar msg de erro //// Avaliação longa, por vezes fica cortada
#url = "https://www.amazon.com/ap/register?openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fap%2Fcnep%3Fie%3DUTF8%26orig_return_to%3Dhttps%253A%252F%252Fwww.amazon.com%252Fyour-account%26openid.assoc_handle%3Dusflex%26pageId%3Dusflex&prevRID=05AYRRNGN9PBHQCYWN7S&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=usflex&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"

#url = "https://www.ilovepdf.com/contact" #Não captura mutations agora CHECKAR
#url = "https://support.fandango.com/fandangosupport/s/contactsupport" # não captura mutations, precisa de um time sleep sq

#url = "https://www.staples.pt/pt/pt/registo" #aconteceu token exceed 1 vez
#url = "https://www.infinite.media/bible-gateway/"
#url = "https://ads.reddit.com/register?utm_source=web3x_consumer&utm_name=left_nav_cta" 
#url = "https://www.ipma.pt/pt/siteinfo/contactar.jsp" 
#url = "https://www.ctt.pt/feapl_2/app/open/postalCodeSearch/postalCodeSearch.jspx?lang=def#fndtn-postalCodeSearchPanel" #Avaliação longa, por vezes fica cortada
#url = "https://doctor.webmd.com/learnmore/profile"

#url = "https://www.cricbuzz.com/info/contact"

#url = "https://www.net-empregos.com/" #submeter empty form lança a pesquisa porque nada é required, válido
#url = "https://www.continente.pt/loja-online/contactos/" #Apanhar o botão de submeter do 2nd form que é para a newsletter e so tem um field ahahahaha, válido kinda 


#WRONG BUTTON
#url = "https://www.medicalnewstoday.com/articles/323586#bmi-calculators" #Wrong button selected -> selected the subscribe button instead of the calculate
#url="https://www.business.reddit.com/speak-with-a-reddit-ads-expert?utm_product=ads-register-landing-page_product&utm_source=web3x_consumer" # Escolhe o botão errado (Confirm my choices em vez de book meeting)
#url = "https://appserver2.ctt.pt/feapl_2/app/open/stationSearch/stationSearch.jspx?lang=def" #can't locate submit button, returns none

#REFRESH DA PÁGINA
#url = "https://suporte.decathlon.pt/hc/pt/requests/new?ticket_form_id=4421041894417" #REFRESH DA PAGINA AO SUBMETER -> Não são apanhadas mutações
#url = "https://www.gsmarena.com/tipus.php3" #Cant get the button, but even if it could, the errors are shown after a refresh, so no mutations

#CAPTCHA CLICK
#url = "https://cam.merriam-webster.com/registration?utm_source=mw&utm_medium=global-nav-join&utm_campaign=evergreen&partnerCode=default_partner&_gl=1*s07wn2*_ga*NjcwNzY4MzE2LjE3MzkwMzc0NzA.*_ga_821K16B669*MTczOTAzNzQ3MC4xLjAuMTczOTAzNzQ3MC4wLjAuMA..&offerCode=mwu-monthly-free-trial" #cloudaflare verification before submit button becomes available -> need to click the captcha CHECKAR
#url = "https://support.discord.com/hc/en-us/requests/new?ticket_form_id=360006586013"# Verifica se és humano e não és

#BOTAO BLOQUEADO
#url = "https://appserver2.ctt.pt/femgu/app/open/enroll/showUserEnrollAction.jspx?lang=def&redirect=https://www.ctt.pt/ajuda/particulares/receber/gerir-correio-e-encomendas/reter-tudo-que-recebo-numa-loja-ctt#fndtn-panel2-2" #COOKIES ANTES E DPS BOTAO BLOQUEADO SE NAO SELCIONAR UMA CHECKBOX ANTES
#url = "https://www.istockphoto.com/customer-support"# coonsent options in the way

#Não IDENTIFICA FIELDS OU BOTAO
#url = "https://www.accuweather.com/en/contact"#identifica o botão as vezes mas não consegue carregar nele
#url = "https://business.trustpilot.com/signup?cta=free-signup_header_home"# não identifica fields
#url = "https://www.continente.pt/checkout/entrega/" #Nao apanha fields nem buttons

#NO FORM ON PAGE
#url = "https://business.quora.com/contact-us/" #form so fica disponivel depois de carrgar no botaão "booka a call"
#url = "https://cookpad.com/us/premium_signup/unified_subscription_purchases/new?web_subscription_plan_id=47" #No form on page


#Preciso estar logged - nao funciona
#url = "https://loja.meo.pt/compra?modalidade-compra=pronto-pagamento" 
#url = "https://www.decathlon.pt/p-r/calcado-de-caminhada-merrell-crosslander-mulher/_/R-p-X8761333?mc=8761333&offer=8761333" 
#url = "https://www.decathlon.pt/checkout/shipping" 
#url = "https://www.amazon.com/checkout/p/p-106-8712704-0157058/address?pipelineType=Chewbacca&referrer=address" 
#url = "https://contribute.imdb.com/updates/edit?update=title&ref_=czone_ra_new_title"
#url = "https://www.etsy.com/your/shops/me/onboarding/listing-editor/create#about"
#url = "https://genius.com/new"