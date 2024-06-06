import json
import tkinter as tk
from tkinter import ttk
from BM25 import apply_bm25_to_query
from QE import expand_query
from boolean import process_boolean_query
from phrase import phrase_query
from QL import apply_ql_to_query

from spellchecker import SpellChecker
import nltk

# Download WordNet if not already downloaded
nltk.download('wordnet')
nltk.download('omw-1.4')  # Also download Open Multilingual Wordnet for broader synonym sets

# Load inverted index and document titles from files
with open('save/inverted_index.json', 'r') as f:
    inverted_index = json.load(f)

with open('save/doc_titles.json', 'r') as f:
    doc_titles = json.load(f)

with open('save/doc_lengths.json', 'r') as f:
    doc_lengths = json.load(f)

# Load inverted index and document titles from files
with open('save/inverted_index_pq.json', 'r') as f:
    inverted_index_pq = json.load(f)


# Initialize the spell checker
spell = SpellChecker()
def correct_spelling(query):
    words = query.split()
    misspelled = spell.unknown(words)
    corrected_words = [spell.correction(word) if word in misspelled else word for word in words]
    return ' '.join(corrected_words), misspelled


def search_query(event=None):
    query = query_entry.get()
    selected_algorithm = algorithm.get()

    if spellcheck_var.get():
        corrected_query, misspelled = correct_spelling(query)
        query_entry.delete(0, tk.END)
        query_entry.insert(0, corrected_query)
        corrections_label.config(text="")
    else:
        corrected_query = query
        misspelled = []

    if misspelled:
        corrections = [f"{word} -> {spell.correction(word)}" for word in misspelled]
        corrections_label.config(text="Did you mean? " + ", ".join(corrections))
    else:
        corrections_label.config(text="")

    if selected_algorithm == "Boolean":
        results = process_boolean_query(corrected_query, inverted_index, doc_titles)
        expanded_words_label.config(text="")
    elif selected_algorithm == "BM25":
        results = apply_bm25_to_query(corrected_query, inverted_index, doc_lengths)
        results = [doc_id for doc_id, _ in results]
        expanded_words_label.config(text="")
    elif selected_algorithm == "Phrase":
        results = phrase_query(inverted_index_pq, corrected_query)
        results = [doc_id for doc_id, _ in results]
        expanded_words_label.config(text="")
    elif selected_algorithm == "QueryLikelihood":  # Handle QL option
        results = apply_ql_to_query(corrected_query, inverted_index, doc_lengths)
        results = [doc_id for doc_id, _ in results]
        expanded_words_label.config(text="")
    elif selected_algorithm == "QE":
        expanded_query, expanded_list = expand_query(corrected_query)
        expanded_words_label.config(text=f"The expanded query includes: {', '.join(expanded_list)}")
        results = apply_bm25_to_query(expanded_query, inverted_index, doc_lengths)
        results = [doc_id for doc_id, _ in results]
    else:
        expanded_words_label.config(text="")

    results_list.delete(*results_list.get_children())
    counter = 0
    for doc_id in results:
        if counter >= 10:
            break
        title = doc_titles.get(doc_id, "Title not available")
        results_list.insert("", "end", values=(doc_id, title))
        counter += 1


# Create the main window
root = tk.Tk()
root.title("NewsRank")
root.geometry("900x600")

# Style configuration
style = ttk.Style()
style.theme_use("clam")

style.configure("TLabel", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
style.configure("Treeview", font=("Helvetica", 10))

style.map("TButton", foreground=[("pressed", "red"), ("active", "blue")],
          background=[("pressed", "!disabled", "black"), ("active", "white")])

# Create and place the query input field
query_frame = ttk.Frame(root)
query_frame.pack(side=tk.TOP, pady=10)  # Placing the query frame at the top

query_label = ttk.Label(query_frame, text="Enter Query:")
query_label.pack(side=tk.LEFT, padx=5)

query_entry = ttk.Entry(query_frame, width=80)
query_entry.pack(side=tk.LEFT, padx=5)

# Create and place the spellcheck checkbox
spellcheck_var = tk.BooleanVar(value=True)
spellcheck_checkbox = ttk.Checkbutton(query_frame, text="Enable Spellcheck", variable=spellcheck_var)
spellcheck_checkbox.pack(side=tk.LEFT, padx=5)

# Bind the Enter key to the search_query function
query_entry.bind("<Return>", search_query)

# Create and place the search button
search_button = ttk.Button(root, text="Search", command=search_query)
search_button.pack(pady=5)

# Create a frame to hold the radio buttons and place them horizontally
radio_frame = ttk.Frame(root)
radio_frame.pack(pady=5)

algorithm = tk.StringVar(value="Boolean")
style.configure("TRadiobutton", font=("Helvetica", 14))  # Increase font size

boolean_radio = ttk.Radiobutton(radio_frame, text="Boolean", variable=algorithm, value="Boolean", command=lambda: expanded_words_label.config(text=""))
boolean_radio.pack(side=tk.LEFT, padx=10)
bm25_radio = ttk.Radiobutton(radio_frame, text="BM25", variable=algorithm, value="BM25", command=lambda: expanded_words_label.config(text=""))
bm25_radio.pack(side=tk.LEFT, padx=10)
phrase_radio = ttk.Radiobutton(radio_frame, text="Phrase", variable=algorithm, value="Phrase", command=lambda: expanded_words_label.config(text=""))
phrase_radio.pack(side=tk.LEFT, padx=10)
ql_radio = ttk.Radiobutton(radio_frame, text="QueryLikelihood", variable=algorithm, value="QueryLikelihood", command=lambda: expanded_words_label.config(text=""))
ql_radio.pack(side=tk.LEFT, padx=10)
qe_radio = ttk.Radiobutton(radio_frame, text="QE", variable=algorithm, value="QE")
qe_radio.pack(side=tk.LEFT, padx=10)

# Create and place the spellcheck corrections label
corrections_label = ttk.Label(root, text="", font=("Helvetica", 12), foreground="red")
corrections_label.pack(pady=10)

# Create and place the results treeview
columns = ("Document ID", "Document Title")
results_list = ttk.Treeview(root, columns=columns, show="headings")
results_list.heading("Document ID", text="Document ID")
results_list.heading("Document Title", text="Document Title")

# Adjust column widths and centers heading text
results_list.column("Document ID", width=280, stretch=tk.NO)
results_list.column("Document Title", width=620, anchor=tk.W, stretch=tk.YES)

# Create a style for centered headings
centered_heading_style = ttk.Style()
centered_heading_style.configure("Centered.Treeview.Heading", anchor="center")

# Apply the style to the heading
results_list.heading("Document Title", text="Document Title",
                     command=lambda: results_list.heading("Document Title", style="Centered.Treeview.Heading"))

results_list.pack(pady=20, fill=tk.BOTH, expand=True)

# Create and place the label to display expanded words
expanded_words_label = ttk.Label(root, text="", font=("Helvetica", 12))
expanded_words_label.pack(pady=10)

# Run the application
root.mainloop()
