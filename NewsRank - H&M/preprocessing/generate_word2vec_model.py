import gensim
from gensim.models import Word2Vec
import os

# Function to read input file and tokenize it into sentences and words
def read_corpus(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Tokenize each line into words
            yield gensim.utils.simple_preprocess(line)

# Path to your text data file
corpus_file = 'corpus.txt'  # Replace with your file path

# Read the corpus
sentences = list(read_corpus(corpus_file))

# Train the Word2Vec model
model = Word2Vec(sentences, vector_size=100, window=5, min_count=2, workers=4)

# Save the model
model.save("word2vec_model.bin")
print("Model saved successfully.")
