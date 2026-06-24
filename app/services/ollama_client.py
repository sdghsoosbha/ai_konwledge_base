import httpx

from app.core.config import settings


class OllamaUnavailableError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.chat_model = settings.ollama_chat_model
        self.embed_model = settings.ollama_embed_model

    def embed(self, text: str) -> list[float]:
        payload = {"model": self.embed_model, "input": text}
        data = self._post("/api/embed", payload, timeout=60.0)
        embedding = _extract_embedding(data)
        if len(embedding) != settings.embedding_dimensions:
            raise OllamaUnavailableError(
                f"Embedding dimension mismatch: expected {settings.embedding_dimensions}, got {len(embedding)}"
            )
        return [float(value) for value in embedding]

    def chat(self, prompt: str) -> str:
        payload = {
            "model": self.chat_model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": "You answer questions using only the provided knowledge base context.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        data = self._post("/api/chat", payload, timeout=120.0)
        message = data.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"].strip()
        raise OllamaUnavailableError("Ollama chat response is invalid")

    def _post(self, path: str, payload: dict, timeout: float) -> dict:
        try:
            response = httpx.post(f"{self.base_url}{path}", json=payload, timeout=timeout)
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError("Ollama service unavailable") from exc

        if response.status_code >= 400:
            raise OllamaUnavailableError(
                "Ollama request failed. Make sure the required model has been pulled"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise OllamaUnavailableError("Ollama returned non-JSON response") from exc


def _extract_embedding(data: dict) -> list:
    embedding = data.get("embedding")
    if isinstance(embedding, list):
        return embedding

    embeddings = data.get("embeddings")
    if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
        return embeddings[0]

    raise OllamaUnavailableError("Ollama embedding response is invalid")
