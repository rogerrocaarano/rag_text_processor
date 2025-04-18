from sentence_transformers import SentenceTransformer

model_str = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_str)

def process_text(text: str):
    embedding = model.encode(text)
    return embedding