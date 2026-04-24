def route_signal(signal_summary: dict) -> str:
    relevance_score = int(signal_summary.get("relevance_score", 0))
    is_video = bool(signal_summary.get("is_video", False))
    has_trend_hook = bool(signal_summary.get("has_trend_hook", False))
    has_textual_depth = bool(signal_summary.get("has_textual_depth", False))

    if relevance_score < 6:
        return "drop"

    if is_video and has_trend_hook and has_textual_depth:
        return "both"

    if is_video and has_trend_hook:
        return "workflow_a"

    if has_textual_depth:
        return "workflow_b"

    return "drop"
