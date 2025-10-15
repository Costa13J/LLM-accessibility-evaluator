import os
import dspy
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from dspy.retrieve.chromadb_rm import ChromadbRM

load_dotenv(override=True)

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

#Language models
mistral = dspy.LM('mistral/mistral-large-latest')
mini = dspy.LM("openai/gpt-4o-mini-2024-07-18")
quatro = dspy.LM("openai/gpt-4o-2024-08-06")
quatroum = dspy.LM("openai/gpt-4.1-2025-04-14")
quatroummini = dspy.LM("openai/gpt-4.1-mini-2025-04-14")
cinco = dspy.LM("openai/gpt-5", max_tokens=None, temperature=None)

# Configure DSPy with the models to use and retriever
dspy.settings.configure(lm=mistral, rm=crm)

# Final URL list
url = "https://store.steampowered.com/join/"
#url = "https://www.nba.com/account/sign-up" 
#url = "https://www.infinite.media/bible-gateway/" 
#url = "https://www.cricbuzz.com/info/contact"
#url = "https://www.amazon.com/ap/register?openid.pape.max_auth_age=900&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fap%2Fcnep%3Fie%3DUTF8%26orig_return_to%3Dhttps%253A%252F%252Fwww.amazon.com%252Fyour-account%26openid.assoc_handle%3Dusflex%26pageId%3Dusflex&prevRID=05AYRRNGN9PBHQCYWN7S&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&prepopulatedLoginId=&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=usflex&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
#url = "https://www.livescore.com/en/contact/"
#url = "https://uh.edu/undergraduate-admissions/apply/index" 
#url = "https://www.adsmartfromsky.co.uk/contact-us/"
#url = "https://blog.collinsdictionary.com/contact-us/"
#url = "https://www.pexels.com/join-contributor/?redirect_to=%2F"
#url = "https://www.zomato.com/deliver-food/" 
