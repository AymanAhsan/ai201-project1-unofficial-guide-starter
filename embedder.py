import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from course_normalizer import normalize_course

CHUNKS_PATH = "documents/chunks.json"
CHROMA_PATH = "documents/chroma_db"
COLLECTION_NAME = "reviews"
ENCODE_BATCH = 64
UPSERT_BATCH = 500


def _embed_text(chunk: dict, course_norm: str) -> str:
    """Build the string that gets encoded — includes professor + course so the
    embedding captures who/what context, not just the review sentiment."""
    professor = chunk.get("professor", "Unknown")
    return f"Professor: {professor} | Course: {course_norm}\n{chunk['text']}"


def main() -> None:
    chunks = json.loads(Path(CHUNKS_PATH).read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids, documents, embed_texts, metadatas = [], [], [], []

    for chunk in chunks:
        course_raw = chunk.get("course", "")
        course_norm = normalize_course(course_raw)

        ids.append(str(chunk["chunk_id"]))
        documents.append(chunk["text"])
        embed_texts.append(_embed_text(chunk, course_norm))
        metadatas.append(
            {
                "chunk_id": chunk["chunk_id"],
                "professor": chunk.get("professor", ""),
                "course_raw": course_raw,
                "course_normalized": course_norm,
                "rating": chunk.get("rating", ""),
                "difficulty": chunk.get("difficulty", ""),
            }
        )

    print(f"Encoding {len(embed_texts)} chunks with all-MiniLM-L6-v2...")
    embeddings = model.encode(
        embed_texts, batch_size=ENCODE_BATCH, show_progress_bar=True
    )

    for i in range(0, len(ids), UPSERT_BATCH):
        sl = slice(i, i + UPSERT_BATCH)
        collection.upsert(
            ids=ids[sl],
            embeddings=embeddings[sl].tolist(),
            documents=documents[sl],
            metadatas=metadatas[sl],
        )
        print(f"  upserted {min(i + UPSERT_BATCH, len(ids))}/{len(ids)}")

    print(f"Done. Collection '{COLLECTION_NAME}' now has {collection.count()} entries.")
    print(f"Vector store saved to {CHROMA_PATH}/")


if __name__ == "__main__":
    main()
