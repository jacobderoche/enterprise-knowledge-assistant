"""Pytest fixtures: reset global singletons between tests."""
import pytest

from app.rag import graph, vectorstore


@pytest.fixture(autouse=True)
def _reset_state():
    vectorstore.reset_vector_store()
    graph.reset_pipeline()
    yield
    vectorstore.reset_vector_store()
    graph.reset_pipeline()
