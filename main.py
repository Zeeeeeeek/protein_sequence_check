import difflib
import os
from io import StringIO

import pandas as pd
import requests
from Bio import SeqIO
from typing import List, Tuple
from doc_writer import write_docx
def compare(a, b):
    res = f"{a} => {b}\n"
    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            res += u'Delete "{}" from position {}\n'.format(s[-1], i)
        elif s[0] == '+':
            res += u'Add "{}" to position {}\n'.format(s[-1], i)
    return res+"\n"


def get_fasta(pdb_id):
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}"
    response = requests.get(url)
    fasta = response.text
    return StringIO(fasta)


def is_chain(description, chain_id):
    chains = [char for char in list(description.split("|")[1].replace("Chains", "")) if char.isalpha()]
    return chain_id in chains


def get_chain_from_fasta(fasta_io, chain_id):
    for record in SeqIO.parse(fasta_io, "fasta"):
        if is_chain(record.description, chain_id):
            return record.seq
    return None


def check_df(df_path):
    df = pd.read_csv(df_path, usecols=["pdb_id", "pdb_chain", "sequence", "region_id"])
    errors = []
    for index, row in df.iterrows():
        fasta_io = get_fasta(row["pdb_id"])
        chain_data = get_chain_from_fasta(fasta_io, row["pdb_chain"])
        if chain_data is None:
            raise ValueError(f"Chain {row['pdb_chain']} not found in {row['pdb_id']}")
        if row["sequence"] not in chain_data:
            errors.append((row['region_id'], (chain_data, row["sequence"])))
    name = df_path.split("/")[-1].replace(".csv", "")
    write_docx(name + "_report.docx", errors)


def main():
    if not os.path.exists("./fasta"):
        os.makedirs("./fasta")
    check_df("class2.csv")


if __name__ == "__main__":
    main()
