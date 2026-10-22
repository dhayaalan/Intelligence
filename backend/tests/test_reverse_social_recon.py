import pytest
from fastapi.testclient import TestClient
from app.core.database import db
from app.module_sdk.provider_adapter import ProviderRequest
from app.modules.osint.providers.reverse_social_recon import reverse_social_recon_provider


@pytest.mark.asyncio
async def test_reverse_social_recon_gravatar_integration(monkeypatch):
    """
    Verifies that reverse email lookup extracts verified social media accounts
    (Instagram, Twitter/X, GitHub) even when usernames are completely different from email.
    """
    mock_gravatar_entry = {
        "preferredUsername": "alex_surfer",
        "displayName": "Alexandre Dumas",
        "thumbnailUrl": "https://secure.gravatar.com/avatar/mock123.jpg",
        "profileUrl": "https://gravatar.com/alex_surfer",
        "aboutMe": "Photographer and traveler",
        "accounts": [
            {
                "shortname": "instagram",
                "url": "https://instagram.com/alex_travel_photos",
                "username": "alex_travel_photos"
            },
            {
                "shortname": "twitter",
                "url": "https://x.com/alex_tweets_99",
                "username": "alex_tweets_99"
            }
        ]
    }

    async def mock_query_gravatar(self, client, email):
        return mock_gravatar_entry

    async def mock_query_github(self, client, email):
        return {"login": "alex-code-dev", "html_url": "https://github.com/alex-code-dev", "avatar_url": "https://github.com/alex.png"}

    monkeypatch.setattr(reverse_social_recon_provider, "_query_gravatar", mock_query_gravatar.__get__(reverse_social_recon_provider))
    monkeypatch.setattr(reverse_social_recon_provider, "_query_github_by_email", mock_query_github.__get__(reverse_social_recon_provider))

    req = ProviderRequest(
        query="contact.alex.work@company-domain.org",
        target_type="email",
        options={"tenant_id": "tenant_acme"}
    )
    res = await reverse_social_recon_provider.execute(req)

    assert res.status == "success"
    raw_entities = res.raw_data.get("entities", [])
    raw_relationships = res.raw_data.get("relationships", [])

    # Discovered accounts should include: Gravatar (@alex_surfer), Instagram (@alex_travel_photos), Twitter (@alex_tweets_99), GitHub (@alex-code-dev)
    usernames = [e["value"] for e in raw_entities if str(e.get("type", "")).lower() in ["username", "entitytype.username"]]
    assert "@alex_surfer" in usernames
    assert "@alex_travel_photos" in usernames
    assert "@alex_tweets_99" in usernames
    assert "@alex-code-dev" in usernames

    # Check platforms in metadata
    insta_entity = next(e for e in raw_entities if e["value"] == "@alex_travel_photos")
    assert insta_entity["metadata"]["platform"] == "Instagram"
    assert insta_entity["metadata"]["profile_url"] == "https://instagram.com/alex_travel_photos"

    # Verify relationships connect email -> accounts
    rel_targets = [r["target_entity_value"] for r in raw_relationships]
    assert "@alex_travel_photos" in rel_targets
    assert "@alex-code-dev" in rel_targets


@pytest.mark.asyncio
async def test_reverse_social_recon_phone_linked_instagram_account():
    """
    Verifies that querying a phone number retrieves linked Instagram, Telegram,
    or other social accounts even when the username is completely different from the phone digits.
    """
    phone_number = "+919876543210"
    instagram_handle = "@cool_surfer_99"

    with db._lock:
        # Seed an existing corroborated account linked to this phone
        db.entities["ent_insta_surfer"] = {
            "id": "ent_insta_surfer",
            "tenant_id": "tenant_acme",
            "type": "username",
            "value": instagram_handle,
            "confidence": 0.95,
            "sources": ["Cross-Identifier Identity Registry"],
            "metadata": {
                "platform": "Instagram",
                "category": "Social Media",
                "profile_url": "https://instagram.com/cool_surfer_99",
                "avatar_url": "https://instagram.com/avatar_cool.jpg",
                "display_name": "Marcus Vance"
            }
        }
        db.relationships["rel_phone_insta"] = {
            "id": "rel_phone_insta",
            "tenant_id": "tenant_acme",
            "source_val": phone_number,
            "target_val": instagram_handle,
            "relationship_type": "OWNS",
            "confidence": 0.95,
            "sources": ["Cross-Identifier Identity Registry"],
            "metadata": {"platform": "Instagram"}
        }

    try:
        req = ProviderRequest(
            query=phone_number,
            target_type="phone",
            options={"tenant_id": "tenant_acme"}
        )
        res = await reverse_social_recon_provider.execute(req)

        assert res.status == "success"
        raw_entities = res.raw_data.get("entities", [])
        raw_relationships = res.raw_data.get("relationships", [])

        matched_values = [e["value"] for e in raw_entities]
        assert instagram_handle in matched_values

        insta_ent = next(e for e in raw_entities if e["value"] == instagram_handle)
        assert insta_ent["metadata"]["platform"] == "Instagram"
        assert insta_ent["metadata"]["profile_url"] == "https://instagram.com/cool_surfer_99"

        # Verify relationship connects phone to instagram
        rel = next(r for r in raw_relationships if r["target_entity_value"] == instagram_handle)
        assert rel["source_entity_value"] == phone_number
        assert str(rel["relationship_type"]).upper().endswith("OWNS")

    finally:
        with db._lock:
            db.entities.pop("ent_insta_surfer", None)
            db.relationships.pop("rel_phone_insta", None)


def test_api_search_phone_retrieves_differently_named_instagram_account(client: TestClient, analyst_headers):
    """
    End-to-end API test:
    When searching for a phone number in /api/v1/search, any associated social media account
    (e.g., Instagram with handle @cool_surfer_99) is returned in the entities and profiles.
    """
    phone_number = "+919876543210"
    instagram_handle = "@cool_surfer_99"

    with db._lock:
        db.entities["ent_phone_marcus"] = {
            "id": "ent_phone_marcus",
            "tenant_id": "tenant_acme",
            "type": "phone",
            "value": phone_number,
            "confidence": 1.0,
            "sources": ["telecom_registry"],
            "metadata": {"canonical_e164": phone_number}
        }
        db.entities["ent_insta_marcus"] = {
            "id": "ent_insta_marcus",
            "tenant_id": "tenant_acme",
            "type": "username",
            "value": instagram_handle,
            "confidence": 0.95,
            "sources": ["social_registry"],
            "metadata": {
                "platform": "Instagram",
                "category": "Social Media",
                "profile_url": "https://instagram.com/cool_surfer_99",
                "avatar_url": "https://instagram.com/avatar_cool.jpg"
            }
        }
        db.relationships["rel_marcus_phone_insta"] = {
            "id": "rel_marcus_phone_insta",
            "tenant_id": "tenant_acme",
            "source_val": phone_number,
            "target_val": instagram_handle,
            "relationship_type": "OWNS",
            "confidence": 0.95,
            "sources": ["social_identity_registry"],
            "metadata": {"platform": "Instagram"}
        }

    try:
        res = client.post(
            "/api/v1/search",
            json={"query": phone_number},
            headers=analyst_headers,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["is_exact_identifier"] is True
        assert data["target_type"] == "phone"
        assert data["normalized_identifier"] == phone_number

        entity_vals = [e["value"] for e in data["entities"]]
        assert phone_number in entity_vals
        assert instagram_handle in entity_vals

        # Check Instagram entity metadata
        insta = next(e for e in data["entities"] if e["value"] == instagram_handle)
        assert insta["type"] == "username"
        assert insta["metadata"]["platform"] == "Instagram"

        # Check that relationship connects them
        rel_pairs = [(r["source_entity_value"], r["target_entity_value"]) for r in data["relationships"]]
        assert (phone_number, instagram_handle) in rel_pairs or (instagram_handle, phone_number) in rel_pairs

    finally:
        with db._lock:
            db.entities.pop("ent_phone_marcus", None)
            db.entities.pop("ent_insta_marcus", None)
            db.relationships.pop("rel_marcus_phone_insta", None)
