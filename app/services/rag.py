from app.schemas.chat import SourceChunk


def build_rag_prompt(question: str, sources: list[SourceChunk]) -> str:
    context_blocks = []
    for index, source in enumerate(sources, start=1):
        context_blocks.append(
            f"[{index}] Document: {source.document_name}\n"
            f"Similarity: {source.score}\n"
            f"Content:\n{source.content}"
        )
    context = "\n\n".join(context_blocks)
    return (
        "请根据下面的知识库片段回答用户问题。\n"
        "如果片段中没有答案，请明确说明知识库中没有足够信息，不要编造。\n\n"
        f"知识库片段:\n{context}\n\n"
        f"用户问题: {question}\n\n"
        "请给出简洁、准确的中文回答，并在必要时说明依据来自哪些片段编号。"
    )

