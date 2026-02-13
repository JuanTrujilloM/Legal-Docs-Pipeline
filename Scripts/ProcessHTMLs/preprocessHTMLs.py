import argparse
import re
from pathlib import Path
from bs4 import BeautifulSoup

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
        if not hasattr(tag, "attrs") or tag.attrs is None:
            continue
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


def process_directory(input_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = list(input_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files.\n")

    for file_path in html_files:
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
        output_path = output_dir / file_path.with_suffix(".txt").name

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        print(f"Processed {file_path.name}")

    print("\nAll files converted to txt.")


def main():
    parser = argparse.ArgumentParser(
        description="Clean and convert HTML legal documents to structured TXT format"
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input directory containing HTML files",
    )

    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output directory for cleaned TXT files",
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists() or not input_dir.is_dir():
        print("Error: Input directory is not valid.")
        return 1

    process_directory(input_dir, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
