from app.rag.graph import RagPipeline
from app.schemas import AccessContext


def test_end_to_end_rag_with_citations():
    pipeline = RagPipeline()
    pipeline.ingest(
        document_id="handbook",
        source="handbook.md",
        content=(
            "Employees accrue 20 days of paid time off per year. "
            "PTO requests must be approved by a direct manager. "
            "Unused PTO rolls over up to a maximum of 5 days."
        ),
        scope="public",
    )
    access = AccessContext(user_id="u1", roles=["employee"], allowed_scopes=["public"])
    result = pipeline.query("How many PTO days do employees get?", access)

    assert result.used_context is True
    assert result.citations, "expected at least one citation"
    assert "20 days" in result.answer
    # citation markers should be present in an offline extractive answer
    assert "[1]" in result.answer


def test_permission_aware_answer_excludes_forbidden_scope():
    pipeline = RagPipeline()
    pipeline.ingest(
        document_id="salaries",
        source="salaries.csv",
        content="The CEO salary is 1000000 dollars per year.",
        scope="hr-confidential",
    )
    access = AccessContext(user_id="u2", roles=["employee"], allowed_scopes=["public"])
    result = pipeline.query("What is the CEO salary?", access)

    assert result.used_context is False
    assert "1000000" not in result.answer
    assert result.citations == []


def test_answer_reflects_only_allowed_docs():
    pipeline = RagPipeline()
    pipeline.ingest("d1", "public.txt", "The office wifi password is guest123.", scope="public")
    pipeline.ingest("d2", "secret.txt", "The admin password is root456.", scope="admin")

    employee = AccessContext(user_id="e", roles=["employee"], allowed_scopes=["public"])
    admin = AccessContext(user_id="a", roles=["admin"], allowed_scopes=["public", "admin"])

    emp_result = pipeline.query("what is the password", employee)
    admin_result = pipeline.query("what is the admin password", admin)

    assert "root456" not in emp_result.answer
    assert any(c.document_id == "d2" for c in admin_result.citations)
