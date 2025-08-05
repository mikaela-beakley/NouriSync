import openai
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# === Set OpenAI API Key ===
openai.api_key = "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"

# === Sample Knowledge Base ===
documents = [
    "Photosynthesis is the process by which green plants use sunlight to synthesize foods.",
    "The mitochondrion is the powerhouse of the cell.",
    "LLMs use attention mechanisms to capture long-range dependencies in text.",
    "Python is a popular programming language for data science and machine learning."
]

# === Create Embeddings ===
print("[+] Embedding documents...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
doc_embeddings = embedder.encode(documents, convert_to_numpy=True)

# === Build FAISS Index ===
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)

# === Ask Questions ===
print("[+] Ready. Ask questions about your documents.")
while True:
    query = input("\nAsk me something (or type 'exit'): ")
    if query.lower() == 'exit':
        break

    query_embedding = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, k=1)
    context = documents[I[0][0]]

    prompt = f"""Answer the following question using only the context below. If the answer is not in the context, say "I don't know."

Context:
{context}

Question:
{query}

Answer:"""

    # === GPT-3.5 Turbo Call ===
    client = OpenAI(api_key="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")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    print("\n", response.choices[0].message.content.strip())
