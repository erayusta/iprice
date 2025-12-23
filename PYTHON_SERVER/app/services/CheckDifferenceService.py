import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class CheckDifferenceService:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.threshold = 0.70

    def checkDifference(self, product_1, product_2):
        embedding_1 = self.model.encode([product_1])
        embedding_2 = self.model.encode([product_2])

        similarity_score = cosine_similarity(embedding_1, embedding_2)[0][0]

        is_similar = similarity_score >= self.threshold

        return is_similar, similarity_score