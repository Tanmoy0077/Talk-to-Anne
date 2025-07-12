from fastapi import FastAPI
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from app.utils import (
    get_aggregated_query,
    generate_response,
    get_ranked_results,
)

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

static_files_dir = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "dist"
)

app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(static_files_dir, "assets")),
    name="assets",
)


class ChatRequest(BaseModel):
    queries: str
    query: str



@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_files_dir, "index.html"))


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    file_path = os.path.join(static_files_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(static_files_dir, "index.html"))


@app.post("/api/chat")
async def search(request: ChatRequest= Body(...)):
    # vector_docs = get_semantic_retriever(request.query)
    # bm25_results = get_bm25_retriever(request.query)
    # print("Received queries:", request.queries)
    # print("Received query:", request.query)
    structured_query= get_aggregated_query(request.queries, request.query)
    combined_text = get_ranked_results(structured_query)
    response = generate_response(structured_query, combined_text)
    return {"response": response.content}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(PORT))
