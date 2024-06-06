import math
import nltk

class QueryLikelihoodModel:
    def __init__(self, inverted_index, doc_lengths, smoothing_param=0.5):
        self.inverted_index = inverted_index
        self.doc_lengths = doc_lengths
        self.smoothing_param = smoothing_param
        self.total_terms = sum(doc_lengths.values())
        self.term_freq_cache = {}

    def term_freq(self, term, doc_id):
        if (term, doc_id) not in self.term_freq_cache:
            tf = self.inverted_index.get(term, {'postings': {}})['postings'].get(doc_id, 0)
            doc_length = self.doc_lengths[doc_id]
            self.term_freq_cache[(term, doc_id)] = (tf + self.smoothing_param) / (doc_length + self.smoothing_param * len(self.inverted_index))
        return self.term_freq_cache[(term, doc_id)]

    def coll_freq(self, term):
        return self.inverted_index.get(term, {'doc_freq': 0})['doc_freq']

    def score(self, query_terms, doc_id):
        score = 0
        for term in query_terms:
            term_freq = self.term_freq(term, doc_id)
            coll_freq = self.coll_freq(term) / self.total_terms

            # Add a small positive value (e.g., 1e-10) to prevent log(0)
            score += math.log(term_freq + 1e-10) - math.log(coll_freq + 1e-10)
        return score


def apply_ql_to_query(query, inverted_index, doc_lengths, k=10):
    ql = QueryLikelihoodModel(inverted_index, doc_lengths)
    query_terms = [nltk.stem.porter.PorterStemmer().stem(term) for term in query.split()]
    scores = [(doc_id, ql.score(query_terms, doc_id)) for doc_id in doc_lengths.keys()]
    ranked_docs = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
    return ranked_docs