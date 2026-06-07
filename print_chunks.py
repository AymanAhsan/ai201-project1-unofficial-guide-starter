import chromadb

client = chromadb.PersistentClient(path="documents/chroma_db")
collection = client.get_collection("reviews")

result = collection.get(include=["documents", "metadatas"])

print(f"{'ID':>4}  {'Professor':<30}  {'Course':^12}  {'Rating':^6}  {'Diff':^6}  Text")
print("-" * 120)
# Similarity values are based on cosine similarity, where 0 is identifical, and 2 is maxmially different.
for doc, meta in zip(result["documents"], result["metadatas"]):
    snippet = doc.replace("\n", " ")[:70]
    print(
        f"{meta['chunk_id']:>4}  "
        f"{meta['professor']:<30}  "
        f"{meta['course_normalized']:^12}  "
        f"{meta['rating']:^6}  "
        f"{meta['difficulty']:^6}  "
        f"{snippet}"
    )
