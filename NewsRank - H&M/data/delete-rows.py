import re

# Function to check if an ID contains uppercase letters
def contains_uppercase(id_str):
    return any(char.isupper() for char in id_str)

# Input and output file paths
input_file_path = 'trec_corpus.txt'
output_file_path = 'output.txt'

# Process the input file and write to the output file
with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
    for line in infile:
        # Split the line into ID and text
        parts = line.split(' ', 1)
        if len(parts) == 2:
            doc_id, text = parts
            # Write the line to the output file if the ID does not contain uppercase letters
            if not contains_uppercase(doc_id):
                outfile.write(line)

print("Processing completed. The output file is saved as 'output.txt'.")
