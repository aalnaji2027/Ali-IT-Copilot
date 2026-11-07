from pathlib import Path

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}
DEFAULT_PREVIEW_LENGTH = 5000


def read_text_file(file_path):
    """Extract text from a plain-text document."""
    path = Path(file_path)

    for encoding in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "The text-file encoding could not be detected."
    )


def read_pdf_file(file_path):
    """Extract text from a PDF document."""
    reader = PdfReader(str(file_path))

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as error:
            raise ValueError(
                "The PDF is password protected."
            ) from error

    extracted_pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""

        if page_text.strip():
            extracted_pages.append(
                f"--- Page {page_number} ---\n"
                f"{page_text.strip()}"
            )

    return "\n\n".join(extracted_pages)


def read_docx_file(file_path):
    """Extract paragraphs and tables from a DOCX document."""
    document = Document(str(file_path))
    extracted_content = []

    for paragraph in document.paragraphs:
        paragraph_text = paragraph.text.strip()

        if paragraph_text:
            extracted_content.append(paragraph_text)

    for table in document.tables:
        for row in table.rows:
            row_values = [
                cell.text.strip()
                for cell in row.cells
            ]

            if any(row_values):
                extracted_content.append(
                    " | ".join(row_values)
                )

    return "\n".join(extracted_content)


def extract_document_text(file_path):
    """Extract text and return a structured result."""
    path = Path(file_path)
    extension = path.suffix.lower()

    result = {
        "success": False,
        "text": "",
        "error": "",
        "extension": extension,
        "character_count": 0,
        "word_count": 0,
    }

    if not path.exists():
        result["error"] = (
            "The physical document could not be found."
        )
        return result

    if not path.is_file():
        result["error"] = (
            "The selected path is not a file."
        )
        return result

    if extension not in SUPPORTED_EXTENSIONS:
        result["error"] = (
            f"Unsupported file type: "
            f"{extension or 'unknown'}"
        )
        return result

    try:
        if extension == ".txt":
            extracted_text = read_text_file(path)
        elif extension == ".pdf":
            extracted_text = read_pdf_file(path)
        else:
            extracted_text = read_docx_file(path)

        extracted_text = extracted_text.strip()

        if not extracted_text:
            result["error"] = (
                "No readable text was found. The document "
                "may be empty, scanned, or image-based."
            )
            return result

        return {
            "success": True,
            "text": extracted_text,
            "error": "",
            "extension": extension,
            "character_count": len(extracted_text),
            "word_count": len(extracted_text.split()),
        }

    except Exception as error:
        result["error"] = str(error)
        return result


def create_document_preview(
    file_path,
    maximum_characters=DEFAULT_PREVIEW_LENGTH,
):
    """Extract text and create a shortened interface preview."""
    extraction_result = extract_document_text(file_path)

    if not extraction_result["success"]:
        extraction_result["preview"] = ""
        extraction_result["preview_shortened"] = False
        return extraction_result

    complete_text = extraction_result["text"]

    if len(complete_text) > maximum_characters:
        preview_text = (
            complete_text[:maximum_characters].rstrip()
            + "\n\n[Preview shortened]"
        )
        preview_shortened = True
    else:
        preview_text = complete_text
        preview_shortened = False

    extraction_result["preview"] = preview_text
    extraction_result["preview_shortened"] = (
        preview_shortened
    )

    return extraction_result