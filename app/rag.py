from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.Client()
collection = client.create_collection("docs")


def index_document(doc_id, text):
    chunks = [text[i:i+200] for i in range(0, len(text), 200)]

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[f"{doc_id}_{i}"],
            embeddings=[embedding],
            documents=[chunk]
        )
def search(query):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=20   # get more results first
    )

    docs = results["documents"][0]

    # RERANKING 
    scored_results = []

    for doc in docs:
        score = 0

    
        query_words = query.lower().split()
        doc_lower = doc.lower()

        for word in query_words:
            if word in doc_lower:
                score += 1

        scored_results.append((doc, score))

    
    scored_results.sort(key=lambda x: x[1], reverse=True)
    top_results = [doc for doc, score in scored_results[:5]]
    return {"results": top_results}
