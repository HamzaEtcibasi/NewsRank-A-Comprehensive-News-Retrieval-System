import os
import sys

def load_corpus_ids(corpus_file):
    corpus_ids = set()
    with open(corpus_file, 'r', encoding='utf-8') as file:
        for line in file:
            doc_id = line.split(' ', 1)[0]
            corpus_ids.add(doc_id.strip())
    return corpus_ids

def filter_qrels(qrel_file, corpus_ids, output_file):
    with open(qrel_file, 'r', encoding='utf-8') as file, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in file:
            parts = line.split()
            if len(parts) >= 3:
                doc_id = parts[2].strip()
                if doc_id in corpus_ids:
                    outfile.write(line)
                else:
                    print(f'Skipping qrel (doc not in corpus): {doc_id}')

if __name__ == "__main__":

    corpus_file = "trec_corpus.txt"
    qrel_file = "qrels.txt"
    output_file = "qrel_filtered.txt"

    corpus_ids = load_corpus_ids(corpus_file)
    filter_qrels(qrel_file, corpus_ids, output_file)

    print("Filtered qrel file written to:", output_file)
