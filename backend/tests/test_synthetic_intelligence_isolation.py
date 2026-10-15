import pytest
from app.module_registry.registry import module_registry
from app.modules.example_intelligence.module import example_module
from app.modules.test_intelligence.module import test_intelligence_module
from app.module_sdk.models import SearchContext
from app.search.orchestrator import SearchOrchestrator
from app.search.schemas import SearchRequest
from app.identity.models import UserRecord, UserRole
from app.core.config import settings


@pytest.mark.asyncio
async def test_synthetic_modules_can_be_disabled_and_isolated():
    """Verify synthetic modules when disabled are not active."""
    module_registry.disable_module("example_intelligence")
    module_registry.disable_module("test_intelligence")
    assert not module_registry.is_module_enabled("example_intelligence")
    assert not module_registry.is_module_enabled("test_intelligence")


@pytest.mark.asyncio
async def test_search_orchestrator_excludes_synthetic_modules():
    """Verify SearchOrchestrator excludes disabled synthetic modules from default search scopes."""
    module_registry.disable_module("example_intelligence")
    module_registry.disable_module("test_intelligence")
    all_registered = module_registry.list_modules()
    extra_pluggable = [
        m for m in all_registered
        if m not in ["osint", "threat_intelligence", "news_intelligence", "social_media_intelligence"]
        and module_registry.is_module_enabled(m)
    ]
    assert "example_intelligence" not in extra_pluggable
    assert "test_intelligence" not in extra_pluggable


@pytest.mark.asyncio
async def test_test_intelligence_production_isolation(monkeypatch):
    """Verify test_intelligence module never produces synthetic entities in production."""
    monkeypatch.setattr(settings, "APP_ENV", "production")
    ctx = SearchContext(
        search_id="test_srch_1",
        tenant_id="tenant_default",
        user_id="usr_test_1",
        query="target-corp.com",
        target_type="domain"
    )
    res = await test_intelligence_module.search(ctx)
    assert res.status == "skipped"
    assert len(res.entities) == 0
    assert len(res.evidence) == 0


@pytest.mark.asyncio
async def test_example_intelligence_tags_synthetic_fixtures():
    """Verify example_intelligence tags all generated entities with is_synthetic=True."""
    ctx = SearchContext(
        search_id="test_srch_2",
        tenant_id="tenant_default",
        user_id="usr_test_1",
        query="target-corp.com",
        target_type="domain"
    )
    res = await example_module.search(ctx)
    assert len(res.entities) > 0
    assert res.entities[0].metadata.get("is_synthetic") is True
    assert res.entities[0].metadata.get("plugin_demonstration") is True
