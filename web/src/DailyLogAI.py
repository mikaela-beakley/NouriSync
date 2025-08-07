from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import fitz
import os

class DailyLogAI:
    def __init__(self):
        self.generate = self.load_model()

    def extract_text_from_pdfs(self, folder_path):
        docs = []
        full_path = os.path.join(os.path.dirname(__file__), folder_path)
        for filename in os.listdir(full_path):
            if filename.endswith(".pdf"):
                with fitz.open(os.path.join(full_path, filename)) as doc:
                    text = "".join(page.get_text() for page in doc)
                    docs.append(text)
        return docs

    def chunk_text(self, text, chunk_size=500):
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    def load_model(self, model_id="mistralai/Mistral-7B-Instruct-v0.3"):
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
            use_safetensors=True
        )
        return pipeline("text-generation", model=model, tokenizer=tokenizer)

    def build_faiss_index(self, docs, embedder):
        embeddings = embedder.encode(docs, convert_to_numpy=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index, embeddings
    
   
    def generate_response(self, query, index, embedder, docs, generate):
        query_vec = embedder.encode([query], convert_to_numpy=True)
        _, I = index.search(query_vec, k=3)
        context = "\n\n".join([docs[i] for i in I[0]])

        prompt = f"""[INST] 
        You are a clinical assistant AI that helps analyze outpatient eating behaviors for risk of relapse from eating disorders. Below is a patient's weekly eating habit log. Use the context below (from medical literature) to assess relapse risk, identify any red flags, and provide 1–2 suggestions for intervention.

        If the context doesn’t apply, say "Not enough information."

        Respond only in valid JSON. Do not include any explanation, commentary, or Markdown formatting.

        Context:
        {context}

        Patient log:
        {query}

        Respond in the following exact JSON format:
        {{
        "risk_score": "low" | "moderate" | "high",
        "risk_factors": [
            "Short explanation of reasoning 1",
            "Short explanation of reasoning 2"
        ],
        "plan": [
            {{
            "step": "Actionable recommendation 1",
            "rationale": "Brief justification for step 1",
            "source": "Source or best practice principle"
            }},
            {{
            "step": "Actionable recommendation 2",
            "rationale": "Brief justification for step 2",
            "source": "Source or best practice principle"
            }}
        ]
        }}
        [/INST]
        """

        response = generate(prompt, max_new_tokens=500, do_sample=False)[0]['generated_text']
        response = "\n" +  response.split("[/INST]")[-1].strip()
        return response
    
    def queryLLM(self, query):
        print("[+] Loading Model")
        generate = self.generate

        print("[+] Loading and chunking PDFs...")
        raw_docs = self.extract_text_from_pdfs("pdfs")
        all_chunks = [chunk for doc in raw_docs for chunk in self.chunk_text(doc)]

        print("[+] Embedding documents...")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        index, _ = self.build_faiss_index(all_chunks, embedder)

        return self.generate_response(query, index, embedder, all_chunks, generate)
