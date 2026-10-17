"""
Regression test suite for Identifier Search Accuracy.
Validates email and phone number exact search semantics, normalization,
zero-silent-fallback rules, query intent classification, and non-pollution
of identifier queries by fuzzy/semantic or unrelated text matches.
"""

import pytest
from fastapi.testclient import TestClient
from app.search.normalization import (
    normalize_email,
    normalize_phone,
    classify_query_intent_and_mode,
    verify_identifier_match,
)
from app.core.database import db


def test_unit_email_normalization_and_validation():
    # Valid emails: trimming and lowercase domain/canonicalization
    res, err = normalize_email("  Target.User@Example.COM  ")
    assert err is None
    assert res is not None
    assert res.canonical_email == "Target.User@example.com"

    res2, err2 = normalize_email("investigator@sential.io")
    assert err2 is None
    assert res2.canonical_email == "investigator@sential.io"

    # Preserves plus-addressing without unsafe stripping
    res3, err3 = normalize_email("user+tag@gmail.com")
    assert err3 is None
    assert res3.canonical_email == "user+tag@gmail.com"

    # Invalid emails
    assert normalize_email("not-an-email")[0] is None
    assert normalize_email("@missing-user.com")[0] is None
    assert normalize_email("missing-domain@")[0] is None
    assert normalize_email("")[0] is None


def test_unit_phone_normalization_e164():
    # Valid US number
    res_us, err_us = normalize_phone("+1 415 555 2671")
    assert err_us is None
    assert res_us is not None
    assert res_us.e164 == "+14155552671"
    assert res_us.country_code == 1

    # Valid UK number
    res_uk, err_uk = normalize_phone("+44 20 7946 0991")
    assert err_uk is None
    assert res_uk is not None
    assert res_uk.e164 == "+442079460991"
    assert res_uk.country_code == 44

    # Valid international without spaces
    res_in, err_in = normalize_phone("+919876543210")
    assert err_in is None
    assert res_in is not None
    assert res_in.e164 == "+919876543210"

    # Ambiguous or invalid phone numbers
    assert normalize_phone("123")[0] is None
    assert normalize_phone("abcdef")[0] is None


def test_unit_query_intent_classification():
    # Email detection
    class_email = classify_query_intent_and_mode("analyst@acme.com")
    assert class_email["is_identifier"] is True
    assert class_email["identifier_type"] == "EMAIL"
    assert class_email["search_mode"] == "EXACT_IDENTIFIER"
    assert class_email["active_search_mode_label"] == "Exact email search"
    assert class_email["normalized_value"] == "analyst@acme.com"

    # Phone detection
    class_phone = classify_query_intent_and_mode("+14155552671")
    assert class_phone["is_identifier"] is True
    assert class_phone["identifier_type"] == "PHONE"
    assert class_phone["search_mode"] == "EXACT_IDENTIFIER"
    assert class_phone["active_search_mode_label"] == "Exact phone search"
    assert class_phone["normalized_value"] == "+14155552671"

    # General text query
    class_text = classify_query_intent_and_mode("Operation Dark Sky Syndicate")
    assert class_text["is_identifier"] is False
    assert class_text["search_mode"] == "TEXT_SEARCH"
    assert class_text["active_search_mode_label"] == "Text search"

    # Explicit semantic query
    class_sem = classify_query_intent_and_mode("What infrastructure was observed in Eastern Europe?")
    assert class_sem["is_identifier"] is False
    assert class_sem["search_mode"] == "SEMANTIC_SEARCH"
    assert class_sem["active_search_mode_label"] == "Semantic text search"


def test_unit_server_side_verification_strictness():
    # Email verification: exact match required
    assert verify_identifier_match(
        "EMAIL",
        "suspect@darkweb.org",
        "email",
        "suspect@darkweb.org"
    ) is True

    # Case insensitive canonical equality
    assert verify_identifier_match(
        "EMAIL",
        "suspect@darkweb.org",
        "email",
        "SUSPECT@DARKWEB.ORG"
    ) is True

    # Substring or similar domain must NOT match
    assert verify_identifier_match(
        "EMAIL",
        "suspect@darkweb.org",
        "email",
        "notsuspect@darkweb.org"
    ) is False

    # Phone verification: exact E.164 match required
    assert verify_identifier_match(
        "PHONE",
        "+14155552671",
        "phone",
        "+14155552671"
    ) is True

    # Partial digit overlap must NOT match
    assert verify_identifier_match(
        "PHONE",
        "+14155552671",
        "phone",
        "+14155552672"
    ) is False

    # Phone appearing in article body text is rejected as contact number
    assert verify_identifier_match(
        "PHONE",
        "+14155552671",
        "article",
        "Call us at +14155552671 for tips"
    ) is False


def test_api_nonexistent_email_returns_zero_matches(client: TestClient, analyst_headers):
    """
    Searching for a nonexistent email must return ZERO exact matches.
    It must NOT silently fall back to fuzzy, full-text, or semantic matches,
    nor fabricate synthetic profiles or relationships.
    """
    res = client.post(
        "/api/v1/search",
        json={"query": "nonexistent.investigator.target@unknown-domain-404.org"},
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_exact_identifier"] is True
    assert data["search_mode"] == "EXACT_IDENTIFIER"
    assert data["active_search_mode_label"] == "Exact email search"
    assert data["target_type"] == "email"
    assert data["normalized_identifier"] == "nonexistent.investigator.target@unknown-domain-404.org"

    # Strict zero match assertions
    assert len(data["entities"]) == 0
    assert len(data["relationships"]) == 0
    assert len(data["evidence"]) == 0
    assert data["investigation_snapshot"]["entities_count"] == 0


def test_api_nonexistent_phone_returns_zero_matches(client: TestClient, analyst_headers):
    """
    Searching for a nonexistent international phone number returns ZERO matches.
    Must not return profiles with similar digits or partial overlaps.
    """
    res = client.post(
        "/api/v1/search",
        json={"query": "+1 202 555 0199"},
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_exact_identifier"] is True
    assert data["search_mode"] == "EXACT_IDENTIFIER"
    assert data["active_search_mode_label"] == "Exact phone search"
    assert data["target_type"] == "phone"
    assert data["normalized_identifier"] == "+12025550199"

    # Strict zero match assertions
    assert len(data["entities"]) == 0
    assert len(data["relationships"]) == 0
    assert len(data["evidence"]) == 0


def test_api_existing_email_returns_exact_verified_record(client: TestClient, analyst_headers):
    """
    Searching for a seeded/existing email in the identity store returns records
    with that exact normalized email.
    """
    with db._lock:
        db.entities["ent_seeded_email_target"] = {
            "id": "ent_seeded_email_target",
            "tenant_id": "tenant_acme",
            "type": "email",
            "value": "subject.target@syndicate.net",
            "confidence": 1.0,
            "sources": ["osint_corporate_records"],
            "metadata": {"name": "Target Subject X"},
        }

    try:
        # Search using mixed casing and whitespace
        res = client.post(
            "/api/v1/search",
            json={"query": "  Subject.Target@Syndicate.Net  "},
            headers=analyst_headers,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["is_exact_identifier"] is True
        assert data["search_mode"] == "EXACT_IDENTIFIER"
        assert data["normalized_identifier"].lower() == "subject.target@syndicate.net"

        # Verified entity returned
        assert len(data["entities"]) >= 1
        matched_values = [e["value"].lower() for e in data["entities"]]
        assert "subject.target@syndicate.net" in matched_values

    finally:
        with db._lock:
            db.entities.pop("ent_seeded_email_target", None)


def test_api_existing_phone_returns_exact_verified_record(client: TestClient, analyst_headers):
    """
    Searching for an existing international phone returns verified matching records.
    """
    with db._lock:
        db.entities["ent_seeded_phone_target"] = {
            "id": "ent_seeded_phone_target",
            "tenant_id": "tenant_acme",
            "type": "phone",
            "value": "+442079460991",
            "confidence": 1.0,
            "sources": ["telecom_registry"],
            "metadata": {"carrier": "British Telecom"},
        }

    try:
        # Search with international formatting spaces
        res = client.post(
            "/api/v1/search",
            json={"query": "+44 20 7946 0991"},
            headers=analyst_headers,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["is_exact_identifier"] is True
        assert data["search_mode"] == "EXACT_IDENTIFIER"
        assert data["normalized_identifier"] == "+442079460991"

        assert len(data["entities"]) >= 1
        matched_phones = [e["value"] for e in data["entities"]]
        assert "+442079460991" in matched_phones

    finally:
        with db._lock:
            db.entities.pop("ent_seeded_phone_target", None)


def test_api_invalid_identifier_explicit_validation_rejection(client: TestClient, analyst_headers):
    """
    Invalid identifiers must follow explicit validation and not be executed as normal targets.
    """
    # Malformed email with @ but missing domain
    res = client.post(
        "/api/v1/search",
        json={"query": "user-without-domain@"},
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data.get("validation_error") is not None
    assert "Invalid email format" in data["validation_error"]
    assert len(data["entities"]) == 0


def test_api_general_text_search_still_works(client: TestClient, analyst_headers):
    """
    General text and keyword queries continue to function in their appropriate mode
    without being blocked by identifier constraints.
    """
    res = client.post(
        "/api/v1/search",
        json={"query": "Cyber Espionage Threat Actor APT29"},
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_exact_identifier"] is False
    assert data["search_mode"] in ["TEXT_SEARCH", "SEMANTIC_SEARCH"]
    assert data["target_type"] in ["keyword", "text"]
    assert len(data["module_jobs"]) > 0
