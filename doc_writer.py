import difflib
from typing import List, Tuple

from docx import Document
from docx.shared import RGBColor


RED = RGBColor(0xFF, 0x00, 0x00)
BLACK = RGBColor(0x00, 0x00, 0x00)


def compare2(a, b):
    # list of type: (color: char) if color is black, char is the same in both strings, else it's red
    res = []
    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == ' ':
            res.append(('BLACK', s[-1], i))
        else:
            res.append(('RED', s[-1], i))
    return res

def write_docx(path,  errors: List[Tuple[str, str]]):
    doc = Document()
    for a, b in errors:
        doc.add_paragraph(f"FASTA:\n{a}")
        doc.add_paragraph(f"Expected:\n{b}")
        comparison = compare2(a, b)
        paragraph = doc.add_paragraph()
        for color, c, _ in comparison:
            run = paragraph.add_run(c)
            if color.upper() == 'RED':
                run.font.color.rgb = RED
            elif color.upper() == 'BLACK':
                run.font.color.rgb = BLACK
        doc.add_paragraph()
    doc.save(path)


if __name__ == "__main__":
    write_docx("test.docx", [("a", "ab"), ("c", "dc")])
