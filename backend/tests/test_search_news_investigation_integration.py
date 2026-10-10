from fastapi.testclient import TestClient
from app.core.database import db

def test_search_orchestration_persists_news_intelligence_to_investigation(client: TestClient, analyst_headers):
    query_target = "Kashmir conflict escalation viral video"
    
    # 1. Execute universal search from main search module with Deep Scan
    res = client.post(
        "/api/v1/search",
        json={
            "query": query_target,
            "target_type": "text",
            "selected_modules": ["osint", "threat_intelligence", "news_intelligence"]
        },
        headers=analyst_headers
    )
    assert res.status_code == 200
    search_data = res.json()
    
    # Verify module execution includes news_intelligence
    executed_mods = [j["module"] for j in search_data["module_jobs"]]
    assert "news_intelligence" in executed_mods
    assert "osint" in executed_mods
    assert "threat_intelligence" in executed_mods
    
    # Verify entities and evidence returned contain news data
    news_entities = [e for e in search_data["entities"] if "news_intelligence" in (e.get("sources") or [])]
    assert len(news_entities) > 0, "Expected entities extracted by news_intelligence"
    
    news_evidence = [ev for ev in search_data["evidence"] if ev.get("module") == "news_intelligence"]
    assert len(news_evidence) > 0, "Expected evidence produced by news_intelligence"
    
    # 2. Verify auto-created investigation in Investigations Repository
    inv_list_res = client.get("/api/v1/investigations", headers=analyst_headers)
    assert inv_list_res.status_code == 200
    investigations = inv_list_res.json()
    
    matching_inv = next((inv for inv in investigations if inv.get("target") == query_target), None)
    assert matching_inv is not None, f"Investigation targeting '{query_target}' should be created"
    inv_id = matching_inv["id"]
    
    # 3. Verify Investigation Detail includes linked entities and evidence
    detail_res = client.get(f"/api/v1/investigations/{inv_id}", headers=analyst_headers)
    assert detail_res.status_code == 200
    inv_detail = detail_res.json()
    assert inv_detail["id"] == inv_id
    
    # Verify evidence linked to investigation
    ev_res = client.get(f"/api/v1/evidence?investigation_id={inv_id}", headers=analyst_headers)
    assert ev_res.status_code == 200
    evidence_vault = ev_res.json()
    assert any(ev.get("module") == "news_intelligence" for ev in evidence_vault)
    
    # 4. Verify News Investigation Record is auto-created and attached to this case
    news_invs_res = client.get("/api/v1/news/investigations", headers=analyst_headers)
    assert news_invs_res.status_code == 200
    news_invs = news_invs_res.json()
    
    matching_news_inv = next((n for n in news_invs if n.get("associated_case_id") == inv_id or n.get("original_query") == query_target), None)
    assert matching_news_inv is not None, "News investigation record should be created and linked to the case"
    assert matching_news_inv["associated_case_id"] == inv_id
    assert len(matching_news_inv["claims"]) > 0
    assert len(matching_news_inv["timeline"]) > 0
    assert matching_news_inv["assessment"] is not None
