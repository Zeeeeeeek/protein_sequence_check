import difflib
from typing import List, Tuple

import docx
from docx import Document
from docx.shared import RGBColor


RED = RGBColor(0xFF, 0x00, 0x00)
BLACK = RGBColor(0x00, 0x00, 0x00)

def get_or_create_hyperlink_style(d):
    if "Hyperlink" not in d.styles:
        if "Default Character Font" not in d.styles:
            ds = d.styles.add_style("Default Character Font",
                                    docx.enum.style.WD_STYLE_TYPE.CHARACTER,
                                    True)
            ds.element.set(docx.oxml.shared.qn('w:default'), "1")
            ds.priority = 1
            ds.hidden = True
            ds.unhide_when_used = True
            del ds
        hs = d.styles.add_style("Hyperlink",
                                docx.enum.style.WD_STYLE_TYPE.CHARACTER,
                                True)
        hs.base_style = d.styles["Default Character Font"]
        hs.unhide_when_used = True
        hs.font.color.rgb = docx.shared.RGBColor(0x05, 0x63, 0xC1)
        hs.font.underline = True
        del hs
    return "Hyperlink"


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )
    new_run = docx.text.run.Run(
        docx.oxml.shared.OxmlElement('w:r'), paragraph)
    new_run.text = text
    new_run.style = get_or_create_hyperlink_style(part.document)
    hyperlink.append(new_run._element)
    paragraph._p.append(hyperlink)
    return hyperlink

def compare2(a, b):
    # list of type: (color: char) if color is black, char is the same in both strings, else it's red
    res = []
    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == ' ':
            res.append(('BLACK', s[-1]))
        else:
            res.append(('RED', s[-1]))
    return res

def write_docx(path, errors: List[Tuple[str, Tuple[str, str]]], missing):
    doc = Document()
    doc.add_heading('RepeatsDB Structure Checker', level=1)
    for region_id, (a, b) in errors:
        h = doc.add_heading(level=3)
        add_hyperlink(h,
                      f"Region ID: {region_id}", f"https://repeatsdb.bio.unipd.it/structure/{region_id.split('_')[0]}"
                      )
        doc.add_paragraph(f"FASTA:\n{a}")
        doc.add_paragraph(f"From query:\n{b}")
        comparison = compare2(a, b)
        paragraph = doc.add_paragraph('\nComparison:\n')
        for color, c in comparison:
            run = paragraph.add_run(c)
            if color.upper() == 'RED':
                run.font.color.rgb = RED
            elif color.upper() == 'BLACK':
                run.font.color.rgb = BLACK
        doc.add_paragraph()
    if missing:
        doc.add_heading('Missing chains', level=2)
        for m in missing:
            p = doc.add_paragraph(m)
            add_hyperlink(p, "Check PDB", f"https://repeatsdb.bio.unipd.it/structure/{m}")
    if errors or missing:
        doc.add_heading('Summary', level=2)
        if errors:
            doc.add_paragraph(f"Errors found: {len(errors)}")
        if missing:
            doc.add_paragraph(f"Missing chains: {len(missing)}")
    doc.save(path)
