import os
import re
from bs4 import BeautifulSoup


INPUT_DIR = os.path.join( "data", "Laws")
OUTPUT_DIR = os.path.join( "dataCleaned", "Laws")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text(text):
    text = re.sub(r"\xa0", " ", text)
    text = re.sub(r"[\t\r ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\bARTICULO\n(\d+°?)", r"ARTICULO \1", text)
    return text.strip()


def strip_unwanted_elements(soup):
    # Remove non-content or boilerplate sections.
    for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
        tag.decompose()

    # Remove menus, sliders, TOC, and similar UI blocks.
    for tag in soup.find_all(["table", "div"], id=re.compile(r"toc|Resumen|NotasDestino", re.IGNORECASE)):
        tag.decompose()
    for tag in soup.find_all(["div"], class_=re.compile(r"slider|toc|resumenvigencias", re.IGNORECASE)):
        tag.decompose()

    # Remove elements that are hidden by inline styles.
    for tag in soup.find_all(style=True):
        style = tag.get("style", "").replace(" ", "").lower()
        if "display:none" in style or "visibility:hidden" in style:
            tag.decompose()

    # Remove UI toggles and boilerplate labels.
    for tag in soup.find_all(class_=re.compile(r"toctoggle|toc-link", re.IGNORECASE)):
        tag.decompose()

    # Remove paragraphs or spans that only announce auxiliary text blocks.
    for text_node in soup.find_all(string=re.compile(r"TEXTO\s+CORRESPONDIENTE\s+A", re.IGNORECASE)):
        parent = text_node.parent
        if parent:
            parent.decompose()

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".html"):
        continue

    file_path = os.path.join(INPUT_DIR, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Extract metadata before removing hidden spans
    metadata = {}
    for span in soup.find_all("span", attrs={"field": True}):
        field = span.get("field")
        if field:
            metadata[field] = clean_text(span.get_text(" ", strip=True))

    strip_unwanted_elements(soup)

    # Remove metadata spans from content extraction
    for span in soup.find_all("span", attrs={"field": True}):
        span.decompose()

    # Extract main text
    body_node = soup.body if soup.body else soup
    body = body_node.get_text(separator="\n")
    body = clean_text(body)

    # Build final structured text
    final_text = ""

    final_text += "TIPO: " + metadata.get("tipo", "") + "\n"
    final_text += "NUMERO: " + metadata.get("numero", "") + "\n"
    final_text += "ANIO: " + metadata.get("anio", "") + "\n"
    final_text += "ESTADO: " + metadata.get("estado_documento", "") + "\n"
    final_text += "ENTIDAD: " + metadata.get("entidad_emisora", "") + "\n"
    final_text += "\n"
    final_text += "CONTENIDO:\n\n"
    final_text += body

    # Save txt
    txt_filename = filename.replace(".html", ".txt")
    output_path = os.path.join(OUTPUT_DIR, txt_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"Processed {filename}")

print("All files converted to txt.")
