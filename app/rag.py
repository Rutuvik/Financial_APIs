from sentence_transformers import SentenceTransformer
import chromadb
from PyPDF2 import PdfReader

model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.Client()
collection = client.create_collection("docs")


# -------- TEXT EXTRACTION -------- #
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        return text
    else:
        with open(file_path, "r") as f:
            return f.read()


# -------- INDEXING -------- #
def index_document(doc_id, text):
    # better chunking
    chunks = text.split(".")

    for i, chunk in enumerate(chunks):
        if chunk.strip() == "":
            continue

        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[f"{doc_id}_{i}"],
            embeddings=[embedding],
            documents=[chunk]
        )


# -------- SEARCH + RERANK -------- #
def search(query):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=20
    )

    docs = results["documents"][0]

    # reranking
    scored_results = []

    for doc in docs:
        score = 0
        query_words = query.lower().split()
        doc_lower = doc.lower()

        for word in query_words:
            if word in doc_lower:
                score += 2   # weighted scoring

        scored_results.append((doc, score))

    scored_results.sort(key=lambda x: x[1], reverse=True)

    top_results = [doc for doc, score in scored_results[:5]]

    return {"results": top_results}