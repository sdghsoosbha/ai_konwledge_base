from dataclasses import dataclass

from app.services.file_parser import ParsedPage


@dataclass(frozen=True)
class TextChunk:
    content: str
    metadata: dict


def split_pages(pages: list[ParsedPage], chunk_size: int = 800, overlap: int = 120) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be greater than or equal to 0 and smaller than chunk_size")

    chunks: list[TextChunk] = []
    for page in pages:
        text = _normalize_text(page.text)
        if not text:
            continue

        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            content = text[start:end].strip()
            if content:
                chunks.append(
                    TextChunk(
                        content=content,
                        metadata={
                            "page": page.page_number,
                            "start": start,
                            "end": end,
                        },
                    )
                )
            if end == len(text):
                break
            next_start = end - overlap
            start = next_start if next_start > start else end
    return chunks


def _normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line)

