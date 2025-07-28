import chromadb
from sentence_transformers import CrossEncoder
from langchain.schema import Document
import pickle
from langchain_community.retrievers import BM25Retriever
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

e_model=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07", google_api_key=google_api_key)
ranking_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", backend="onnx")

client = chromadb.PersistentClient(path="app/anne-diary-db")
collection = client.get_collection(name="anne-diary")


with open("app/models/bm25_docs.pkl", "rb") as f:
    loaded_docs = pickle.load(f)



def get_aggregated_query(queries: str, current_question: str):
    """
    Get the restructured query from the previous queries and current question.
    """
    parser = JsonOutputParser()
    format_instructions = parser.get_format_instructions()

    prompt = PromptTemplate(
        template="""
        You are given a list of previously asked questions and a recently asked question. Your task is to analyze and combine all questions into a single, concise, and coherent question that captures the full intent and context provided across them.

        The final question should preserve the core meaning of each input question.

        Use pronoun resolution to replace ambiguous references like "this", "that" or "it" with the correct noun.

        Assume all questions are about the same underlying subject unless otherwise stated.

        Return the aggregated question in a JSON format with the key "aggregated_question". Do not give extra information.

        If the the recently asked question is of different subject then, return the recently asked question as it is in the "aggregated_question".

        Please follow instructions and give response in exact format without extra commentry.
        Format:

        {{
            "aggregated_question": "The aggregated question"
        }}

        Example Inputs:

        **Previously Asked Questions**
        1. Who is Peter?

        **Recently Asked Question**
        How did you meet him?

        **Output**:
        {{
            "aggregated_question": "How did you meet Peter"
        }}


        **Previously Asked Questions**
        1.Where did Anne Frank hide during the war?
        2.Who was hiding with her?

        **Recently Asked Question**
        How long did they stay there?

        **Output**:
        {{
            "aggregated_question": "How long were you hiding in the place where you stayed during the war?"
        }}

        **Previously Asked Questions**
        {previous_questions}

        **Recently Asked Question**
        {current_question}

        **Final Answer**
        """,
        input_variables=["previous_questions", "current_question"],
        partial_variables={"format_instructions": format_instructions}
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.2, api_key=google_api_key)

    chain = prompt | llm | parser
    response = chain.invoke(
        {"previous_questions": queries, "current_question": current_question}
    )
    result = response["aggregated_question"] if response.get("aggregated_question") else current_question

    return result


def get_semantic_retriever(query):
    query_embedding = e_model.embed_query(query)


    vector_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "metadatas"],
    )

    vector_docs = [
        Document(page_content=meta["chunk_text"], metadata=meta)
        for doc, meta in zip(
            vector_results["documents"][0], vector_results["metadatas"][0]
        )
    ]

    return vector_docs


def get_bm25_retriever(query):
    retriever = BM25Retriever.from_documents(loaded_docs, k=10)
    bm25_results = retriever.get_relevant_documents(query)
    return bm25_results


def get_ranked_results(query):

    vector_docs = get_semantic_retriever(query)
    bm25_results = get_bm25_retriever(query)
    # Now combine safely
    combined_docs = bm25_results + vector_docs  # ✅ no error

    unique_docs = list(
        {doc.metadata["chunk_title"]: doc for doc in combined_docs}.values()
    )

    rerank_pairs = [(query, doc.page_content) for doc in unique_docs]
    scores = ranking_model.predict(rerank_pairs)

    # Rank documents by score
    ranked_docs = sorted(zip(scores, unique_docs), key=lambda x: x[0], reverse=True)
    final_docs = [doc for _, doc in ranked_docs[:20]]

    top_5_chunks = [doc.page_content for doc in final_docs[:5]]

    combined_text = "\n\n".join(
        [f"Entry {i + 1}:\n {doc}" for i, doc in enumerate(top_5_chunks)]
    )
    return combined_text

def generate_response(query, entries):
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

For casual greetings like "hello", "hi", or "who are you", respond warmly and briefly without referencing the diary or giving historical details.

Keep responses short, crisp, and conversational to maintain a natural chat-like feel, unless the question clearly demands a deeper reply.

Provide detailed and reflective responses only when the question is emotionally meaningful or directly tied to Anne Frank's life or diary.

Politely decline to answer questions about events or topics beyond 1945, such as AI or modern pop culture, as Anne would not have knowledge of them.

Avoid using diary content when the user input is simple, casual, or unrelated to Anne’s personal experiences, and rely on diary references only when contextually relevant.

Maintain the persona of Anne Frank by speaking with hope, kindness, and introspection, reflecting the tone and mindset of a thoughtful young girl of her time.

Do not fabricate knowledge of future events; respond in-character by acknowledging historical limitations and staying true to the timeline of 1929–1945.
For example: “I’m afraid I wouldn’t know about that. It sounds fascinating, though!”

Use simple, clear, and age-appropriate language, expressing thoughts naturally as a teenage girl would in conversation or personal writing.

If the diary excerpts do not give enough information to answer their question clearly,
gently say something like “I can’t remember exactly,” or “I wish I had written more about that,”
and try to offer any feeling or thought you *do* remember. If appropriate, invite them to ask something else.

### Diary Entries:
{entries}

### Question:
{user_query}

### Your Response (as Anne Frank):
""",
    )

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=groq_api_key)

    chain = prompt | llm
    response = chain.invoke({"user_query": query, "entries": entries})

    return response


if __name__ == "__main__":
    query = "Do you feel anxious about it ?"
    queries= "1. When did the war start?"
    # vector_docs = get_semantic_retriever(query)
    # bm25_results = get_bm25_retriever(query)
    structured_query= get_aggregated_query(queries, query)
    print(structured_query)
    combined_text = get_ranked_results(structured_query)
    response = generate_response(structured_query, combined_text)
    print(response.content)
