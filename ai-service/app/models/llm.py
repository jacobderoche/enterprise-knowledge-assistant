"""Chat/LLM providers producing grounded, cited answers.

The offline provider is fully extractive: it composes an answer from the
retrieved context and never hallucinates, which makes it safe for demos and
deterministic for tests. Real providers (OpenAI / Anthropic) are used when
configured and receive a strict grounding system prompt.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..config import Settings, get_settings

SYSTEM_PROMPT = (
    "You are an enterprise knowledge assistant. Answer ONLY using the provided "
    "context passages. Every factual sentence must reference a passage using its "
    "bracketed citation marker like [1]. If the context does not contain the "
    "answer, say you do not have enough information. Be concise."
)


@dataclass
class ContextPassage:
    marker: int  # 1-based index shown to the model / user
    chunk_id: str
    document_id: str
    source: str
    text: str
    score: float


class ChatLLM(Protocol):
    name: str

    def generate(self, query: str, passages: list[ContextPassage]) -> str: ...


def _format_context(passages: list[ContextPassage]) -> str:
    return "\n\n".join(f"[{p.marker}] (source: {p.source})\n{p.text}" for p in passages)


class OfflineExtractiveLLM:
    """Deterministic extractive answerer used when no API key is configured."""

    name = "offline-extractive"

    def generate(self, query: str, passages: list[ContextPassage]) -> str:
        if not passages:
            return (
                "I don't have enough information in the knowledge base to answer "
                "that question."
            )
        lines = [
            "Based on the available documents:",
        ]
        for p in passages:
            snippet = " ".join(p.text.split())
            if len(snippet) > 320:
                snippet = snippet[:317] + "..."
            lines.append(f"- {snippet} [{p.marker}]")
        return "\n".join(lines)


class OpenAIChatLLM:
    name = "openai"

    def __init__(self, model: str, api_key: str) -> None:
        from openai import OpenAI  # type: ignore

        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.name = f"openai:{model}"

    def generate(self, query: str, passages: list[ContextPassage]) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{_format_context(passages)}\n\nQuestion: {query}",
                },
            ],
            temperature=0.1,
        )
        return resp.choices[0].message.content or ""


class AnthropicChatLLM:
    name = "anthropic"

    def __init__(self, model: str, api_key: str) -> None:
        import anthropic  # type: ignore

        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.name = f"anthropic:{model}"

    def generate(self, query: str, passages: list[ContextPassage]) -> str:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{_format_context(passages)}\n\nQuestion: {query}",
                }
            ],
        )
        return "".join(block.text for block in resp.content if block.type == "text")


def get_llm(settings: Settings | None = None) -> ChatLLM:
    settings = settings or get_settings()
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAIChatLLM(settings.openai_model, settings.openai_api_key)
    if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicChatLLM(settings.anthropic_model, settings.anthropic_api_key)
    return OfflineExtractiveLLM()
