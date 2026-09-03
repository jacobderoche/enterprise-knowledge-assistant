"""Automated LLM/RAG evaluation.

Runs the RAG pipeline over a small labelled dataset and asserts quality gates:

* keyword recall  - the answer contains the expected facts
* groundedness    - every answer that makes a claim is backed by a citation
* citation@1      - the correct source document is the top citation

This is deliberately provider-agnostic: with the offline extractive LLM the
scores are deterministic, and the same harness works against OpenAI/Anthropic
by setting the provider env vars (useful in a nightly CI job or LangSmith run).
"""
from __future__ import annotations

import json
from pathlib import Path

from app.rag.graph import RagPipeline
from app.schemas import AccessContext

DATASET = Path(__file__).parent / "dataset.jsonl"
KEYWORD_RECALL_THRESHOLD = 0.99
CITATION_AT_1_THRESHOLD = 0.99


def _load_cases():
    with DATASET.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def test_rag_eval_quality_gates():
    cases = _load_cases()
    pipeline = RagPipeline()
    access = AccessContext(user_id="eval", roles=["employee"], allowed_scopes=["public"])

    for case in cases:
        pipeline.ingest(case["doc_id"], case["source"], case["content"], scope=case["scope"])

    keyword_hits = 0
    citation_hits = 0
    grounded = 0
    for case in cases:
        result = pipeline.query(case["question"], access)
        answer_lower = result.answer.lower()
        if all(kw.lower() in answer_lower for kw in case["expected_keywords"]):
            keyword_hits += 1
        if result.citations and result.citations[0].document_id == case["doc_id"]:
            citation_hits += 1
        if result.used_context and result.citations:
            grounded += 1

    n = len(cases)
    keyword_recall = keyword_hits / n
    citation_at_1 = citation_hits / n
    groundedness = grounded / n

    assert keyword_recall >= KEYWORD_RECALL_THRESHOLD, f"keyword recall too low: {keyword_recall}"
    assert citation_at_1 >= CITATION_AT_1_THRESHOLD, f"citation@1 too low: {citation_at_1}"
    assert groundedness == 1.0, f"groundedness too low: {groundedness}"
