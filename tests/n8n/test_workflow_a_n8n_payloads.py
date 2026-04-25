from content_engine.models.workflow_a import VideoScript
from content_engine.n8n.payloads import (
    build_video_filming_notification,
    build_video_script_envelope,
)


def make_script() -> VideoScript:
    return VideoScript(
        script_id="scr_hook_001_1",
        source_item_id="itm_vid_001",
        title="Boutique Hotels signal for developer_investor",
        platform="instagram",
        hook_text="What looks cheap first is often the most expensive later.",
        script_text="Hook\nLesson\nSave this for the next deal review.",
        cta="Save this for the next deal review.",
        filming_priority=1,
        status="scripted",
    )


def test_build_video_script_envelope_sets_route_and_workflow(video_hook) -> None:
    script = make_script()
    envelope = build_video_script_envelope(script, video_hook)

    assert envelope["workflow"] == "video_pipeline"
    assert envelope["route"] == "script_ready"
    assert envelope["script"]["script_id"] == "scr_hook_001_1"
    assert envelope["hook"]["hook_type"] == "market_warning"
    assert envelope["hook"]["score"] == 8


def test_build_video_filming_notification_includes_priority(video_hook) -> None:
    script = make_script()
    envelope = build_video_script_envelope(script, video_hook)
    notification = build_video_filming_notification(envelope)

    assert notification["channel"] == "telegram"
    assert notification["route"] == "script_ready"
    assert "priority 1" in notification["message"]
    assert notification["script_id"] == "scr_hook_001_1"
