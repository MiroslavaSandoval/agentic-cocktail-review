from pathlib import Path

from pypdf import PdfReader


class DocumentLoadError(Exception):
    """Raised when a document cannot be loaded."""


def load_document(file_path: str) -> dict:
    """
    Load a text-based PDF recipe.

    Returns the filename, path, page count and extracted text.
    """
    path = Path(file_path).resolve()

    if not path.exists():
        raise DocumentLoadError(f"File does not exist: {path}")

    if path.suffix.lower() != ".pdf":
        raise DocumentLoadError("Only PDF files are currently supported.")

    try:
        reader = PdfReader(path)
        pages: list[str] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"\n--- PAGE {page_number} ---\n{text.strip()}")

        full_text = "\n".join(pages).strip()

    except Exception as exc:
        raise DocumentLoadError(
            f"Could not read PDF '{path.name}': {exc}"
        ) from exc

    if not full_text:
        raise DocumentLoadError(
            "No text was extracted. The PDF may be scanned or image-only."
        )

    return {
        "file_name": path.name,
        "file_path": str(path),
        "page_count": len(reader.pages),
        "text": full_text,
    }