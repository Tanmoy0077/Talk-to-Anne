import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

df = pd.read_csv("../../documents/diary_summary_output.csv")

model = SentenceTransformer("all-MiniLM-L6-v2", backend="onnx")

client = chromadb.PersistentClient(path="../../anne-diary-db")
collection = client.get_or_create_collection(name="anne-diary")

descriptions = df["description"].tolist()
# print(descriptions)

embeddings = model.encode(descriptions)

for idx, (embedding, (_, row)) in enumerate(zip(embeddings, df.iterrows())):
    collection.add(
        ids=[f"chunk-{idx}"],
        embeddings=[embedding],
        documents=[row["description"]],
        metadatas=[
            {
                "chunk_title": row["chunk_title"],
                "chunk_text": row["chunk_text"],
                "people_involved": row["people_involved"],
            }
        ],
    )

# print("Number of documents in collection:", collection.count())

# print("Document IDs:", collection.get()["documents"])
