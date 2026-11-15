import csv
import io
from typing import List, Dict, Any

from pypdf import PdfReader


def parse_pdf(filepath: str) -> List[Dict[str, Any]]:
    """
    Extract text from each page of a PDF using pypdf.
    Returns a list of {page_num, text} dicts.
    Why pypdf: pure-Python, no native dependencies, straightforward for text extraction.
    Limitation: does not handle image-only (scanned) PDFs — text will be empty in those.
    """
    reader = PdfReader(filepath)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"page_num": i + 1, "text": text.strip()})
    return pages


def parse_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Read a CSV file and return each row as a dict.
    Returns a list of {row_index, row_dict} where row_dict maps column headers to values.
    Why treat CSV separately: tabular data has a different structure to prose —
    chunking it row-by-row preserves the meaning of each data record.
    """
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows.append({"row_index": i, "row_dict": dict(row)})
    return rows


def parse_text(filepath: str) -> List[Dict[str, Any]]:
    """Read a plain text file and return it as a single page."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    return [{"page_num": 1, "text": content.strip()}]
