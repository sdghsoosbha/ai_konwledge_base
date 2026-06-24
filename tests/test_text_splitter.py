import pytest

from app.services.file_parser import ParsedPage
from app.services.text_splitter import split_pages


def test_split_pages_with_overlap():
    chunks = split_pages([ParsedPage(text="abcdef", page_number=1)], chunk_size=4, overlap=2)

    assert [chunk.content for chunk in chunks] == ["abcd", "cdef"]
    assert chunks[0].metadata["page"] == 1


def test_split_pages_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        split_pages([ParsedPage(text="abc")], chunk_size=4, overlap=4)

