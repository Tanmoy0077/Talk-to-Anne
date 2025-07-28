import pandas as pd
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

df = pd.read_csv("../../documents/diary_summary_output.csv")

embedding_model=GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

client = chromadb.PersistentClient(path="../../anne-diary-db")
collection = client.get_or_create_collection(name="anne-diary")

descriptions = df["description"].tolist()
# print(descriptions)


batch_size = 4
batched_embeddings = []

# Retry settings
max_retries = 5
initial_delay = 180  # seconds

for i in range(0, len(descriptions), batch_size):
    batch = descriptions[i:i + batch_size]

    retries = 0
    while retries <= max_retries:
        try:
            batch_embeddings = embedding_model.embed_documents(batch)
            batched_embeddings.extend(batch_embeddings)
            break  # success, move to next batch
        except Exception as e:
            print(f"❌ Batch {i // batch_size + 1} failed (attempt {retries+1}): {e}")
            retries += 1
            if retries > max_retries:
                print(f"⛔ Skipping batch {i // batch_size + 1} after {max_retries} retries.")
                break
            wait_time = initial_delay * (2 ** (retries - 1))  # exponential backoff
            print(f"⏳ Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

for idx, (embedding, (_, row)) in enumerate(zip(batched_embeddings, df.iterrows())):
    collection.add(
        ids=[f"chunk-{idx}"],
        embeddings=[embedding],
        documents=[row["description"]],
        metadatas=[{
            "chunk_title": row["chunk_title"],
            "chunk_text": row["chunk_text"],
            "people_involved": row["people_involved"]
        }]
    )

# print("Number of documents in collection:", collection.count())

# print("Document IDs:", collection.get()["documents"])
