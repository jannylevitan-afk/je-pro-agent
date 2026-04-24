from content_engine.models.workflow_b import ContentBrief, DraftBundle


def build_draft_bundle(
    brief: ContentBrief,
    draft_text_ru: str,
    voice_register: str,
    audience_portrait: str,
    draft_text_en: str | None = None,
) -> DraftBundle:
    return DraftBundle(
        title=f"{audience_portrait} — {brief.platform_lane}",
        platform=brief.platform,
        platform_lane=brief.platform_lane,
        working_language=brief.working_language,
        publish_language=brief.publish_language,
        audience_portrait=audience_portrait,
        voice_register=voice_register,
        funnel_role=brief.funnel_role,
        draft_text_ru=draft_text_ru,
        draft_text_en=draft_text_en,
    )
