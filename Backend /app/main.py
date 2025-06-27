from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from utils import *


load_dotenv()

PORT = os.getenv("PORT")

app = FastAPI()


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str

@app.post("/chat/")
async def search(request: ChatRequest):
    vector_docs= get_semantic_retriever(request.query)
    bm25_results= get_bm25_retriever(request.query)
    combined_text= get_ranked_results(vector_docs, bm25_results, request.query)
    response=generate_response(request.query, combined_text)
    return response.content
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
