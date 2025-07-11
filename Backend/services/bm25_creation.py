import pandas as pd
from langchain.schema import Document
import pickle
# from langchain_community.retrievers import BM25Retriever

# Step1: Loading CSV
df = pd.read_csv("../../documents/diary_summary_output.csv")

# Step2: Converting each row to langchain document
documents = []
for _, row in df.iterrows():
    doc = Document(
        page_content=row["chunk_text"],
        metadata={
            "chunk_title": row["chunk_title"],
            "description": row["description"],
            "people_involved": row["people_involved"]
        }
    )
    documents.append(doc)

# print(documents)

# Step3: Saving document object for retrieval 
with open("../../documents/bm25_docs.pkl", "wb") as f:
    pickle.dump(documents, f)

# retriever = BM25Retriever.from_documents(documents, k=10)
# query = "Anne feels anxious about the war"
# bm25_results = retriever.get_relevant_documents(query)

# for doc in bm25_results:
#     # print(doc.page_content,doc.metadata)
#     print(doc.page_content,doc.metadata)
#     print("---")
