import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

#NLP MODEL
model = SentenceTransformer("all-MiniLM-L6-v2")

def similarity_to_weight(sim):
    if sim < 0.1:
        return 0
    elif sim < 0.2:
        return 1
    elif sim < 0.3:
        return 2
    else:
        return 3

def performance_label(value):
    if value >= 2.5:
        return "Strongly Attained"
    elif value >= 2.0:
        return "Attained"
    elif value >= 1.5:
        return "Partially Attained"
    else:
        return "Not Attained"

#Main Logic
def compute_attainment(po_input_str, co_input_str, co_att_input_str):
    try:
        #Parse POs
        POs = {}
        for line in po_input_str.strip().split("\n"):
            if line:
                entries = line.split(',')
                for entry in entries:
                    entry = entry.strip()
                    if entry:
                        k, v = entry.split(":", 1)
                        POs[k.strip()] = v.strip()

        #Parse COs
        COs = {}
        for line in co_input_str.strip().split("\n"):
            if line:
                entries = line.split(',')
                for entry in entries:
                    entry = entry.strip()
                    if entry:
                        k, v = entry.split(":", 1)
                        COs[k.strip()] = v.strip()

        #Parse CO attainment
        CO_att = {}
        for line in co_att_input_str.strip().split("\n"):
            if line:
                entries = line.split(',')
                for entry in entries:
                    entry = entry.strip()
                    if entry:
                        k, v = entry.split("=")
                        CO_att[k.strip()] = float(v.strip())

        po_keys = list(POs.keys())
        co_keys = list(COs.keys())

        if not po_keys or not co_keys:
            raise ValueError("No Program Outcomes or Course Outcomes provided.")

        po_emb = model.encode(list(POs.values()))
        co_emb = model.encode(list(COs.values()))

        sim = cosine_similarity(co_emb, po_emb)
        df_sim = pd.DataFrame(sim, index=co_keys, columns=po_keys)

        df_weight = df_sim.map(similarity_to_weight)

        #PO attainment
        PO_att = {}
        for po in po_keys:
            num = sum(df_weight.loc[co, po] * CO_att.get(co, 0) for co in co_keys)
            den = sum(df_weight[po])
            PO_att[po] = round(num / den, 2) if den != 0 else 0

        output_str = "CO–PO SIMILARITY MATRIX (RAW)\n"
        output_str += str(df_sim) + "\n\n"

        output_str += "CO–PO WEIGHTAGE MATRIX (0–3)\n"
        output_str += str(df_weight) + "\n\n"

        output_str += "PO ATTAINMENT & PERFORMANCE\n"
        for po, val in PO_att.items():
            output_str += (
                f"{po} : {val} → {performance_label(val)}\n"
            )
        return output_str

    except Exception as e:
        return f"Error: {e}"

def get_multiline_input(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)
    return "\n".join(lines)


po_input = get_multiline_input("Enter Program Outcomes (POs) (e.g., PO1: text, or PO1: text, PO2: text, type END on a new line to finish):")
co_input = get_multiline_input("Enter Course Outcomes (COs) (e.g., CO1: text, or CO1: text, CO2: text, type END on a new line to finish):")
co_att_input = get_multiline_input("Enter CO Attainment (0–3) (e.g., CO1=2.6, or CO1=2.6, CO2=1.5, type END on a new line to finish):")

result = compute_attainment(po_input, co_input, co_att_input)
print(result)
