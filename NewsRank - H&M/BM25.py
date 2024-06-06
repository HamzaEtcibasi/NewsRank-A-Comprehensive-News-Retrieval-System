import nltk
import math
class BM25:
    def __init__(self, inverted_index, doc_lengths, k1=1.5, b=0.75):
        self.inverted_index = inverted_index
        self.doc_lengths = doc_lengths
        self.avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)
        self.k1 = k1
        self.b = b
        self.N = len(doc_lengths)
        self.idf_cache = {}

    def idf(self, term):
        if term not in self.idf_cache:
            df = self.inverted_index.get(term, {'doc_freq': 0})['doc_freq']
            self.idf_cache[term] = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
        return self.idf_cache[term]

    def score(self, query_terms, doc_id):
        score = 0
        doc_length = self.doc_lengths[doc_id]
        for term in query_terms:
            tf = self.inverted_index.get(term, {'postings': {}})['postings'].get(doc_id, 0)
            idf = self.idf(term)
            score += idf * (tf * (self.k1 + 1)) / (
                        tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length))
        return score


def apply_bm25_to_query(query, inverted_index, doc_lengths, k=10):
    bm25 = BM25(inverted_index, doc_lengths)
    query_terms = [nltk.stem.porter.PorterStemmer().stem(term) for term in query.split()]
    scores = [(doc_id, bm25.score(query_terms, doc_id)) for doc_id in doc_lengths.keys()]
    ranked_docs = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
    return ranked_docs

