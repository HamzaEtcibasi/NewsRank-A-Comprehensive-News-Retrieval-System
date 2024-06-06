import os
import sys
import re
import chardet
from nltk.stem import PorterStemmer

# Ensure correct usage
if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print('Needs 1 argument - the input file path!')
    exit(0)

# Detect the file encoding
with open(sys.argv[1], 'rb') as f:
    rawdata = f.read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']

# Regular expression to clean the text
cleanTextRegex = re.compile('[^a-zA-Z]')
stemmer = PorterStemmer()
doStem = len(sys.argv) == 3 and sys.argv[2] == 'doStem'

# Output file path
outFilepath = '../data/' + os.path.basename(sys.argv[1])
if doStem:
    outFilepath = '../data/' + os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".stemmed" + \
                  os.path.splitext(os.path.basename(sys.argv[1]))[1]

count = 0

# Process the input file and generate the output file
with open(outFilepath, 'w', encoding='utf-8') as outputFile:
    with open(sys.argv[1], 'r', encoding=encoding) as inputFile:
        for inLine in inputFile.readlines():
            if ',' in inLine:
                # Extract the id and the title
                parts = inLine.strip().split(',', 1)
                if len(parts) == 2:
                    currentId, text = parts
                    # Clean text
                    text = cleanTextRegex.sub(' ', text).lower()
                    # Remove multiple whitespaces
                    text = re.sub(r'\s+', ' ', text).strip()

                    wordList = []
                    for w in text.split(' '):
                        if w:
                            cleaned = stemmer.stem(w.strip()) if doStem else w.strip()
                            wordList.append(cleaned)
                    outputText = ' '.join(wordList)

                    # Write single line output
                    outputFile.write(currentId)
                    outputFile.write(' ')
                    outputFile.write(outputText.strip())
                    outputFile.write('\n')
                    count += 1

print('Completed all', count, 'titles')
print('Saved in:', outFilepath)
