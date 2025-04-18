from fastapi import FastAPI, UploadFile, File
from utils.embedding_builder import process_text
from utils.document_processor import generate_tag_list, most_common_tags
from utils.fragment_builder import fragment_text, normalize_text

app = FastAPI()


@app.get("/")
async def get_heartbeat():
    return {"message": "Hello World"}



@app.post("/process/embedding")
async def post_process_embedding(text: str):
    embedding = process_text(text)
    return {
        "text": text,
        "embedding": embedding.tolist()
    }


@app.post("/process/tags")
async def post_process_tags(text: str):
    tags = generate_tag_list(text)
    return {
        "text": text,
        "tags": set(tags)
    }


@app.post("/process/most-common-tags")
async def post_process_most_common_tags(text: str, n: int):
    tags = generate_tag_list(text)
    tags = most_common_tags(tags, n)
    return {
        "text": text,
        "tags": tags
    }


@app.post("/prepare/split-text")
async def post_prepare_split_text(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        return {"error": "Invalid file type. Only text files are allowed."}
    content = await file.read()
    text = content.decode("utf-8")
    normalized_text = normalize_text(text)
    result = fragment_text(normalized_text)
    return result


@app.post("/prepare/normalize")
async def post_prepare_normalize(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        return {"error": "Invalid file type. Only text files are allowed."}
    content = await file.read()
    text = content.decode("utf-8")
    return normalize_text(text)
