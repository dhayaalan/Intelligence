import pytest
from app.modules.news_intelligence.country_registry import (
    global_country_registry,
    CountrySourceRecord,
)
from app.modules.news_intelligence.models import (
    NewsSearchRequest,
    NewsSearchResponse,
)
from app.modules.news_intelligence.search_engine import news_retrieval_engine


class TestGlobalCountryRegistry:
    def test_registry_completeness_iso3166(self):
        """Verify the dynamic country registry includes comprehensive ISO 3166-1 countries."""
        all_countries = global_country_registry.get_all_countries()
        assert len(all_countries) >= 240, f"Expected >= 240 countries/territories, got {len(all_countries)}"
        
        # Verify diversity of regions across all continents
        regions = {c.region for c in all_countries}
        assert "Americas" in regions
        assert "Europe" in regions
        assert "Asia" in regions
        assert "Africa" in regions
        assert "Oceania" in regions

        # Verify attributes exist on each country entry
        for c in all_countries:
            assert len(c.alpha2) == 2
            assert len(c.alpha3) == 3
            assert c.name
            assert c.region
            assert isinstance(c.languages, list)
            assert isinstance(c.tlds, list)

    def test_country_resolution_by_alpha2_alpha3_name_and_aliases(self):
        """Verify robust resolution across codes, names, and aliases."""
        # Alpha-2
        fr = global_country_registry.resolve_country("FR")
        assert fr is not None and fr.name == "France"

        jp = global_country_registry.resolve_country("JP")
        assert jp is not None and jp.name == "Japan"

        ng = global_country_registry.resolve_country("NG")
        assert ng is not None and ng.name == "Nigeria"

        # Alpha-3
        de = global_country_registry.resolve_country("DEU")
        assert de is not None and de.name == "Germany"

        br = global_country_registry.resolve_country("BRA")
        assert br is not None and br.name == "Brazil"

        # Canonical Name & Case-insensitivity
        in_c = global_country_registry.resolve_country("india")
        assert in_c is not None and in_c.alpha2 == "IN"

        # Aliases
        uk = global_country_registry.resolve_country("UK")
        assert uk is not None and uk.alpha2 == "GB"

        usa = global_country_registry.resolve_country("USA")
        assert usa is not None and usa.alpha2 == "US"

        russia = global_country_registry.resolve_country("Russian Federation")
        assert russia is not None and russia.alpha2 == "RU"

    def test_country_resolution_by_tld(self):
        """Verify detection of country by top-level domain."""
        de = global_country_registry.resolve_by_tld(".de")
        assert de is not None and de.name == "Germany"

        jp = global_country_registry.resolve_by_tld(".jp")
        assert jp is not None and jp.name == "Japan"

        in_c = global_country_registry.resolve_by_tld(".in")
        assert in_c is not None and in_c.name == "India"

    def test_publisher_detection_from_source_or_url(self):
        """Verify publisher country inference from known outlet names and TLDs."""
        # Known outlet name
        c_reuters, code_reuters = global_country_registry.detect_publisher_country(source_name="Reuters")
        assert code_reuters == "GB" or c_reuters == "United Kingdom"

        c_lemonde, code_lemonde = global_country_registry.detect_publisher_country(source_name="Le Monde")
        assert code_lemonde == "FR"

        c_dw, code_dw = global_country_registry.detect_publisher_country(source_name="Deutsche Welle")
        assert code_dw == "DE"

        # TLD-based detection
        c_url, code_url = global_country_registry.detect_publisher_country(url="https://news.tokyo.jp/article/123")
        assert code_url == "JP"

    def test_custom_source_registration(self):
        """Verify adding new source dynamically to country registry without code modification."""
        source = CountrySourceRecord(
            publisher_name="AllAfrica News Bureau",
            domain="allafrica.com",
            feed_url="https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",
            language="en",
            source_type="COMMERCIAL",
            is_verified=True,
        )
        registered = global_country_registry.register_custom_source("ZA", source)
        assert registered is True

        za = global_country_registry.get_country("ZA")
        assert za is not None
        assert "allafrica.com" in [s.domain for s in za.sources]


class TestGeographicDimensionsAndSeparation:
    def test_publisher_country_vs_event_location_separation(self):
        """
        Verify rule #6: Never infer publisher country solely from event location or IP.
        An Indian outlet reporting on Paris must preserve:
        publisher_country='India', event_location='France'.
        """
        text = "French President Emmanuel Macron spoke today in Paris regarding new European Union policies."
        publisher = "The Hindu"

        pub_country, pub_code = global_country_registry.detect_publisher_country(source_name=publisher)
        assert pub_code == "IN", f"Expected India publisher for The Hindu, got {pub_code}"

        event_loc = news_retrieval_engine._extract_event_location(text)
        assert event_loc == "France", f"Expected event location France, got {event_loc}"
        assert pub_country != event_loc, "Publisher country and event location must remain strictly distinct"

    def test_unknown_publisher_country_handling(self):
        """Unknown publisher country returns UNKNOWN/UNVERIFIED instead of inventing data."""
        c_name, c_code = global_country_registry.detect_publisher_country(source_name="Generic Obscure Blog 99")
        assert c_code is None
        assert c_name == "UNKNOWN"


class TestGlobalSearchAndComparisonEngine:
    def test_multi_country_comparison_matrix_generation(self):
        """Verify comparative analysis matrix contains real metrics and zero fabricated narratives."""
        import asyncio
        req = NewsSearchRequest(
            query="renewable energy transition",
            countries=["FR", "DE", "IN"],
            compare_countries=True,
            min_relevance=40,
        )
        res = asyncio.run(news_retrieval_engine.search(req))
        assert isinstance(res, NewsSearchResponse)
        assert res.country_comparison_matrix is not None
        assert len(res.country_comparison_matrix) >= 3

        matrix_codes = {row.country_code for row in res.country_comparison_matrix}
        assert "FR" in matrix_codes
        assert "DE" in matrix_codes
        assert "IN" in matrix_codes

        for row in res.country_comparison_matrix:
            assert row.country_name
            assert row.region
            assert row.operational_status in [
                "WORKING_TESTED_REAL",
                "VERIFIED_COVERAGE",
                "UNVERIFIED_COVERAGE",
                "CONFIG_REQUIRED",
                "NO_MATCHING_RESULTS",
                "NO_MATCHING_ARTICLES",
                "NO_SOURCES_CONFIGURED",
                "UNVERIFIED",
                "PARTIAL",
            ]
            assert isinstance(row.coverage_gaps, list)
            assert 0 <= row.source_independence_score <= 100

    def test_worldwide_search_execution(self):
        """Verify worldwide search mode triggers multi-provider discovery without manual country selection."""
        import asyncio
        req = NewsSearchRequest(
            query="climate summit",
            is_worldwide=True,
            min_relevance=40,
        )
        res = asyncio.run(news_retrieval_engine.search(req))
        assert isinstance(res, NewsSearchResponse)
        assert res.coverage_summary is not None
        assert res.coverage_summary.get("mode") in ["WORLDWIDE", "COUNTRY_FILTERED", "GLOBAL_DISCOVERY"]
        assert "total_results_evaluated" in res.coverage_summary


class TestNewsApiEndpoints:
    def test_get_countries_endpoint(self, client, analyst_headers):
        """Verify /api/v1/news/countries returns complete global registry."""
        resp = client.get("/api/v1/news/countries", headers=analyst_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 240

    def test_get_single_country_endpoint(self, client, analyst_headers):
        """Verify /api/v1/news/countries/{code} returns detailed country metadata."""
        resp = client.get("/api/v1/news/countries/FR", headers=analyst_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["alpha2"] == "FR"
        assert data["name"] == "France"
        assert "Europe" in data["region"]

    def test_get_invalid_country_returns_404(self, client, analyst_headers):
        """Verify non-existent country code returns 404."""
        resp = client.get("/api/v1/news/countries/ZZZ_INVALID", headers=analyst_headers)
        assert resp.status_code == 404

    def test_get_coverage_summary_endpoint(self, client, analyst_headers):
        """Verify /api/v1/news/coverage-summary returns dynamic coverage matrix status."""
        resp = client.get("/api/v1/news/coverage-summary", headers=analyst_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_countries_registered" in data
        assert data["total_countries_registered"] >= 240
        assert "verified_countries_count" in data
        assert "supported_news_providers" in data

    def test_register_source_endpoint(self, client, analyst_headers):
        """Verify POST /api/v1/news/sources registers new publisher dynamically."""
        payload = {
            "publisher_name": "Sveriges Television",
            "canonical_domain": "svt.se",
            "country_code": "SE",
            "country_name": "Sweden",
            "original_language": "sv",
            "source_category": "news",
            "is_official": False,
            "is_verified": True,
            "feed_or_endpoint": "https://www.svt.se/nyheter/rss.xml",
        }
        resp = client.post("/api/v1/news/sources", json=payload, headers=analyst_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "registered"
        assert data["country"] == "Sweden"
