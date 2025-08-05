from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import fitz
import os

def extract_text_from_pdfs(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            with fitz.open(os.path.join(folder_path, filename)) as doc:
                text = "".join(page.get_text() for page in doc)
                docs.append(text)
    return docs

def chunk_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def load_model(model_id="mistralai/Mistral-7B-Instruct-v0.3"):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
        use_safetensors=True
    )
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

def build_faiss_index(docs, embedder):
    embeddings = embedder.encode(docs, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings

def run_qa_loop(docs, index, embedder, generate):
    print("[+] Model is ready! Ask your questions.")
    while True:
        query = input("\nAsk me something (or type 'exit'): ")
        if query.lower() == 'exit':
            break

        query_vec = embedder.encode([query], convert_to_numpy=True)
        _, I = index.search(query_vec, k=3)
        context = "\n\n".join([docs[i] for i in I[0]])

        prompt = f"""[INST] Use the context below to help answer the user's question. Be really understanding and helpful. Be kind, sweet, caring, and talk to the user like they are someone important to you.

Context:
{context}

Question:
{query}
[/INST]
"""

        response = generate(prompt, max_new_tokens=200, do_sample=False)[0]['generated_text']
        print("\n", response.split("[/INST]")[-1].strip())

# === Entry Point ===
if __name__ == "__main__":
    print("[+] Loading Mistral model...")
    generate = load_model()

    print("[+] Loading and chunking PDFs...")
    raw_docs = extract_text_from_pdfs("pdfs")
    all_chunks = [chunk for doc in raw_docs for chunk in chunk_text(doc)]

    print("[+] Embedding documents...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    index, _ = build_faiss_index(all_chunks, embedder)

    run_qa_loop(all_chunks, index, embedder, generate)
