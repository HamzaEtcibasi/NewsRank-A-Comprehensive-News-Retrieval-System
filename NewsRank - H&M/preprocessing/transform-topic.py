import re

input_file_path = 'topics2018.txt'  # Update with the actual path to your topics file
output_file_path = 'topics.txt'  # Update with the desired output path

with open(input_file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', encoding='utf-8') as outfile:
    topic_id = None
    topic_title = None
    for line in infile:
        num_match = re.search(r'<num> Number: (\d+) </num>', line)
        title_match = re.search(r'<title>(.*?)</title>', line)

        if num_match:
            topic_id = num_match.group(1).strip()
        if title_match:
            topic_title = title_match.group(1).strip()

        if topic_id and topic_title:
            outfile.write(f'{topic_id} {topic_title}\n')
            topic_id = None
            topic_title = None

print(f'Transformed topics written to {output_file_path}')
