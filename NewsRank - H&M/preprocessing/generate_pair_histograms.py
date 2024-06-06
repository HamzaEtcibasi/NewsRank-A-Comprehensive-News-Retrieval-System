import os
import sys
from gensim.models import KeyedVectors
import numpy as np
import timeit
from TextCollection import TextCollection

start_time = timeit.default_timer()

def cal_hist(t1_rep, t2_rep, qnum, hist_size):
    mhist = np.zeros((qnum, hist_size), dtype=np.float32)
    if t1_rep.size == 0 or t2_rep.size == 0:
        return mhist.flatten()
    mm = t1_rep.dot(np.transpose(t2_rep))

    for (i, j), v in np.ndenumerate(mm):
        if i >= qnum:
            break
        vid = int((v + 1.) / 2. * (hist_size - 1.))
        if vid < 0:
            vid = 0
        elif vid >= hist_size:
            vid = hist_size - 1
        mhist[i][vid] += 1.

    mhist += 1.
    mhist = np.log10(mhist)
    return mhist.flatten()

# Ensure correct number of arguments
if len(sys.argv) < 7:
    print('Needs 6 arguments - see comments for info ...')
    exit(0)

arg_corpus_file = sys.argv[1]
arg_topics_file = sys.argv[2]
arg_preranked_or_qrel_file = sys.argv[3]
arg_embedding_file = sys.argv[4]
arg_bin_size = int(sys.argv[5])
arg_qrel_or_preranked = sys.argv[6]  # 'qrel' or 'prerank'
print(arg_corpus_file)
print(arg_topics_file)
print(arg_preranked_or_qrel_file)
print(arg_embedding_file)
print(arg_bin_size)
print(arg_qrel_or_preranked)

# Load pre-ranked or qrels file
topic_doc_pairs = []  # (topic, doc id, score) score is 0,1 if qrel

if arg_qrel_or_preranked == 'prerank':
    with open(arg_preranked_or_qrel_file, 'r') as inputFile:
        for line in inputFile:
            parts = line.split()
            topic_doc_pairs.append((parts[0], parts[2].strip(), parts[4].strip()))

elif arg_qrel_or_preranked == 'qrel':
    with open(arg_preranked_or_qrel_file, 'r') as inputFile:
        for line in inputFile:
            parts = line.split()
            if len(parts) >= 4:  # Ensure there are enough parts
                topic_doc_pairs.append((parts[0], parts[2].strip(), parts[3].strip()))
            else:
                print("Skipping invalid line:", line)

print('All', len(topic_doc_pairs), 'topic_doc pairs loaded')

# Load word embedding
model = KeyedVectors.load_word2vec_format(arg_embedding_file, binary=True)
vectors = model
del model
vectors.fill_norms()  # Normalize the vectors

print('Embeddings loaded')
print('Loading docs ...')

# Load TREC corpus
trec_text_collection_data = []  # text 1 string per doc only, no id
trec_corpus = {}  # corpus id -> list of doc vector ids
count = 0
with open(arg_corpus_file, 'r', encoding='utf-8') as inputFile:
    for line in inputFile:
        count += 1
        if count % 10000 == 0:
            print('    ', count, 'docs loaded')
        parts = line.split(' ', 1)
        trec_corpus[parts[0]] = []

        trec_text_collection_data.append(parts[1])

        for w in parts[1].split(' '):
            ws = w.strip()
            if ws in vectors.key_to_index:
                trec_corpus[parts[0]].append(vectors.key_to_index[ws])

trec_text_collection = TextCollection(trec_text_collection_data)

print('All', count, 'docs loaded')

# Load topics file
trec_topics = {}  # topic -> list of query term vector ids
max_topic_word_count = 0
with open(arg_topics_file, 'r', encoding='utf-8') as inputFile:
    for line in inputFile:
        parts = line.split(' ', 1)

        if parts[0] not in trec_topics:
            trec_topics[parts[0]] = []

        for w in parts[1].split(' '):
            ws = w.strip()
            if ws in vectors.key_to_index:
                trec_topics[parts[0]].append(vectors.key_to_index[ws])

        if len(trec_topics[parts[0]]) > max_topic_word_count:
            max_topic_word_count = len(trec_topics[parts[0]])

print('All', len(trec_topics), 'topics loaded')
print('Max topic words:', max_topic_word_count)

print('Creating histograms')
count = 0
# Create histograms for every query term <-> doc term
# Based on pairs from pre-ranked file, using the similarities of the word embedding

# Histogram file format: topicId DocId prerankscore numberOfTopicWords(N) idf1 idf2 ... idfN <hist1> <hist2> ... <histN>
with open('../data/' + arg_qrel_or_preranked + '_histogram_' + str(arg_bin_size) + '.txt', 'w', encoding='utf-8') as outputFile:

    for topic, doc, score in topic_doc_pairs:
        count += 1
        if count % 10000 == 0:
            print('    ', count, 'ranked docs processed')

        if doc not in trec_corpus:
            print('Skipping doc (not in corpus): ' + doc)
            continue
        if topic not in trec_topics:
            print('Skipping topic (not in corpus): ' + topic)
            continue

        # Get the word embedding ids
        topic_word_ids = trec_topics[topic]
        doc_words_ids = trec_corpus[doc]

        if not topic_word_ids or not doc_words_ids:
            print(f'Skipping pair (empty vectors): {topic}, {doc}')
            continue

        topic_vectors = np.array([vectors[vectors.index_to_key[topic_word_ids[i]]] for i in range(0, len(topic_word_ids))], np.float32)
        doc_vectors = np.array([vectors[vectors.index_to_key[doc_words_ids[i]]] for i in range(0, len(doc_words_ids))], np.float32)

        if topic_vectors.size == 0 or doc_vectors.size == 0:
            print(f'Skipping pair (empty vectors after conversion): {topic}, {doc}')
            continue

        outputFile.write(topic + " " + doc + " " + str(score) + " " + str(len(topic_word_ids)) + " ")
        for w in topic_word_ids:
            outputFile.write(str(trec_text_collection.idf(vectors.index_to_key[w])) + " ")

        qnum = len(topic_word_ids)
        d1_embed = topic_vectors
        d2_embed = doc_vectors

        curr_hist = cal_hist(d1_embed, d2_embed, qnum, arg_bin_size)
        curr_hist = curr_hist.tolist()
        outputFile.write(' '.join(map(str, curr_hist)))

        outputFile.write('\n')
        outputFile.flush()

print('Completed after (seconds):', timeit.default_timer() - start_time)
