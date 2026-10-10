from typing import Any, Dict, List, Optional
from app.modules.social_media_intelligence.models import (
    CredibilityScore,
    CredibilityBand,
    SocialPlatformType,
    SocialPost
)

class CredibilityEngine:
    """
    Social Media Account Credibility & Bot Probability Scoring Engine.
    Computes an explainable 0–100 credibility index with multi-factor breakdown.
    """

    def score_account(
        self,
        target_handle: str,
        platform: SocialPlatformType,
        posts: List[SocialPost],
        account_age_days: Optional[int] = None,
        has_custom_avatar: bool = True
    ) -> CredibilityScore:
        factors: Dict[str, float] = {}

        # 1. Posting Velocity Factor (0 to 20 pts)
        post_count = len(posts)
        if post_count <= 20:
            velocity_score = 20.0
        elif post_count <= 60:
            velocity_score = 15.0
        elif post_count <= 150:
            velocity_score = 10.0
        else:
            velocity_score = 4.0  # Hyperactive posting characteristic of automated bots
        factors["velocity"] = velocity_score

        # 2. Text Repetition Factor (0 to 30 pts)
        if post_count > 1:
            unique_texts = len({p.text[:60] for p in posts})
            repetition_rate = 1.0 - (unique_texts / post_count)
            text_score = max(30.0 * (1.0 - repetition_rate), 5.0)
        else:
            repetition_rate = 0.0
            text_score = 28.0
        factors["text_diversity"] = round(text_score, 1)

        # 3. Domain & Link Diversity Factor (0 to 25 pts)
        all_links = [link for p in posts for link in p.links]
        if all_links:
            unique_domains = len({link.split('/')[2] for link in all_links if len(link.split('/')) > 2})
            diversity_rate = min(unique_domains / len(all_links), 1.0)
            domain_score = 15.0 + (10.0 * diversity_rate)
        else:
            diversity_rate = 1.0
            domain_score = 22.0
        factors["link_diversity"] = round(domain_score, 1)

        # 4. Profile Completeness & Age Factor (0 to 25 pts)
        age_days = account_age_days or 180
        age_score = min(age_days / 30.0, 15.0)  # Up to 15 pts for > 15 months
        avatar_score = 10.0 if has_custom_avatar else 0.0
        factors["profile_maturity"] = round(age_score + avatar_score, 1)

        total_score = round(sum(factors.values()), 1)
        total_score = min(max(total_score, 0.0), 100.0)

        # Classify Band
        if total_score >= 75.0:
            band = CredibilityBand.HIGH
            bot_prob = 0.08
            rationale = "High credibility score: organic content diversity, mature account history, and human-typical posting intervals."
        elif total_score >= 50.0:
            band = CredibilityBand.MODERATE
            bot_prob = 0.28
            rationale = "Moderate credibility: active dissemination patterns observed with standard multi-topic variety."
        elif total_score >= 30.0:
            band = CredibilityBand.LOW
            bot_prob = 0.65
            rationale = "Low credibility: elevated repetition rate and narrow domain citation patterns warrant analyst scrutiny."
        else:
            band = CredibilityBand.INAUTHENTIC
            bot_prob = 0.88
            rationale = "Inauthentic indicators detected: repetitive duplicate message broadcasting, rapid velocity bursts, and unverified profile markers."

        return CredibilityScore(
            target=target_handle,
            platform=platform,
            overall_score=total_score,
            band=band,
            account_age_days=age_days,
            post_velocity_per_day=round(post_count / max(age_days / 30.0, 1.0), 1),
            has_custom_avatar=has_custom_avatar,
            text_repetition_rate=round(repetition_rate, 2),
            domain_diversity_score=round(diversity_rate, 2),
            bot_probability=round(bot_prob, 2),
            factors=factors,
            rationale=rationale
        )

credibility_engine = CredibilityEngine()
