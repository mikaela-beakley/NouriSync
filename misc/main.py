from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# === Load LLM and tokenizer ===
llm_name = "tiiuae/falcon-rw-1b"  # Or use a smaller one like "tiiuae/falcon-rw-1b"
tokenizer = AutoTokenizer.from_pretrained(llm_name)
model = AutoModelForCausalLM.from_pretrained(llm_name, device_map="auto")  # adjust as needed
generate = pipeline("text-generation", model=model, tokenizer=tokenizer)

# === Sample Knowledge Base ===
documents = [
    "Photosynthesis is the process by which green plants use sunlight to synthesize foods.",
    "The mitochondrion is the powerhouse of the cell.",
    "LLMs use attention mechanisms to capture long-range dependencies in text.",
    "Python is a popular programming language for data science and machine learning."
]

# === Create Embeddings ===
embedder = SentenceTransformer('all-MiniLM-L6-v2')
doc_embeddings = embedder.encode(documents, convert_to_numpy=True)

# === Build FAISS Index ===
index = faiss.IndexFlatL2(doc_embeddings.shape[1])
index.add(doc_embeddings)

# === Ask Questions ===
while True:
    query = input("\nAsk me something (or type 'exit'): ")
    if query.lower() == 'exit':
        break
    
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, k=1)  # top-1 document
    context = documents[I[0][0]]

    prompt = f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {query}\nAnswer:"
    response = generate(prompt, max_new_tokens=100, do_sample=False)[0]['generated_text']
    
    print("\n", response.split("Answer:")[-1].strip())
