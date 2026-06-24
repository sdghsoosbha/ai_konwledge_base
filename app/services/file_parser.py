from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


class UnsupportedFileTypeError(ValueError):
    pass


class DocumentParseError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedPage:
    text: str
    page_number: int | None = None


SUPPORTED_TYPES = {".txt": "txt", ".md": "md", ".pdf": "pdf"}


def get_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    file_type = SUPPORTED_TYPES.get(suffix)
    if file_type is None:
        raise UnsupportedFileTypeError("不支持文件类型,仅支持TXT,MD,PDF")
    return file_type


def parse_document(filename: str, content: bytes) -> list[ParsedPage]:
    file_type = get_file_type(filename)
    try:
        if file_type in {"txt", "md"}:
            text = _decode_text(content)
            pages = [ParsedPage(text=text, page_number=None)]
        else:
            pages = _parse_pdf(content)
    except DocumentParseError:
        raise
    except Exception as exc:
        raise DocumentParseError(f"Failed to parse {file_type.upper()} file") from exc

    if not any(page.text.strip() for page in pages):
        raise DocumentParseError("No extractable text found in document")
    return pages


def _decode_text(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DocumentParseError("Text file encoding is not supported")


def _parse_pdf(content: bytes) -> list[ParsedPage]:
    reader = PdfReader(BytesIO(content))
    pages: list[ParsedPage] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(ParsedPage(text=text, page_number=index))
    return pages

