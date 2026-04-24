from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveryScoreResult:
    score: int
    reasons: list[str]


def score_candidate(profile: dict, criteria: dict) -> DiscoveryScoreResult:
    score = 0
    reasons: list[str] = []

    bio = str(profile.get("bio", "")).lower()
    bio_keywords = [str(item).lower() for item in criteria.get("bio_keywords", [])]
    if any(keyword in bio for keyword in bio_keywords):
        score += 3
        reasons.append("bio_keyword_match")

    geo = str(profile.get("geo", "")).lower()
    allowed_geo = [str(item).lower() for item in criteria.get("geo", [])]
    if geo in allowed_geo:
        score += 2
        reasons.append("geo_match")

    profile_signals = {str(item).lower() for item in profile.get("content_signals", [])}
    allowed_signals = {str(item).lower() for item in criteria.get("content_signals", [])}
    if profile_signals & allowed_signals:
        score += 2
        reasons.append("content_signal_match")

    if profile.get("follower_range") == criteria.get("follower_range"):
        score += 1
        reasons.append("follower_range_match")

    if bool(profile.get("irrelevant", False)):
        score -= 2
        reasons.append("irrelevant_penalty")

    return DiscoveryScoreResult(score=score, reasons=reasons)


def eligible_for_queue(score_result: DiscoveryScoreResult) -> bool:
    return score_result.score >= 6
