import os
import re
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.modules.news_intelligence.models import ClaimMatrixStatus, ClaimVerificationMatrixItem

logger = logging.getLogger("sential.news.factcheck")


class FactCheckService:
    """
    Fact Check & Claim Corroboration Engine.
    Integrates with Google Fact Check Tools API, IFCN open fact-check feeds,
    and cross-publisher claim verification matrices.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")

    async def query_fact_checks(self, query: str) -> Dict[str, Any]:
        """
        Query verified fact-checking registries for prior verdicts.
        """
        clean_query = query.strip()
        now = datetime.now(timezone.utc).isoformat()

        if self.api_key:
            url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={httpx.URL(clean_query)}&key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=6.0) as client:
                    res = await client.get(url)
                    if res.status_code == 200:
                        data = res.json()
                        claims = data.get("claims", [])
                        parsed = []
                        for c in claims[:5]:
                            claim_reviews = c.get("claimReview", [])
                            reviews = []
                            for r in claim_reviews:
                                reviews.append({
                                    "publisher": r.get("publisher", {}).get("name"),
                                    "publisher_site": r.get("publisher", {}).get("site"),
                                    "url": r.get("url"),
                                    "title": r.get("title"),
                                    "review_date": r.get("reviewDate"),
                                    "textual_rating": r.get("textualRating")
                                })
                            parsed.append({
                                "text": c.get("text"),
                                "claimant": c.get("claimant"),
                                "claim_date": c.get("claimDate"),
                                "reviews": reviews
                            })
                        return {
                            "status": "LIVE_VERIFIED",
                            "source": "Google Fact Check Tools API v1alpha1",
                            "claims_found": parsed,
                            "count": len(parsed),
                            "fetched_at": now
                        }
            except Exception as e:
                logger.warning(f"Google Fact Check API query notice: {e}")

        # When API key is not supplied, transparently report CONFIG_REQUIRED with zero synthetic data
        return {
            "status": "CONFIG_REQUIRED",
            "source": "Google Fact Check Tools API",
            "requirement": "Set GOOGLE_FACT_CHECK_API_KEY in environment for live IFCN claimant queries",
            "claims_found": [],
            "count": 0,
            "fetched_at": now
        }

    def evaluate_claim_evidence(
        self,
        claim_id: str,
        claim_text: str,
        supporting_publishers: List[str],
        contradicting_publishers: List[str],
        origin_wire: Optional[str] = None,
        is_wire_syndicated: bool = False,
        fact_check_rating: Optional[str] = None
    ) -> ClaimVerificationMatrixItem:
        """
        Evaluates evidence tier strictly according to journalistic verification rules:
        - If prior fact check or reputable source contradicted the claim -> CONTRADICTED
        - If multiple independent publishers with distinct origin confirm -> CORROBORATED
        - If mixed contradictory and supportive reports exist -> DISPUTED
        - If multiple outlets simply repeat a single wire without independent checking -> SINGLE_SOURCE_REPEATED
        - If only one publisher or unverified sources exist -> UNVERIFIED
        - If no sources or broken coverage -> INSUFFICIENT_EVIDENCE
        """
        sup_clean = [p.strip() for p in supporting_publishers if p.strip()]
        con_clean = [p.strip() for p in contradicting_publishers if p.strip()]

        # Check fact-check verdict
        if fact_check_rating:
            f_lower = fact_check_rating.lower()
            if any(term in f_lower for term in ["false", "debunked", "incorrect", "misleading", "fake", "pants on fire"]):
                return ClaimVerificationMatrixItem(
                    claim_id=claim_id,
                    claim_text=claim_text,
                    verification_tier=ClaimMatrixStatus.CONTRADICTED,
                    independent_publishers_count=len(sup_clean),
                    syndicated_publishers_count=1 if is_wire_syndicated else 0,
                    origin_wire=origin_wire,
                    supporting_publishers=sup_clean,
                    contradicting_publishers=con_clean or ["IFCN Verified Fact Checker"],
                    confidence_score=94.0,
                    forensic_rationale=f"Claim contradicted by independent fact-check rating: '{fact_check_rating}'.",
                    evidence_references=["Google Fact Check Tools / IFCN Signatory"]
                )

        if con_clean and sup_clean:
            return ClaimVerificationMatrixItem(
                claim_id=claim_id,
                claim_text=claim_text,
                verification_tier=ClaimMatrixStatus.DISPUTED,
                independent_publishers_count=len(sup_clean),
                syndicated_publishers_count=1 if is_wire_syndicated else 0,
                origin_wire=origin_wire,
                supporting_publishers=sup_clean,
                contradicting_publishers=con_clean,
                confidence_score=70.0,
                forensic_rationale="Conflicting primary accounts: active dispute between reporting publishers.",
                evidence_references=sup_clean + con_clean
            )

        if con_clean and not sup_clean:
            return ClaimVerificationMatrixItem(
                claim_id=claim_id,
                claim_text=claim_text,
                verification_tier=ClaimMatrixStatus.CONTRADICTED,
                independent_publishers_count=0,
                syndicated_publishers_count=0,
                origin_wire=origin_wire,
                supporting_publishers=[],
                contradicting_publishers=con_clean,
                confidence_score=88.0,
                forensic_rationale="Claim explicitly contradicted by verified investigative reporting.",
                evidence_references=con_clean
            )

        if is_wire_syndicated and len(sup_clean) > 1:
            return ClaimVerificationMatrixItem(
                claim_id=claim_id,
                claim_text=claim_text,
                verification_tier=ClaimMatrixStatus.SINGLE_SOURCE_REPEATED,
                independent_publishers_count=1,
                syndicated_publishers_count=len(sup_clean),
                origin_wire=origin_wire or sup_clean[0],
                supporting_publishers=sup_clean,
                contradicting_publishers=[],
                confidence_score=65.0,
                forensic_rationale=(
                    f"Syndication detected: {len(sup_clean)} articles share identical origin wire text. "
                    "Multiple syndications of one wire do not constitute independent confirmations."
                ),
                evidence_references=[origin_wire] if origin_wire else sup_clean[:2]
            )

        if len(sup_clean) >= 2:
            return ClaimVerificationMatrixItem(
                claim_id=claim_id,
                claim_text=claim_text,
                verification_tier=ClaimMatrixStatus.CORROBORATED,
                independent_publishers_count=len(sup_clean),
                syndicated_publishers_count=0,
                origin_wire=origin_wire,
                supporting_publishers=sup_clean,
                contradicting_publishers=[],
                confidence_score=92.0,
                forensic_rationale=f"Claim independently corroborated across {len(sup_clean)} distinct journalistic newsrooms.",
                evidence_references=sup_clean
            )

        if len(sup_clean) == 1:
            return ClaimVerificationMatrixItem(
                claim_id=claim_id,
                claim_text=claim_text,
                verification_tier=ClaimMatrixStatus.UNVERIFIED,
                independent_publishers_count=1,
                syndicated_publishers_count=0,
                origin_wire=origin_wire,
                supporting_publishers=sup_clean,
                contradicting_publishers=[],
                confidence_score=50.0,
                forensic_rationale="Single-source report: requires independent cross-outlet corroboration.",
                evidence_references=sup_clean
            )

        return ClaimVerificationMatrixItem(
            claim_id=claim_id,
            claim_text=claim_text,
            verification_tier=ClaimMatrixStatus.INSUFFICIENT_EVIDENCE,
            independent_publishers_count=0,
            syndicated_publishers_count=0,
            origin_wire=None,
            supporting_publishers=[],
            contradicting_publishers=[],
            confidence_score=20.0,
            forensic_rationale="Insufficient evidence: no verifiable publishers or wire dispatches found.",
            evidence_references=[]
        )


fact_check_service = FactCheckService()
