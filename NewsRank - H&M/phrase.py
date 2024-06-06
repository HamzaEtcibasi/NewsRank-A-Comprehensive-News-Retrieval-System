import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

# Remove the suffixes from an English word and obtain its stem
porter_stemmer = nltk.stem.PorterStemmer()


def tokenize(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation

    # Add space between digits and letters except for ordinal numbers
    text = re.sub(r'(?<!\d)(\d+)(?!st|nd|rd|th)(?!\d)', r'\1 ', text)

    tokens = [porter_stemmer.stem(token) for token in text.split() if token not in stop_words]

    return tokens


def phrase_query(inverted_index, query):
    query_terms = tokenize(query)
    doc_scores = {}

    # Initialize document scores
    for term in query_terms:
        if term in inverted_index:
            for doc_id, positions in inverted_index[term]['postings'].items():
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = 0

    # Check for consecutive matches
    for term in query_terms:
        if term in inverted_index:
            for doc_id, positions in inverted_index[term]['postings'].items():
                if all(doc_id in inverted_index[qt]['postings'] for qt in query_terms):
                    for pos in positions:
                        if all((pos + i) in inverted_index[query_terms[i]]['postings'][doc_id] for i in range(len(query_terms))):
                            doc_scores[doc_id] += 1

    # Filter out documents with zero score
    sorted_docs = [(doc_id, score) for doc_id, score in doc_scores.items() if score > 0]

    # Sort documents by score
    sorted_docs = sorted(sorted_docs, key=lambda x: x[1], reverse=True)

    return sorted_docs
