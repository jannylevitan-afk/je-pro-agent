from content_engine.knowledge.kmd import MarkdownKnowledgeStore


def test_markdown_knowledge_store_writes_workflow_source_material(tmp_path, source_item) -> None:
    store = MarkdownKnowledgeStore(tmp_path)

    path = store.write_source_material(source_item, workflow="workflow_b")

    assert path == tmp_path / "workflow_b" / "developer_investor" / "boutique_hotels" / "itm_001.kmd.md"
    assert path.exists()
    body = path.read_text(encoding="utf-8")
    assert "workflow: workflow_b" in body
    assert "audience_segment: developer_investor" in body
    assert "content_theme: boutique_hotels" in body
    assert source_item.source_url in body
    assert "## Search Dependencies" in body
    assert "## Source Note" in body
    assert "## Writer Context" in body


def test_markdown_knowledge_store_includes_video_intake_for_workflow_a(tmp_path, video_source_item) -> None:
    store = MarkdownKnowledgeStore(tmp_path)

    path = store.write_source_material(video_source_item, workflow="workflow_a")

    body = path.read_text(encoding="utf-8")
    assert "## Video Intake" in body
    assert "title: What cheap villas hide" in body
    assert "spoken transcript: Cheap villas are never actually cheap" in body
    assert "first 3 seconds: A villa price flashes on screen" in body
    assert "source hook: Cheap villas are never actually cheap." in body
    assert "visual device: price tag cut to legal documents" in body
    assert "hook pattern: cheap surface -> hidden structural cost" in body
    assert "repeatable formula: Show the attractive surface" in body
    assert "public comments / reactions: I wish someone told me this before my first viewing." in body
    assert "views=5200" in body
