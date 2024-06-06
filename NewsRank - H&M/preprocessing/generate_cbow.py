import pandas as pd
from gensim.models import Word2Vec
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import logging
import nltk
import chardet

# Download necessary NLTK data
nltk.download('punkt')

# Enable logging for gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Initialize the Porter Stemmer
stemmer = PorterStemmer()

# Detect the encoding of the file
with open('corpus.txt', 'rb') as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']

# Read input from corpus.txt with the detected encoding
with open('corpus.txt', 'r', encoding=encoding) as file:
    lines = file.readlines()

# Preprocess text
def preprocess(text):
    tokens = word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

# Apply preprocessing to each line
processed_texts = [preprocess(line.strip()) for line in lines]

# Create CBOW model
cbow_model = Word2Vec(processed_texts, vector_size=300, window=5, min_count=1, sg=0, workers=4)

# Save the model
cbow_model.save("cbow_model.bin")

# If you want to access the vector for a specific word:
word_vector = cbow_model.wv['wizard']  # Replace 'wizard' with any word from your dataset
print(word_vector)

# For a summary of the model
print(cbow_model)
