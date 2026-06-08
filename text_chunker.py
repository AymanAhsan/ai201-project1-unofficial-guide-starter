import json
from pathlib import Path


def chunk_reviews(filepath: str) -> list[dict]:
    """
    Paragraph-chunk a reviews file where entries are separated by '---'.
    Each chunk preserves the full review entry as one unit.
    """
    text = Path(filepath).read_text(encoding="utf-8")
    raw_chunks = text.split("---")

    chunks = []
    for i, block in enumerate(raw_chunks):
        block = block.strip()
        if not block:
            continue

        chunk = {"chunk_id": i, "text": block}

        # Extract metadata from the header line if present
        lines = block.splitlines()
        header = next((l for l in lines if "|" in l), "")
        if "|" in header:
            parts = [p.strip() for p in header.split("|")]
            for part in parts:
                if part.startswith("Professor:"):
                    chunk["professor"] = part.removeprefix("Professor:").strip()
                elif part.startswith("Course:"):
                    chunk["course"] = part.removeprefix("Course:").strip()
                elif part.startswith("Rating:"):
                    chunk["rating"] = part.removeprefix("Rating:").strip()
                elif part.startswith("Difficulty:"):
                    chunk["difficulty"] = part.removeprefix("Difficulty:").strip()

        chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    reviews_path = "documents/reviews.txt"
    chunks = chunk_reviews(reviews_path)

    print(f"Total chunks: {len(chunks)}\n")
    for chunk in chunks[:5]:  # Print the first 5 chunks for verification
        print(f"--- Chunk {chunk['chunk_id']} ---")
        print(f"Professor : {chunk.get('professor', 'N/A')}")
        print(f"Course    : {chunk.get('course', 'N/A')}")
        print(f"Rating    : {chunk.get('rating', 'N/A')}")
        print(f"Text      :\n{chunk['text']}\n")

    output_path = "documents/chunks.json"
    Path(output_path).write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"All chunks saved to {output_path}")
