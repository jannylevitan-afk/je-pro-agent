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
