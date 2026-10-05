import hashlib
from typing import List, Dict, Any, Tuple
from app.modules.threat_intelligence.engines.base import NormalizedFinding


class FindingNormalizer:
    """
    Deduplicates and correlates findings across multiple scanning engines using stable content-addressed fingerprints.
    """

    @staticmethod
    def generate_fingerprint(finding: NormalizedFinding) -> str:
        """
        Generates a deterministic hash for deduplicating identical vulnerabilities across multiple scanners.
        """
        raw_key = (
            f"{finding.target.lower().strip()}|"
            f"{finding.finding_type.upper().strip()}|"
            f"{(finding.endpoint or '').lower().strip()}|"
            f"{(finding.parameter or '').lower().strip()}|"
            f"{','.join(sorted(finding.cve))}|"
            f"{','.join(sorted(finding.cwe))}"
        )
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def generate_finding_fingerprint(cls, finding: NormalizedFinding) -> str:
        """Alias for generate_fingerprint."""
        return cls.generate_fingerprint(finding)

    @classmethod
    def deduplicate_findings(cls, findings: List[NormalizedFinding]) -> List[NormalizedFinding]:
        """
        Merges duplicate findings from different engines while aggregating sources and evidence.
        """
        deduped: Dict[str, NormalizedFinding] = {}

        for f in findings:
            fp = cls.generate_fingerprint(f)
            f.fingerprint = fp

            if fp not in deduped:
                if "sources" not in f.evidence:
                    f.evidence["sources"] = [f.engine]
                deduped[fp] = f
            else:
                existing = deduped[fp]
                # Merge sources
                if f.source not in existing.source:
                    existing.source = f"{existing.source}, {f.source}"
                if "sources" not in existing.evidence:
                    existing.evidence["sources"] = [existing.engine]
                if f.engine not in existing.evidence["sources"]:
                    existing.evidence["sources"].append(f.engine)
                # Merge evidence
                if f.evidence:
                    existing.evidence.update({k: v for k, v in f.evidence.items() if k != "sources"})
                # Keep highest severity
                severity_ranks = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFORMATIONAL": 0}
                if severity_ranks.get(f.severity.upper(), 0) > severity_ranks.get(existing.severity.upper(), 0):
                    existing.severity = f.severity
                    existing.title = f.title
                    existing.description = f.description

        return list(deduped.values())


class RiskCalculationEngine:
    """
    Deterministic, explainable scoring engine separating Technical Severity from Business Asset Risk.
    """

    @staticmethod
    def calculate_scan_risk(
        findings: List[NormalizedFinding],
        discovered_services: List[Any],
        discovered_technologies: List[Any],
        threat_actors: List[Any],
        malware: List[Any]
    ) -> Dict[str, Any]:
        score = 0
        scoring_breakdown: List[str] = []

        crit_findings = [f for f in findings if f.severity.upper() == "CRITICAL"]
        high_findings = [f for f in findings if f.severity.upper() == "HIGH"]
        med_findings = [f for f in findings if f.severity.upper() == "MEDIUM"]
        low_findings = [f for f in findings if f.severity.upper() in ["LOW", "INFORMATIONAL"]]

        # 1. Critical & High Findings
        if crit_findings:
            pts = min(60, len(crit_findings) * 45)
            score += pts
            scoring_breakdown.append(f"+{pts} for {len(crit_findings)} critical security finding(s)")
        if high_findings:
            pts = min(30, len(high_findings) * 15)
            score += pts
            scoring_breakdown.append(f"+{pts} for {len(high_findings)} high severity finding(s)")
        if med_findings:
            pts = min(15, len(med_findings) * 5)
            score += pts
            scoring_breakdown.append(f"+{pts} for {len(med_findings)} medium severity finding(s)")

        # 2. Threat Actor & Active Threat Intel Matches
        if threat_actors:
            pts = min(25, len(threat_actors) * 25)
            score += pts
            scoring_breakdown.append(f"+{pts} associated with known active threat actor infrastructure")

        if malware:
            pts = min(20, len(malware) * 10)
            score += pts
            scoring_breakdown.append(f"+{pts} associated with known malware family communication patterns")

        # 3. Perimeter Surface Exposure (Open DB ports, cleartext protocols)
        exposed_db_ports = [s for s in discovered_services if getattr(s, "port", None) in [3306, 5432, 6379, 27017]]
        if exposed_db_ports:
            pts = 10
            score += pts
            scoring_breakdown.append(f"+{pts} direct public internet exposure of backend database port(s)")

        final_threat_score = min(100, max(5, score))

        if final_threat_score >= 80:
            overall_severity = "CRITICAL"
        elif final_threat_score >= 60:
            overall_severity = "HIGH"
        elif final_threat_score >= 35:
            overall_severity = "MEDIUM"
        else:
            overall_severity = "LOW"

        return {
            "threat_score": final_threat_score,
            "overall_severity": overall_severity,
            "critical_count": len(crit_findings),
            "high_count": len(high_findings) + len(threat_actors),
            "medium_count": len(med_findings) + len(malware),
            "low_count": len(low_findings),
            "scoring_breakdown": scoring_breakdown,
            "asset_risk": {
                "asset_criticality": "HIGH",
                "exposure_level": "INTERNET_FACING",
                "combined_risk_rating": overall_severity,
                "explanation": f"Score {final_threat_score}/100 calculated from {len(scoring_breakdown)} deterministic evidence factors."
            }
        }
