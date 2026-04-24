from content_engine.models.workflow_b import DraftBundle


def test_linkedin_requires_ru_master_and_en_publish_version() -> None:
    draft = DraftBundle(
        title="AILLA positioning",
        platform="linkedin",
        platform_lane="linkedin_b2b",
        working_language="ru",
        publish_language="en",
        audience_portrait="developer_investor",
        voice_register="register_3",
        funnel_role="authority",
        draft_text_ru="Русский мастер-текст",
        draft_text_en="English publish version",
    )

    assert draft.publish_language == "en"
    assert draft.draft_text_ru
    assert draft.draft_text_en


def test_instagram_defaults_to_russian_publish_language() -> None:
    draft = DraftBundle(
        title="Morning on site",
        platform="instagram",
        platform_lane="instagram_lifestyle",
        working_language="ru",
        publish_language="ru",
        audience_portrait="woman_dreamer",
        voice_register="register_7",
        funnel_role="affinity",
        draft_text_ru="Русский мастер-текст",
        draft_text_en=None,
    )

    assert draft.publish_language == "ru"
