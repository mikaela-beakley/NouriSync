import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import json
import os

class EmotionAI:

    def __init__(self):
        pass
    
    def get_emotions(self, query):
        # === Paths ===
        MODEL_DIR = "model"
        LABEL_FILE = os.path.join(MODEL_DIR, "label_names.json")

        # === Define emotion and behavior groups ===
        EMOTION_LABELS = {
            "guilt", "anxiety", "shame", "sadness", "fear", "hopelessness",
            "self_criticism", "embarrassment", "hope", "confidence", "calm",
            "self_acceptance", "gratitude", "relief", "pride", "motivation"
        }

        # Everything else = behavior (fallback)
        def get_label_type(label):
            return "Emotion" if label in EMOTION_LABELS else "Behavior"

        # === Load model and tokenizer ===
        print("🔁 Loading model and tokenizer...")
        tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
        model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
        model.eval()

        # === Load label names ===
        with open(LABEL_FILE, "r") as f:
            label_names = json.load(f)


        # === Tokenize input ===
        inputs = tokenizer(query, return_tensors="pt", truncation=True, padding=True)

        # === Predict ===
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.sigmoid(outputs.logits).squeeze().tolist()

        # === Get Top 5 predictions ===
        top_n = 5
        top_indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:top_n]

        emotions = label_names[top_indices[0]] + ", " + label_names[top_indices[1]]

        return emotions
        # print("-" * 30)
        # for i in top_indices:
        #     label = label_names[i]
        #     label_type = get_label_type(label)
        #     prob = probs[i]
        #     print(f"{label} ({label_type}): {prob:.3f}")