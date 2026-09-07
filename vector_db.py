import os
import json
import numpy as np

FAISS_AVAILABLE = False
SENTENCE_TRANSFORMERS_AVAILABLE = False
SKLEARN_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

from config import FAISS_INDEX_DIR

class HealthcareVectorStore:
    def __init__(self, collection_name="medical_knowledge"):
        self.collection_name = collection_name
        self.documents = [] # list of dicts: {"id": str, "content": str, "metadata": dict}
        self.encoder = None
        self.tfidf = None
        self.tfidf_matrix = None
        self.faiss_index = None
        
        # Load embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[VectorStore] Could not load SentenceTransformer: {e}")
                self.encoder = None

    def add_documents(self, docs):
        """
        docs: list of dicts, e.g. [{"id": "doc1", "content": "text...", "metadata": {...}}, ...]
        """
        for doc in docs:
            # Avoid duplicate document IDs
            if not any(d["id"] == doc["id"] for d in self.documents):
                self.documents.append(doc)
        
        self._rebuild_index()

    def _rebuild_index(self):
        if not self.documents:
            return

        texts = [doc["content"] for doc in self.documents]

        if FAISS_AVAILABLE and self.encoder is not None:
            try:
                embeddings = self.encoder.encode(texts, convert_to_numpy=True)
                dim = embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatL2(dim)
                self.faiss_index.add(embeddings.astype('float32'))
                return
            except Exception as e:
                print(f"[VectorStore] FAISS index creation failed: {e}")

        # Fallback: TF-IDF Vectorizer
        if SKLEARN_AVAILABLE:
            try:
                self.tfidf = TfidfVectorizer(stop_words='english')
                self.tfidf_matrix = self.tfidf.fit_transform(texts)
            except Exception as e:
                print(f"[VectorStore] TF-IDF indexing failed: {e}")

    def similarity_search(self, query, top_k=3):
        if not self.documents:
            return []

        results = []

        # 1. FAISS Search
        if FAISS_AVAILABLE and self.faiss_index is not None and self.encoder is not None:
            try:
                query_vec = self.encoder.encode([query], convert_to_numpy=True).astype('float32')
                distances, indices = self.faiss_index.search(query_vec, min(top_k, len(self.documents)))
                for idx, dist in zip(indices[0], distances[0]):
                    if idx < len(self.documents) and idx >= 0:
                        doc = self.documents[idx].copy()
                        doc["score"] = float(round(1.0 / (1.0 + float(dist)), 4))
                        results.append(doc)
                return results
            except Exception as e:
                print(f"[VectorStore] FAISS search error: {e}")

        # 2. TF-IDF Cosine Similarity Fallback
        if SKLEARN_AVAILABLE and self.tfidf is not None and self.tfidf_matrix is not None:
            try:
                query_vec = self.tfidf.transform([query])
                scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
                top_indices = np.argsort(scores)[::-1][:top_k]
                
                for idx in top_indices:
                    score = float(scores[idx])
                    if score > 0.001:
                        doc = self.documents[idx].copy()
                        doc["score"] = round(score, 4)
                        results.append(doc)
                return results
            except Exception as e:
                print(f"[VectorStore] TF-IDF search error: {e}")

        # 3. Pure Python Keyword Similarity Fallback
        query_words = set(query.lower().split())
        for doc in self.documents:
            content_words = set(doc["content"].lower().split())
            match_count = len(query_words.intersection(content_words))
            match_score = match_count / max(1, len(query_words))
            if match_score > 0:
                d = doc.copy()
                d["score"] = round(match_score, 4)
                results.append(d)

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    def get_all_documents(self):
        return self.documents

# Global store instances
patient_vector_store = HealthcareVectorStore("patient_records")
medical_knowledge_vector_store = HealthcareVectorStore("medical_knowledge")
