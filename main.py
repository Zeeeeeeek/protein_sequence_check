import difflib
from io import StringIO

import pandas as pd
import requests
from Bio import SeqIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, black
from typing import List, Tuple

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

def compare2(a, b):
    # list of type: (color: char) if color is black, char is the same in both strings, else it's red
    res = []
    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == ' ':
            res.append(('BLACK', s[-1]))
        else:
            res.append(('RED', s[-1]))
    return res

def get_fasta(pdb_id):
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}"
    response = requests.get(url)
    return response.text


def is_chain(description, chain_id):
    chains = [char for char in list(description.split("|")[1].replace("Chains", "")) if char.isalpha()]
    return chain_id in chains


def get_chain_from_fasta(fasta_data, chain_id):
    fasta_io = StringIO(fasta_data)
    for record in SeqIO.parse(fasta_io, "fasta"):
        if is_chain(record.description, chain_id):
            return record.seq
    return None


def check_df(df_path):
    df = pd.read_csv(df_path, usecols=["pdb_id", "pdb_chain", "sequence"])
    for index, row in df.iterrows():
        fasta_data = get_fasta(row["pdb_id"])
        chain_data = get_chain_from_fasta(fasta_data, row["pdb_chain"])
        if chain_data is None:
            raise ValueError(f"Chain {row['pdb_chain']} not found in {row['pdb_id']}")
        if row["sequence"] not in chain_data:
            print(f"Sequence mismatch for {row['pdb_id']} chain {row['pdb_chain']}")
            print(compare(row["sequence"], chain_data))


def write_colored_text_to_pdf(text_list, filename, header):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(10, height - 20, header)
    x_position = 10

    for color, text in text_list:
        if color.upper() == 'RED':
            c.setFillColor(red)
        elif color.upper() == 'BLACK':
            c.setFillColor(black)
        text_width = c.stringWidth(text, "Helvetica", 12)
        c.drawString(x_position, height - 40, text)
        x_position += text_width

    c.save()

def write_report_to_pdf(filename, errors: List[Tuple[str, str]]):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    c.setFillColor(black)

    y_position = height - 40
    for i, (a, b) in enumerate(errors):
        # Se y_position è troppo piccola, crea una nuova pagina
        if y_position < 40:
            c.showPage()
            y_position = height - 40

        c.drawString(10, y_position, f"{a} => {b}")
        x_position = 10
        comparison = compare2(a, b)

        for color, text in comparison:
            if color.upper() == 'RED':
                c.setFillColor(red)
            elif color.upper() == 'BLACK':
                c.setFillColor(black)
            text_width = c.stringWidth(text, "Helvetica", 12)
            c.drawString(x_position, y_position - 20, text)
            x_position += text_width
        c.setFillColor(black)
        c.drawString(10, y_position, "")
        c.drawString(10, y_position - 20, "")

        # Aggiungi newline alla fine del ciclo for
        c.drawString(10, y_position - 40, "")
        c.drawString(10, y_position - 60, "")

        # Aggiorna y_position per il prossimo errore
        y_position -= 80

    c.save()




def main():
    #check_df("class2.csv")
    # fasta_data = get_fasta("1A0M")
    # chain_data = get_chain_from_fasta(fasta_data, "A")
    # print(chain_data)
    write_report_to_pdf("report.pdf", [
        ("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),("XXXXXXXXXXXX", "ATGG"),("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),("ATCG", "ATGG"),
        ("XXXXXXXXXXXX", "ATGG"),
    ])


if __name__ == "__main__":
    main()
