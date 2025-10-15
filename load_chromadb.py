import chromadb
import json
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="wcag_guidelines")


with open("./dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

for entry in dataset:
    text = f"{entry['guideline']} - {entry['explanation']} - Best Practice: {entry['best_practice']}"
    embedding = embedding_model.encode(text).tolist()
    collection.add(
        ids=[str(entry["id"])],
        embeddings=[embedding],
        metadatas=[{"field_type": entry["field_type"], "guideline": entry["guideline"]}],
        documents=[text]
    )

print("Dataset loaded into ChromaDB.")
