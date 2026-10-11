from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DOCUMENTS_DIR
from common import ingest_pdf


def main():
    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {DOCUMENTS_DIR}")
        print("Put one or more PDFs into data/documents/ and run again.")
        return

    for pdf_path in pdf_files:
        try:
            count = ingest_pdf(pdf_path)
            print(f"\nSUCCESS: {pdf_path.name} -> {count} chunks indexed.")
        except Exception as exc:
            print(f"\nFAILED: {pdf_path.name} -> {exc}")


if __name__ == "__main__":
    main()
