"""
Test Suite: ML Integration Contract Decoupling & Boundary Verification

Verifies:
1. Legacy AI endpoints are completely unregistered (HTTP 404).
2. The ML integration contract status endpoint returns NOT_CONFIGURED when external services are unconfigured.
3. Analysis dispatches return explicit NOT_CONFIGURED status without fabricated predictions.
4. Deterministic summary builder and dossier compiler execute without LLMs.
"""

from fastapi.testclient import TestClient
from app.investigations.summary_builder import summary_builder
from app.modules.news_intelligence.dossier_compiler import news_dossier_compiler
from app.ml_contracts.models import MLExecutionStatus


def test_legacy_ai_endpoints_unregistered(client: TestClient, super_admin_headers):
    """
    Verifies that deleted AI endpoints (/api/v1/agents/*) are completely unregistered.
    """
    res1 = client.post(
        "/api/v1/agents/grounded-analysis",
        json={"target": "test", "query": "test"},
        headers=super_admin_headers
    )
    assert res1.status_code == 404

    res2 = client.post(
        "/api/v1/agents/persona-correlation",
        json={"target": "test"},
        headers=super_admin_headers
    )
    assert res2.status_code == 404


def test_ml_contract_status_not_configured(client: TestClient, super_admin_headers):
    """
    Verifies that the decoupled ML contract reports not_configured when no external
    ML microservice URL is set in environment.
    """
    res = client.get("/api/v1/ml/status", headers=super_admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == MLExecutionStatus.NOT_CONFIGURED.value
    assert data["is_configured"] is False
    assert "not configured" in data["message"].lower()


def test_ml_analysis_request_returns_not_configured(client: TestClient, super_admin_headers):
    """
    Verifies that unconfigured ML inference returns explicit NOT_CONFIGURED status
    and never fabricates predictions or mock answers.
    """
    payload = {
        "target": "Suspicious Activity",
        "target_type": "DOMAIN",
        "query": "Evaluate infrastructure risk",
        "context": {
            "tenant_id": "tenant-default",
            "user_id": "admin-user",
            "trace_id": "trace-test-123"
        },
        "evidence": []
    }
    res = client.post("/api/v1/ml/analyze", json=payload, headers=super_admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == MLExecutionStatus.NOT_CONFIGURED.value
    assert data["synthesis"] is None
    assert "not configured" in data["error_message"].lower()


def test_deterministic_summary_builder():
    """
    Verifies that core investigation summaries are generated deterministically
    without requiring any model inference runtime.
    """
    entities = [
        {"type": "IP", "value": "198.51.100.1"},
        {"type": "SUBDOMAIN", "value": "vpn.example.com"}
    ]
    evidence = [
        {"id": "ev-1", "hash": "sha256-abc"}
    ]
    summary = summary_builder.generate_summary(
        target="example.com",
        target_type="domain",
        entities=entities,
        evidence=evidence,
        priority="HIGH"
    )
    assert len(summary.what_we_know) >= 2
    assert any("198.51.100.1" in item for item in summary.what_we_know)
    assert len(summary.investigative_leads) >= 1
    assert summary.investigation_health["entity_resolution"] in ["HIGH", "MEDIUM", "LOW"]


def test_deterministic_news_dossier_compiler():
    """
    Verifies that news article dossier structuring operates deterministically
    via regex, readability scoring, and source profiling without an LLM.
    """
    article = news_dossier_compiler.compile_article(
        article_id="art-test-001",
        title="Major Telecom Network Outage Hits Financial Core",
        summary="A critical fiber line severed causing temporary routing degradation.",
        content="A critical fiber line severed this morning causing widespread packet loss across three exchanges.",
        canonical_url="https://wire.example.com/telecom-outage",
        publisher="Global Wire Dispatch",
        country="US",
        publication_date="2026-10-10T08:00:00Z",
        detected_entities=["Telecom Core", "DWDM Ring"]
    )
    assert "telecom" in article.title.lower()
    assert article.relevance_score > 0
    assert len(article.detected_entities) >= 2
    assert len(article.key_takeaways) > 0
    assert article.publisher == "Global Wire Dispatch"
