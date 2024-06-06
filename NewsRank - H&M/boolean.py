import nltk
import collections

def process_boolean_query(query, inverted_index, doc_titles):
    stemmer = nltk.stem.porter.PorterStemmer()  # Use the PorterStemmer for consistency with your indexing
    indexed_docIDs = sorted(doc_titles.keys())  # All docIDs from your titles

    # Prepare query list
    query = query.replace('(', '( ')
    query = query.replace(')', ' )')
    query = query.split(' ')

    results_stack = []
    postfix_queue = collections.deque(shunting_yard(query))  # Convert infix to postfix

    while postfix_queue:
        token = postfix_queue.popleft()
        result = []

        if token not in ['AND', 'OR', 'NOT']:
            token = stemmer.stem(token)
            if token in inverted_index:
                result = list(inverted_index[token]['postings'].keys())
        elif token == 'AND':
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            result = boolean_AND(left_operand, right_operand, indexed_docIDs)
        elif token == 'OR':
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            result = boolean_OR(left_operand, right_operand, indexed_docIDs)
        elif token == 'NOT':
            right_operand = results_stack.pop()
            result = boolean_NOT(right_operand, indexed_docIDs)

        results_stack.append(result)

    return results_stack.pop()

def shunting_yard(infix_tokens):
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1, '(': 0, ')': 0}
    output = []
    operator_stack = []

    for token in infix_tokens:
        if token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()  # Pop '('
        elif token in precedence:
            while operator_stack and precedence[operator_stack[-1]] >= precedence[token]:
                output.append(operator_stack.pop())
            operator_stack.append(token)
        else:
            output.append(token)

    while operator_stack:
        output.append(operator_stack.pop())

    return output

def boolean_AND(left_operand, right_operand, indexed_docIDs):
    left_set = set(left_operand)
    right_set = set(right_operand)
    return list(left_set.intersection(right_set))


def boolean_OR(left_operand, right_operand, indexed_docIDs):
    left_set = set(left_operand)
    right_set = set(right_operand)
    return list(left_set.union(right_set))


def boolean_NOT(right_operand, indexed_docIDs):
    return list(set(indexed_docIDs) - set(right_operand))