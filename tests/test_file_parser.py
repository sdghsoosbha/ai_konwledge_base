import pytest

from app.services.file_parser import UnsupportedFileTypeError, get_file_type, parse_document


def test_parse_markdown_document():
    pages = parse_document("demo.md", "# Title\n\nKnowledge base text.".encode("utf-8"))

    assert len(pages) == 1
    assert "Knowledge base text" in pages[0].text


def test_reject_unsupported_file_type():
    with pytest.raises(UnsupportedFileTypeError):
        get_file_type("demo.docx")

