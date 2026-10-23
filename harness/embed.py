"""Embedding back-ends. Record the exact model string in the pre-registration."""
from typing import Callable


def get_embedder(spec: str) -> Callable[[list[str]], list[list[float]]]:
    """spec examples: 'st:sentence-transformers/all-MiniLM-L6-v2',
    'openai:text-embedding-3-small', 'litellm:<any litellm embedding model>'."""
    kind, _, model = spec.partition(":")
    if kind == "st":
        import threading
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer(model)
        lock = threading.Lock()  # tau2 runs conversations in threads; concurrent encode() hangs or segfaults torch

        def embed(texts):
            with lock:
                return m.encode(texts, normalize_embeddings=True).tolist()
        return embed
    if kind == "litellm":
        import litellm
        def embed(texts):
            resp = litellm.embedding(model=model, input=texts)
            return [d["embedding"] for d in resp.data]
        return embed
    if kind == "openai":
        from openai import OpenAI
        client = OpenAI()
        def embed(texts):
            resp = client.embeddings.create(model=model, input=texts)
            return [d.embedding for d in resp.data]
        return embed
    raise ValueError(f"Unknown embedder spec: {spec}")
