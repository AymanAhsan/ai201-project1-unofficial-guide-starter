import os
from dotenv import load_dotenv

import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_PATH = "documents/chroma_db"
COLLECTION_NAME = "reviews"
TOP_K = 10
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful academic advisor for CCNY students.
Answer questions strictly based on the student reviews provided below.
If the reviews do not contain enough information to answer, say so — do not make up details.
Be concise and cite specific professors, courses, or ratings when relevant."""


def retrieve(collection, model: SentenceTransformer, query: str) -> list[dict]:
    embedding = model.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({"text": doc, "metadata": meta, "score": round(1 - dist, 4)})
    return chunks


def build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        m = c["metadata"]
        chunk_id = m.get("chunk_id", "?")
        header = (
            f"[Review #{chunk_id}] Professor: {m.get('professor', '?')} | "
            f"Course: {m.get('course_normalized', m.get('course_raw', '?'))} | "
            f"Rating: {m.get('rating', '?')} | "
            f"Difficulty: {m.get('difficulty', '?')} | "
            f"Score: {c['score']}"
        )
        parts.append(f"{header}\n{c['text']}")
    return "\n\n".join(parts)


def ask(client: Groq, question: str, context: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Student reviews:\n\n{context}\n\nQuestion: {question}",
            },
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def main() -> None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client_chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client_chroma.get_collection(COLLECTION_NAME)
    print(f"Connected to ChromaDB — {collection.count()} vectors\n")

    groq = Groq(api_key=api_key)

    print("Ask questions about CCNY Math professors (type 'quit' to exit)\n")
    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break

        chunks = retrieve(collection, model, question)
        context = build_context(chunks)
        answer = ask(groq, question, context)

        print(f"\nAssistant: {answer}\n")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
