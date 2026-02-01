import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def get_multiline_input(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)
    return "\n".join(lines)

#NLP model
model = SentenceTransformer("all-MiniLM-L6-v2")

co_input_raw = get_multiline_input("Enter Course Outcomes (e.g., CO1: text, or CO1: text, CO2: text, type END on a new line to finish):")

#Parsing COs
COs = {}
for line in co_input_raw.strip().split("\n"):
    if line:
        entries = line.split(',')
        for entry in entries:
            entry = entry.strip()
            if entry:
                k, v = entry.split(":", 1)
                COs[k.strip()] = v.strip()

co_keys = list(COs.keys())
co_descriptions = list(COs.values())

#encoding COs
co_embeddings = model.encode(co_descriptions)

print(f"Parsed {len(COs)} Course Outcomes and generated embeddings.")
print("Starting interactive question matching...")

#loop for evaluating entier question paper
while True:
    question = input("\nEnter a question (or type 'STOP' to end):")
    if question.strip().upper() == 'STOP':
        print("Exiting interactive session.")
        break

    #question encoding
    question_embedding = model.encode([question])

    #cosine similarity between the question and CO embeddings
    similarities = cosine_similarity(question_embedding, co_embeddings)[0]

    most_relevant_co_index = np.argmax(similarities)
    
    #most relevant CO key, description, and similarity score
    most_relevant_co_key = co_keys[most_relevant_co_index]
    most_relevant_co_description = COs[most_relevant_co_key]
    highest_similarity_score = similarities[most_relevant_co_index]

    print(f"Most relevant CO: {most_relevant_co_key}")
    print(f"Description: {most_relevant_co_description}")
    print(f"Similarity Score: {highest_similarity_score:.4f}")
