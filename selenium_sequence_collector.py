from bs4 import BeautifulSoup
from selenium import webdriver
from docx import Document
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging


def iter_headings(paragraphs):
    for paragraph in paragraphs:
        if paragraph.style.name.startswith('Heading'):
            yield paragraph


def get_errors(document: Document):
    ids = []
    for heading in iter_headings(document.paragraphs):
        text = heading.text
        if text.startswith("Region ID"):
            ids.append(text.split(":")[-1].split("_")[0].strip())
        elif text.startswith("COMPARISON ERROR") or text.startswith("MISSING"):
            ids.append(text.split(":")[-1].strip())
    return ids


def extract_sequence_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    for span in soup.find_all('span'):
        if 'style' in span.attrs:
            styles = span['style'].split(';')
            for style in styles:
                prop, _, value = style.partition(':')
                if prop.strip() == 'color':
                    if value.strip() != 'rgba(0, 0, 0, 0)':
                        result.append(span.text)
    return "".join(result)


def get_sequences_from_errors(errors):
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 10)
    sequences = {}
    try:
        for error in errors:
            driver.get(f"https://repeatsdb.bio.unipd.it/structure/{error}")
            try:
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'root'))).get_attribute("innerHTML")
                sequences[error] = extract_sequence_from_html(element)
            except TimeoutException:
                logging.error(f"MISSING from repeatsdb region ID: {error}")
    except Exception as e:
        logging.error("EXCEPTION:" + str(e))
    driver.quit()
    for k, v in sequences.items():
        logging.info(f"Region ID: {k}\n{v}\n")


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s', filename="sequence.txt", filemode="w")
    doc = Document("classi_report.docx")
    get_sequences_from_errors(get_errors(doc))


if __name__ == "__main__":
    main()
