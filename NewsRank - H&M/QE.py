from nltk.corpus import wordnet

def expand_query(query):
    words = query.split()
    expanded_words = set(words)
    additional_words = set()

    for word in words:
        if len(additional_words) >= 3:
            break
        synsets = wordnet.synsets(word)
        for synset in synsets:
            for lemma in synset.lemmas():
                if lemma.name() not in expanded_words and lemma.name() not in additional_words:
                    additional_words.add(lemma.name())
                    if len(additional_words) >= 3:
                        break
            if len(additional_words) >= 3:
                break
            for hypernym in synset.hypernyms():
                for hypernym_lemma in hypernym.lemma_names():
                    if hypernym_lemma not in expanded_words and hypernym_lemma not in additional_words:
                        additional_words.add(hypernym_lemma)
                        if len(additional_words) >= 3:
                            break
                if len(additional_words) >= 3:
                    break
            if len(additional_words) >= 3:
                break
        if len(additional_words) >= 3:
            break

    expanded_words.update(additional_words)
    expanded_list = list(additional_words)

    return ' '.join(expanded_words), expanded_list