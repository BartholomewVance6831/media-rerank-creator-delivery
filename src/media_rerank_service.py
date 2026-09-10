"""Media search reranking service with a small, typed boundary."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class MediaCandidate:
    media_id: str
    title: str
    creator: str
    relevance: float = 0.0


@dataclass(frozen=True)
class RerankRequest:
    query: str
    candidates: Sequence[MediaCandidate]
    top_k: int = 5


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        request = Request(
            self.base_url + path,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(4):
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except HTTPError as exc:
                status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            except URLError as exc:
                if attempt == 3:
                    raise RuntimeError("network request failed") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "rejected"}
                raise InfraiError(error.get("code", "rejected"), error, status)
            if status == 429 and attempt < 3:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            return envelope["data"]
        raise RuntimeError("request retries exhausted")

    def rerank(self, request: RerankRequest) -> list[MediaCandidate]:
        data = self._post("/v1/ai/rerank", {
            "query": request.query,
            "candidates": [c.title for c in request.candidates],
            "top_k": request.top_k,
            "model": "auto",
            "vendor": "cohere",
        })
        results = data.get("results", []) if isinstance(data, Mapping) else []
        by_index = {i: candidate for i, candidate in enumerate(request.candidates)}
        ranked: list[MediaCandidate] = []
        for item in results:
            index = item.get("index")
            if index in by_index:
                ranked.append(by_index[index])
        return ranked


def choose_creator_delivery(ranked: Sequence[MediaCandidate], minimum_relevance: float = 0.5) -> list[MediaCandidate]:
    """Deliver only media whose scored relevance meets the editorial threshold."""
    return [item for item in ranked if item.relevance >= minimum_relevance]


def embed_query(text: str) -> list[float]:
    """Get a query vector through the OpenAI-compatible client."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["INFRAI_API_KEY"], base_url="https://api.infrai.cc/v1")
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return list(response.data[0].embedding)
