import csv
import chardet

input_file = 'wapo2.csv'  # Update this with your CSV file name
output_file = 'output_dataset.txt'

# Detect the encoding of the input file
with open(input_file, 'rb') as f:
    result = chardet.detect(f.read())

file_encoding = result['encoding']

# Open the input CSV file and the output text file
with open(input_file, 'r', encoding=file_encoding, errors='ignore') as csv_file, open(output_file, 'w',
                                                                                      encoding='utf-8') as txt_file:
    # Use csv.reader with a flexible delimiter to handle both commas and tabs
    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"', skipinitialspace=True)

    for row in csv_reader:
        # Join all elements of the row and then split by tab if necessary
        joined_row = ','.join(row).split('\t')

        #if len(joined_row) < 2:
        #    print(f"Skipping invalid row: {row}")
        #    continue  # Skip rows that don't have at least 2 columns

        doc_id = joined_row[0].strip()
        text = joined_row[1].strip()

        # Write the id and text in the required format
        txt_file.write(f"{doc_id} {text}\n")

print(f"Dataset transformed and saved to {output_file}")
