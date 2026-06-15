"""
NLP Intent Classifier using sentence-transformers + FAISS
Hybrid: High confidence -> Rule Engine
Low confidence -> LLM Fallback
"""

import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class IntentClassifier:
    def __init__(self, kb_path="knowledge_base/gst_rules.json"):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.kb = self._load_kb(kb_path)
        self.index, self.questions = self._build_faiss_index()

    def _load_kb(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _build_faiss_index(self):
        questions = [faq['question'] for faq in self.kb.get('faqs', [])]
        if not questions:
            questions = ["What is GSTR-1 due date?", "How to calculate late fee?", "ITC eligibility?"]
        embeddings = self.model.encode(questions)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        return index, questions

    def classify(self, query: str, threshold=0.75):
        query_emb = self.model.encode([query])
        distances, indices = self.index.search(query_emb.astype('float32'), k=1)
        confidence = 1 - (distances[0][0] / 100)  # Rough normalization
        if confidence > threshold and indices[0][0] < len(self.questions):
            matched_q = self.questions[indices[0][0]]
            for faq in self.kb.get('faqs', []):
                if faq['question'] == matched_q:
                    return {
                        "intent": faq.get('intent', 'general'),
                        "confidence": round(confidence, 2),
                        "answer": faq['answer'],
                        "action": faq.get('action', '')
                    }
        return {"intent": "general", "confidence": round(confidence, 2), "answer": None}