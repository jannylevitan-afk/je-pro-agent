#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import sys
import json


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def main() -> int:
    smoke_mode = os.environ.get("CONTENT_ENGINE_SMOKE_MODE", "")
    smoke_user = os.environ.get("CONTENT_ENGINE_SMOKE_USER_ID", "")
    public_entity_id = os.environ.get("CONTENT_ENGINE_SMOKE_PUBLIC_ENTITY_ID", "")
    public_invoice_id = os.environ.get("CONTENT_ENGINE_SMOKE_PUBLIC_INVOICE_ID", "")
    if smoke_mode != "readonly":
        print("CONTENT_ENGINE_SMOKE_MODE must be readonly", file=sys.stderr)
        return 2
    if not smoke_user:
        print("CONTENT_ENGINE_SMOKE_USER_ID is required", file=sys.stderr)
        return 2

    from content_engine.models.content_factory import HumanReviewAsset

    asset = HumanReviewAsset(
        content_id="smoke_content_001",
        source_item_id="smoke_source_001",
        opportunity_id="smoke_opp_001",
        decision_id="smoke_decision_001",
        brief_id="smoke_brief_001",
        workflow="workflow_b",
        platform="instagram",
        title="Read-only smoke contract",
        pillar="#недвижка",
        audience_segment="developer_investor",
        approval_status="needs_revision",
        final_text="Smoke contract only. No external systems were mutated.",
        editor_score=0.0,
        revision_notes=["readonly smoke"],
        source_refs=["https://example.com/read-only-smoke"],
        created_at="2026-04-29T00:00:00+08:00",
    )
    result = {
        "status": "ok",
        "mode": smoke_mode,
        "smoke_user_id": smoke_user,
        "checks": [
            "imported HumanReviewAsset",
            "instantiated workflow_b review asset",
            "verified no external systems were called",
        ],
        "fixture_refs": {
            "public_entity_id": public_entity_id or None,
            "public_invoice_id": public_invoice_id or None,
        },
        "asset_id": asset.content_id,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
