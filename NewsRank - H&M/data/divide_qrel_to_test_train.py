def split_data(input_file, train_file, test_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    train_lines = []
    test_lines = []

    for index, line in enumerate(lines):
        if (index + 1) % 5 == 0:
            test_lines.append(line)
        else:
            train_lines.append(line)

    with open(train_file, 'w') as file:
        file.writelines(train_lines)

    with open(test_file, 'w') as file:
        file.writelines(test_lines)

# Specify the file names
input_file = 'qrel_histogram_30.txt'   # Replace with your input file name
train_file = 'qrels_histogram_30_train.txt'
test_file = 'qrels_histogram_30_test.txt'

# Call the function to split the data
split_data(input_file, train_file, test_file)
