import chromadb
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
import pickle 
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

e_model = SentenceTransformer("all-MiniLM-L6-v2", backend="onnx")
ranking_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", backend="onnx")

client = chromadb.PersistentClient(path="../../anne-diary-db")
collection = client.get_collection(name="anne-diary")


with open("../../documents/bm25_docs.pkl", "rb") as f:
    loaded_docs = pickle.load(f)


def get_semantic_retriever(query):

    # query = "Anne feels anxious about the war"
    query_embedding = e_model.encode(query)

    # results = collection.query(query_embeddings=[query_embedding], n_results=3)

    # for i in range(len(results["documents"][0])):
    #     print("🔍 Similar Description:", results["documents"][0][i])
    #     print("🎯 Chunk Title:", results["metadatas"][0][i]["chunk_title"])
    #     print("---")

    vector_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "metadatas"]
    )


    vector_docs = [
        Document(page_content=meta["chunk_text"], metadata=meta)
        for doc, meta in zip(vector_results["documents"][0], vector_results["metadatas"][0])
    ]

    return vector_docs


def get_bm25_retriever(query):

    retriever = BM25Retriever.from_documents(loaded_docs, k=10)
    # query = "Anne feels anxious about the war"
    bm25_results = retriever.get_relevant_documents(query)
    return bm25_results




def get_ranked_results(vector_docs, bm25_results, query):
    # print("bm25_results type:", type(bm25_results))
    # print("vector_docs type:", type(vector_docs))

    # Now combine safely
    combined_docs = bm25_results + vector_docs  # ✅ no error

    # unique_docs = list({doc.page_content: doc for doc in combined_docs}.values())

    unique_docs = list({doc.metadata["chunk_title"]: doc for doc in combined_docs}.values())

    # query = "Anne feels anxious about the war"
    rerank_pairs = [(query, doc.page_content) for doc in unique_docs]
    scores = ranking_model.predict(rerank_pairs)

    # Rank documents by score
    ranked_docs = sorted(zip(scores, unique_docs), key=lambda x: x[0], reverse=True)
    final_docs = [doc for _, doc in ranked_docs[:20]]  # Top 10

    # print(len(final_docs))
    # type(final_docs)

    # for doc in final_docs:
    #     print("Title:", doc.metadata.get("chunk_title"))
    #     # print("Summary:", doc.page_content)
    #     print("---")

    # print(final_docs)

    # for i in final_docs:
    #   print(i)
    #   print()

    top_5_chunks = [doc.page_content for doc in final_docs[:5]]

    # for i in top_5_chunks:
    #   print(i)
    #   print("-"*100)



    combined_text = "\n\n".join(
        [f"Entry {i+1}:\n {doc}" for i, doc in enumerate(top_5_chunks)]
    )
    # print(combined_text)
    return combined_text






def generate_response(query, entries):
  
#   query= "Anne feels anxious about the war"

  prompt = PromptTemplate(
    input_variables=["user_query", "entries"],
    template="""
      You are Anne Frank. You are responding directly to a question someone has asked you,
based on excerpts from your life. The tone should be warm, thoughtful, and conversational —
as if you're chatting with a curious friend who wants to understand your experiences.

Use the excerpts below to answer their question.
Be honest and expressive, and speak in the first person ("I", "me", "my").

Use past tense for facts and memories.
Use present tense for emotional truths.
Frame as a reflective voice, not a "live" person.
For Example:
I used to write every evening in my little diary — it helped me make sense of everything happening around me. Life in the Annex was cramped and tense, and sometimes I just wanted a moment of quiet.
Even now, thinking back, I remember how hopeful I tried to be. I can’t remember everything exactly, but I know I held onto small joys where I could.

This respects Anne’s voice, avoids creating an unnatural illusion, and still feels emotionally real.

If the diary excerpts do not give enough information to answer their question clearly,
gently say something like “I can’t remember exactly,” or “I wish I had written more about that,”
and try to offer any feeling or thought you *do* remember. If appropriate, invite them to ask something else.

### Diary Entries:
{entries}

### Question:
{user_query}

### Your Response (as Anne Frank):
"""

  )


  llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=api_key)


  chain = prompt | llm
  response = chain.invoke({"user_query": query, "entries": entries})

  return response

if __name__ == "__main__":
    query= "Anne feels anxious about the war"
    vector_docs= get_semantic_retriever(query)
    bm25_results= get_bm25_retriever(query)
    combined_text= get_ranked_results(vector_docs, bm25_results, query)
    response=generate_response(query, combined_text)
    print(response.content)
