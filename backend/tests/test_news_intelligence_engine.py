from fastapi.testclient import TestClient
from app.modules.news_intelligence.search_engine import news_query_parser, news_query_expander

def test_query_parser_and_expansion():
    parsed = news_query_parser.parse('"Chennai flood" viral video NOT storm')
    assert "Chennai flood" in parsed["exact_phrases"]
    assert "storm" in parsed["must_exclude"]
    assert len(parsed["detected_entities"]) >= 0

    expansions = news_query_expander.expand(parsed, "test_s_01")
    assert len(expansions) > 0
    for exp in expansions:
        assert exp.parent_query_id == "test_s_01"
        assert exp.generated_query
        assert exp.generated_reason

def test_api_news_search_and_relevance(client: TestClient, super_admin_headers):
    payload = {
        "query": "India election EVM malfunction",
        "search_mode": "SEMANTIC",
        "min_relevance": 50.0,
        "category_filter": "all"
    }
    res = client.post("/api/v1/news/search", json=payload, headers=super_admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["search_id"].startswith("nsrch_")
    assert data["original_query"] == "India election EVM malfunction"
    assert len(data["results"]) > 0

    for item in data["results"]:
        assert item["relevance_score"] >= 50.0
        assert item["investigation_status"] == "UNASSESSED"
        assert len(item["search_explanation"]) > 0

    # Verify search history
    hist_res = client.get("/api/v1/news/search/history", headers=super_admin_headers)
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert len(hist) > 0
    assert any("India election" in h["query"] for h in hist)

def test_api_investigation_lifecycle(client: TestClient, super_admin_headers):
    # 1. Create news investigation from search target
    inv_payload = {
        "original_query": "Chennai flood viral video",
        "target_input": "Viral video claiming catastrophic 2026 Chennai flood emergency, but meteorological reports confirm dry clear weather.",
        "preset_title": "Chennai Flood Video Attribution Investigation"
    }
    create_res = client.post("/api/v1/news/investigations", json=inv_payload, headers=super_admin_headers)
    assert create_res.status_code == 200
    inv = create_res.json()
    inv_id = inv["id"]
    assert inv_id.startswith("ninv_")
    assert inv["original_query"] == "Chennai flood viral video"
    assert len(inv["claims"]) > 0
    assert len(inv["evidence_vault"]) > 0
    assert len(inv["timeline"]) > 0
    assert inv["assessment"] is not None
    assert inv["assessment"]["confidence_breakdown"]["overall_confidence"] > 0

    # 2. Verify evidence retrieval explanation exists
    for ev in inv["evidence_vault"]:
        assert len(ev["retrieval_reason"]) > 0

    # 3. Retrieve investigation by ID
    get_res = client.get(f"/api/v1/news/investigations/{inv_id}", headers=super_admin_headers)
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["id"] == inv_id

    # 4. Generate 16-section Executive Report
    rep_res = client.post(f"/api/v1/news/investigations/{inv_id}/report", headers=super_admin_headers)
    assert rep_res.status_code == 200
    report = rep_res.json()
    assert report["investigation_id"] == inv_id
    assert report["what_was_claimed"]
    assert report["what_evidence_shows"]

def test_api_watchlists(client: TestClient, super_admin_headers):
    w_payload = {
        "topic_query": "India EVM tampering",
        "monitored_entities": ["Election Commission", "EVM"],
        "monitored_domains": ["thehindu.com", "ndtv.com"],
        "check_interval_hours": 6
    }
    create_res = client.post("/api/v1/news/watchlists", json=w_payload, headers=super_admin_headers)
    assert create_res.status_code == 200
    w = create_res.json()
    assert w["id"].startswith("nwt_")
    assert w["topic_query"] == "India EVM tampering"

    list_res = client.get("/api/v1/news/watchlists", headers=super_admin_headers)
    assert list_res.status_code == 200
    all_w = list_res.json()
    assert any(item["id"] == w["id"] for item in all_w)

    del_res = client.delete(f"/api/v1/news/watchlists/{w['id']}", headers=super_admin_headers)
    assert del_res.status_code == 200

def test_api_article_reader_and_investigative_pipeline(client: TestClient, super_admin_headers):
    # 1. Search to get a dynamic article ID
    s_res = client.post("/api/v1/news/search", json={"query": "Israel Iran conflict", "search_mode": "SEMANTIC"}, headers=super_admin_headers)
    assert s_res.status_code == 200
    results = s_res.json()["results"]
    assert len(results) > 0
    art_id = results[0]["id"]

    # 2. Get normalized internal long-form investigative article (DisInfoLab structure)
    art_res = client.get(f"/api/v1/news/articles/{art_id}?query_hint=Israel%20Iran", headers=super_admin_headers)
    assert art_res.status_code == 200
    article = art_res.json()
    assert article["id"] == art_id
    assert article["title"]
    assert len(article["sections"]) >= 3
    assert len(article["key_takeaways"]) >= 2
    assert len(article["claims"]) >= 2
    assert len(article["timeline"]) >= 3
    assert len(article["evidence"]) >= 3
    assert len(article["global_coverage"]) >= 3
    assert article["assessment"] is not None

    # 3. Investigate a specific claim
    claim_text = article["claims"][0]["claim_text"]
    claim_res = client.post(
        f"/api/v1/news/articles/{art_id}/investigate-claim",
        json={"claim_text": claim_text, "context_article_id": art_id},
        headers=super_admin_headers
    )
    assert claim_res.status_code == 200
    claim_data = claim_res.json()
    assert claim_data["claim_text"] == claim_text
    assert claim_data["verdict"] in ["VERIFIED", "MISLEADING", "PARTIALLY TRUE", "UNVERIFIED"]
    assert len(claim_data["supporting_sources"]) > 0

    # 4. Compare coverage across sources
    comp_res = client.post(
        "/api/v1/news/articles/compare",
        json={"article_ids": [art_id]},
        headers=super_admin_headers
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["comparison_id"].startswith("cmp_")
    assert len(comp_data["articles"]) > 0

    # 5. Researcher / Journalist Editorial Revision (Edit Dossier)
    edit_payload = {
        "title": "Revised Investigation: Israel Iran Geopolitical Telemetry",
        "verdict": "VERIFIED",
        "analyst_notes": "Reviewed and verified against primary technical telemetry logs by lead researcher.",
        "key_takeaways": ["Telemetry independently corroborated", "Archival provenance verified"]
    }
    edit_res = client.put(f"/api/v1/news/articles/{art_id}", json=edit_payload, headers=super_admin_headers)
    assert edit_res.status_code == 200
    edited = edit_res.json()
    assert edited["title"] == "Revised Investigation: Israel Iran Geopolitical Telemetry"
    assert edited["assessment"]["verdict"] == "VERIFIED"
    assert edited["analyst_notes"] == "Reviewed and verified against primary technical telemetry logs by lead researcher."
    assert edited["edited_by"] == "superadmin@sential.io"

    # 6. Soft Delete Dossier (hidden from user view, retained in database for audit compliance)
    del_res = client.delete(f"/api/v1/news/articles/{art_id}", headers=super_admin_headers)
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["is_deleted"] is True
    assert del_data["status"] == "ARCHIVED_HIDDEN"

    # Verify article is hidden from regular user requests (returns 404)
    hidden_res = client.get(f"/api/v1/news/articles/{art_id}", headers=super_admin_headers)
    assert hidden_res.status_code == 404

    # Verify data is still safely retained in the database/repository
    from app.modules.news_intelligence.repository import news_article_repo
    db_doc = news_article_repo.get_by_id(art_id, include_deleted=True)
    assert db_doc is not None
    assert db_doc["is_deleted"] is True
    assert db_doc["title"] == "Revised Investigation: Israel Iran Geopolitical Telemetry"


def test_advanced_global_news_intelligence_features(client: TestClient, super_admin_headers):
    """
    Tests the advanced verification pipeline:
    - Multi-provider search and story clustering
    - Source independence scoring (independent vs syndicated copies)
    - EV-001 traceable evidence and cryptographic provenance
    - Entity resolution and canonical alias mapping
    - Knowledge story graph (nodes and relationships)
    - ClaimReview Schema.org interoperability
    - AUTHENTIC MEDIA (FALSE CONTEXT) verdict distinction
    """
    # 1. Search with global query
    res = client.post("/api/v1/news/search", json={"query": "India election EVM 2026", "search_mode": "SEMANTIC"}, headers=super_admin_headers)
    assert res.status_code == 200
    search_data = res.json()
    assert len(search_data["results"]) > 0

    first_item = search_data["results"][0]
    assert "source_type" in first_item
    assert "is_independent" in first_item
    assert first_item["story_cluster"] is not None
    cluster = first_item["story_cluster"]
    assert cluster["independent_sources_count"] >= 1
    assert cluster["source_independence_score"] > 0

    # 2. Get investigative article dossier
    art_res = client.get(f"/api/v1/news/articles/{first_item['id']}?query_hint=India%20election%20EVM", headers=super_admin_headers)
    assert art_res.status_code == 200
    article = art_res.json()

    # Traceable evidence codes
    assert len(article["evidence"]) >= 3
    for ev in article["evidence"]:
        assert ev["evidence_code"] is not None
        assert ev["evidence_code"].startswith("EV-")
        assert len(ev["hash_value"]) == 64
        assert ev["extraction_method"]

    # Authentic Media with False Context verdict distinction
    assert article["assessment"]["verdict"] == "AUTHENTIC MEDIA (FALSE CONTEXT)"
    assert len(article["why_misleading_reasons"]) >= 3

    # Entity resolution
    assert len(article["resolved_entities"]) >= 3
    for rent in article["resolved_entities"]:
        assert rent["canonical_id"]
        assert rent["canonical_name"]
        assert len(rent["aliases"]) > 0

    # Knowledge story graph
    assert article["story_graph"] is not None
    assert len(article["story_graph"]["nodes"]) >= 5
    assert len(article["story_graph"]["edges"]) >= 5
    node_types = [n["node_type"] for n in article["story_graph"]["nodes"]]
    assert "EVENT" in node_types
    assert "ARTICLE" in node_types
    assert "CLAIM" in node_types
    assert "EVIDENCE" in node_types

    # Source independence breakdown
    assert article["source_independence_breakdown"] is not None
    assert "independent_sources_count" in article["source_independence_breakdown"]
    assert "syndicated_reprints_count" in article["source_independence_breakdown"]

    # ClaimReview interoperability
    assert article["claim_review_interoperability"] is not None


