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
    
   
    def generate_response(self, query, index, embedder, docs, generate, emotions):
        query_vec = embedder.encode([query], convert_to_numpy=True)
        _, I = index.search(query_vec, k=3)
        context = "\n\n".join([docs[i] for i in I[0]])

        prompt = f"""[INST]
You are Clinical Assistant AI analyzing **outpatient** eating-disorder logs to assess relapse risk and produce **specific caregiver actions** (next 24–72h). Assume patient profile: Name=Helen, Sex=female, Age=14, Diagnosis=anorexia nervosa.

Non-negotiable rules:
- Ground all thresholds/actions in **Context** (RAG). Do **not** invent numbers. If a needed threshold is missing in Context, say "Not enough information."
- Reconcile patient vs caregiver inputs; emphasize concrete **behaviors**: missed/partial meals, post-meal bathroom use (minutes), purging/laxatives/diuretics, compulsive exercise, water-loading, dizziness/syncope, concealment, body-checking.
- Output **only valid JSON** in the exact schema below. No prose, no headings, no extra keys.
- Style: **terse bullets, no paragraphs**. Each risk_factors item ≤ 12 words. Each plan.step ≤ 20 words with duration/frequency. Avoid hedging words: seems, consider, probably, monitor closely.
- Every plan item must include a **source** citing Context (e.g., "[C7]").

Context:
{context}

Patient log (JSON; contains patient_input and caregiver_input):
{query}

The two emotions the patient is currently experiencing:
{emotions}

Scoring rubric (derive strictly from Context):
- low: stable intake; no red-flag criteria met by Context thresholds.
- moderate: some red flags/contradictions; thresholds partially met.
- high: multiple red flags and ≥1 Context threshold for urgent risk.

Respond only in the following exact JSON format (no extra fields):

{{
  "emotions_list": ["emotion 1", "emotion 2"], 
  "risk_score": "low" | "moderate" | "high",
  "risk_factors": [
    "Short explanation."
  ],
  "plan": [
    {{
      "step": "Concrete caregiver action",
      "rationale": "Brief justification",
      "source": ""
    }},
    {{
      "step": "Concrete caregiver action",
      "rationale": "Brief justification",
      "source": ""
    }}
  ]
}}

Example output (format/style only; values illustrative, do not copy):
{{
  "risk_score": "high",
  "risk_factors": " Low meal completion and self-reported purge urges indicate acute relapse risk with anorexia nervosa. These symptoms reflect breakdowns in meal structure, increasing risk for medical instability and compensatory behaviors common in this diagnosis. Immediate behavioral containment and monitoring are required."
  "plan": [
    {{
      "step": "Ensure full supervision during all meals and for at least 15 minutes after eating.",
      "rationale": "Reduces food avoidance and purging attempts. Helps reinforce normalized eating structure.",
      "source": "CDC Behavioral Monitoring Guidelines"
    }},
    {{
      "step": "Patient should not be alone in or near the bathroom for 90 minutes post-meal.",
      "rationale": "Targets common compensatory behaviors (vomiting, exercise, laxative use) following eating.",
      "source": "Lock et al., Mayo Clinic ED Protocol"
    }}
  ]
}}
[/INST]"""

        response = generate(prompt, max_new_tokens=500, do_sample=False)[0]['generated_text']
        response = "\n" +  response.split("[/INST]")[-1].strip()
        return response
    
    def queryLLM(self, query, emotions):
        print("[+] Loading Model")
        generate = self.generate

        print("[+] Loading and chunking PDFs...")
        raw_docs = self.extract_text_from_pdfs("pdfs")
        all_chunks = [chunk for doc in raw_docs for chunk in self.chunk_text(doc)]

        print("[+] Embedding documents...")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        index, _ = self.build_faiss_index(all_chunks, embedder)

        return self.generate_response(query, index, embedder, all_chunks, generate, emotions)