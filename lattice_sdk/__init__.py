"""Lattice SDK package."""

__version__ = "0.1.0"

import os
from dataclasses import dataclass
from time import time

import httpx

DEFAULT_BASE_URL = os.getenv("LATTICE_BASE_URL", "http://lattice.prismalabs.xyz")


@dataclass
class LatticeDB:
    api_key: str
    knowledge_base: str
    base_url: str
    embedding_model: str | None = None
    timeout: float = 30.0

    """
    A client for interacting with the Lattice API.

    Methods:
    - add: Add a document to the knowledge base.
    - progress: Check the progress of an asynchronous add job.
    - search: Search the knowledge base with a query.
    - list: List documents in the knowledge base.
    - clear: Clear all documents from the knowledge base.

    Embedding models:
    - ds1
    - prisma-embed"""

    def _request(self, method: str, path: str, **kwargs) -> dict:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        url = f"{self.base_url.rstrip('/')}{path}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, url, headers=headers, **kwargs)

        try:
            payload = response.json()
        except Exception:
            payload = {"error": response.text}

        if response.status_code >= 400:
            message = payload.get("error") if isinstance(payload, dict) else str(payload)
            raise RuntimeError(f"{response.status_code} {message}")

        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected API response format")
        return payload

    def add(
        self,
        text: str | None = None,
        *,
        source: str | None = None,
        chunker: str = "punct",
        max_chars: int | None = None,
        path: str | None = None,
        origin: str | None = None,
        async_mode: bool = True,
    ) -> str | dict:
        if text is None and source is None:
            raise ValueError("Either text or source must be provided")
        if text is not None and source is not None:
            raise ValueError("Provide text or source, not both")

        body: dict = {
            "knowledge_base": self.knowledge_base,
            "chunker": chunker,
            "async": async_mode,
        }

        if self.embedding_model:
            body["embedding_model"] = self.embedding_model
        if max_chars is not None:
            body["max_chars"] = max_chars
        if path is not None:
            body["path"] = path
        if origin is not None:
            body["origin"] = origin
        if text is not None:
            body["text"] = text
        if source is not None:
            body["source"] = source

        payload = self._request("POST", "/api/rag/add", json=body)
        if async_mode:
            job_id = payload.get("id") or payload.get("job_id")
            if not job_id:
                raise RuntimeError("Add job id missing from API response")
            return str(job_id)
        return payload

    def progress(self, job_id: str, *, details: bool = False) -> float | dict:
        payload = self._request("GET", f"/api/rag/progress/{job_id}")
        if details:
            return payload
        return float(payload.get("progress", 0.0))

    def search(self, query: str, *, strategy: str = "auto", k: int = 5) -> list[dict]:
        body = {
            "query": query,
            "k": k,
            "strategy": strategy,
            "knowledge_base": self.knowledge_base,
        }
        if self.embedding_model:
            body["embedding_model"] = self.embedding_model
        payload = self._request("POST", "/api/rag/search", json=body)
        return payload.get("results", [])

    def list(self, *, page: int = 1, per_page: int = 50) -> dict:
        params = {
            "page": page,
            "per_page": per_page,
            "knowledge_base": self.knowledge_base,
        }
        if self.embedding_model:
            params["embedding_model"] = self.embedding_model
        return self._request("GET", "/api/rag/list", params=params)

    def clear(self) -> dict:
        body = {"knowledge_base": self.knowledge_base}
        if self.embedding_model:
            body["embedding_model"] = self.embedding_model
        return self._request("POST", "/api/rag/remove", json=body)


class Lattice:
    @staticmethod
    def connect(
        *,
        api_key: str,
        knowledge_base: str = "default",
        base_url: str = DEFAULT_BASE_URL,
        embedding_model: str | None = None,
        timeout: float = 30.0,
    ) -> LatticeDB:
        return LatticeDB(
            api_key=api_key,
            knowledge_base=knowledge_base,
            base_url=base_url,
            embedding_model=embedding_model,
            timeout=timeout,
        )
