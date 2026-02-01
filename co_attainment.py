import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")

file_path = ""
dfs = {}

def process_sheet(df, sheet_index):

    q_numbers = df.iloc[0].fillna("").astype(str).tolist()
    max_marks = pd.to_numeric(df.iloc[1], errors='coerce').fillna(0).tolist()
    raw_co = df.iloc[2].tolist()

    co_map = []
    for v in raw_co:
        try:
            num = int(float(v))
            co_map.append(f"CO{num}")
        except:
            co_map.append(None)

    num_cols = min(len(q_numbers), len(max_marks), len(co_map))
    q_numbers = q_numbers[:num_cols]
    max_marks = max_marks[:num_cols]
    co_map = co_map[:num_cols]

    marks = df.iloc[3:, :num_cols].replace(
        ["-"," ",None,np.nan], np.nan
    )
    marks = marks.apply(pd.to_numeric, errors='coerce').fillna(0)

    n_students = marks.shape[0]

    cos = sorted(set(c for c in co_map if c is not None))
    sheet_co_list = []

    for co in cos:
        co_scored = 0.0
        co_max = 0.0

        for col_idx, mapped_co in enumerate(co_map):
            if mapped_co != co:
                continue
            qname = str(q_numbers[col_idx]).strip()
            qmax = float(max_marks[col_idx])
            col_vals = marks.iloc[:, col_idx].astype(float)
            co_scored += col_vals.sum()

            if re.match(r"1[a-zA-Z]", qname):
                co_max += qmax * n_students
            elif re.match(r"[2-9][a-zA-Z]", qname):
                attempts = (col_vals > 0).sum()
                co_max += qmax * attempts
            else:
                co_max += qmax * n_students

        sheet_co_list.append({
            "co": co,
            "scored": float(co_scored),
            "max": float(co_max)
        })

    return sheet_co_list

def merge_co_lists(*sheets):
    co_totals = {}
    for sheet in sheets:
        for entry in sheet:
            co = entry["co"]
            if co not in co_totals:
                co_totals[co] = {
                    "co": co,
                    "scored": float(entry["scored"]),
                    "max": float(entry["max"])
                }
            else:
                co_totals[co]["scored"] += float(entry["scored"])
                co_totals[co]["max"] += float(entry["max"])

    return sorted(co_totals.values(), key=lambda x: int(x["co"][2:]))

def attain_internal(internal):
    internal_attain = []
    for i in internal:
        if i["max"] == 0:
            att = 0.0
        else:
            att = ((i["scored"] / i["max"]) * 100) * 0.75 + 22.5
        internal_attain.append({"co": i["co"], "attain": round(att, 2)})
    return internal_attain

def attain_external(sheet4):
    external_attain = []
    for i in sheet4:
        if i["max"] == 0:
            att = 0.0
        else:
            att = (i["scored"] / i["max"]) * 100
        external_attain.append({"co": i["co"], "attain": round(att, 2)})
    return external_attain

def total_attainment(internal_attain, external_attain):
    final = {}
    for i in internal_attain:
        final[i["co"]] = 0.4 * i["attain"]
    for i in external_attain:
        final[i["co"]] = final.get(i["co"], 0) + 0.6 * i["attain"]
    return [{"co": k, "attain": round(v, 2)}
            for k, v in sorted(final.items(), key=lambda x: int(x[0][2:]))]

def normalize_co(final_attain):
    normal = []
    for i in final_attain:
        n = min((i["attain"] / 75) * 3, 3)
        normal.append({"co": i["co"], "normalized": round(n, 2)})
    return normal

#GUI Functions

def select_file():
    global file_path, dfs
    file_path = filedialog.askopenfilename(
        title="Select an Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not file_path:
        label.config(text="No file selected")
        return
    dfs = pd.read_excel(file_path, sheet_name=None, header=None)
    for i, (name, sheet) in enumerate(dfs.items(), start=1):
        globals()[f"df{i}"] = sheet

    label.config(text=f"Loaded {len(dfs)} sheets")
    print(f"\nLoaded {len(dfs)} sheets\n")

def attain_co():
    if not dfs:
        label.config(text="Select file first!")
        return
    calculate_all()
    attain_all()

def calculate_all():
    sheets = list(dfs.values())

    sheet1 = process_sheet(sheets[0], 1)
    sheet2 = process_sheet(sheets[1], 2)
    sheet4 = process_sheet(sheets[3], 4)

    globals()["internal"] = merge_co_lists(sheet1, sheet2)
    globals()["sheet4"] = sheet4

    label.config(text="CO Calculated")

def attain_all():
    internal_attain = attain_internal(internal)
    external_attain = attain_external(sheet4)
    final_attain = total_attainment(internal_attain, external_attain)
    normal_attain = normalize_co(final_attain)


    output.delete("1.0", tk.END)

    for entry in normal_attain:
        line = f"{entry['co']} : {entry['normalized']}\n"
        output.insert(tk.END, line)
    label.config(text="CO Attainment calculated ✔")

#GUI
root = tk.Tk()
root.title("Excel CO Calculator")
root.geometry("500x260")

tk.Button(root, text="Select File", command=select_file).pack(pady=10)
tk.Button(root, text="Attain CO", command=attain_co).pack(pady=10)

label = tk.Label(root, text="No file selected yet")
label.pack(pady=20)

output = tk.Text(root, width=30, height=8)
output.pack(pady=10)

root.mainloop()
