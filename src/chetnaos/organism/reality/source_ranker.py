"""
Source Ranker — Assigns trust scores to information sources.
"""

SOURCE_TRUST = {
    "peer_reviewed": 0.95,
    "official_gov":  0.90,
    "news_major":    0.70,
    "wikipedia":     0.65,
    "blog":          0.40,
    "social_media":  0.20,
    "llm_generated": 0.55,
    "unknown":       0.30,
}


class SourceRanker:
    def rank(self, source_type: str) -> dict:
        score = SOURCE_TRUST.get(source_type, SOURCE_TRUST["unknown"])
        return {
            "source": source_type,
            "trust_score": score,
            "reliable": score >= 0.6,
        }

    def rank_output(self, text: str) -> dict:
        """Auto-detect source type from text markers."""
        t = text.lower()
        if any(k in t for k in ["published in", "journal", "doi:", "arxiv"]):
            return self.rank("peer_reviewed")
        if any(k in t for k in ["wikipedia", "wiki"]):
            return self.rank("wikipedia")
        if any(k in t for k in ["according to", "reports say", "news"]):
            return self.rank("news_major")
        return self.rank("llm_generated")
