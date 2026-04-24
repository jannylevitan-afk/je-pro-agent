from content_engine.models.workflow_a import FilmingCard, VideoPublishItem, VideoScript
from content_engine.notion.payloads import (
    build_filming_card_properties,
    build_script_properties,
    build_video_publish_properties,
)
from content_engine.notion.sync import (
    create_filming_card,
    create_script,
    create_video_publish_item,
    upsert_source,
)
from tests.notion.conftest import StubNotionClient, first_text


def make_script() -> VideoScript:
    return VideoScript(
        script_id="scr_001",
        source_item_id="itm_vid_001",
        title="What cheap villas hide",
        platform="instagram",
        hook_text="What looks cheap first is often the most expensive later.",
        script_text="Hook\nPoint 1\nPoint 2\nCTA",
        cta="Save this if you're buying in Bali.",
        filming_priority=1,
        status="scripted",
    )


def make_filming_card() -> FilmingCard:
    return FilmingCard(
        card_id="film_scr_001",
        linked_script_id="scr_001",
        filming_priority=1,
        shoot_date="2026-04-25",
        filmed=False,
        raw_file_link=None,
    )


def make_publish_item() -> VideoPublishItem:
    return VideoPublishItem(
        publish_item_id="pub_scr_001",
        linked_script_id="scr_001",
        platform="instagram",
        caption="What looks cheap first is often the most expensive later.",
        publish_date=None,
        status="ready",
    )


# --- payload builder tests ---------------------------------------------------

def test_build_script_properties_maps_all_schema_fields() -> None:
    script = make_script()
    props = build_script_properties(script)

    assert first_text(props["Hook"]) == "What looks cheap first is often the most expensive later."
    assert props["Platform"] == {"select": {"name": "instagram"}}
    assert props["Filming priority"] == {"number": 1}
    assert props["Status"] == {"select": {"name": "scripted"}}


def test_build_filming_card_properties_maps_relation_and_flags() -> None:
    card = make_filming_card()
    props = build_filming_card_properties(card)

    assert props["Linked script"] == {"relation": [{"id": "scr_001"}]}
    assert props["Shoot date"] == {"date": {"start": "2026-04-25"}}
    assert props["Filmed"] == {"checkbox": False}
    assert props["Raw file link"] == {"url": None}


def test_build_video_publish_properties_ready_item() -> None:
    item = make_publish_item()
    props = build_video_publish_properties(item)

    assert props["Platform"] == {"select": {"name": "instagram"}}
    assert props["Publish date"] == {"date": None}
    assert props["Status"] == {"select": {"name": "ready"}}


# --- sync function tests -----------------------------------------------------

def test_create_script_calls_create_database_page() -> None:
    client = StubNotionClient(create_results=[{"id": "page_scr_001"}])
    script = make_script()

    response = create_script(client, "db_scripts", script)

    assert response["id"] == "page_scr_001"
    assert client.create_calls[0][0] == "db_scripts"
    assert client.query_calls == []


def test_create_filming_card_creates_with_linked_script() -> None:
    client = StubNotionClient(create_results=[{"id": "page_film_001"}])
    card = make_filming_card()

    response = create_filming_card(client, "db_filming", card)

    assert response["id"] == "page_film_001"
    sent_props = client.create_calls[0][1]
    assert sent_props["Linked script"] == {"relation": [{"id": "scr_001"}]}


def test_create_video_publish_item_creates_page() -> None:
    client = StubNotionClient(create_results=[{"id": "page_pub_001"}])
    item = make_publish_item()

    response = create_video_publish_item(client, "db_video_calendar", item)

    assert response["id"] == "page_pub_001"


def test_upsert_source_creates_when_missing(source_item) -> None:
    client = StubNotionClient(
        query_results=[{"results": []}],
        create_results=[{"id": "page_src_001"}],
    )

    response = upsert_source(client, "db_sources", source_item)

    assert response["id"] == "page_src_001"
    assert client.query_calls[0][1]["filter"]["property"] == "Dedupe key"
    assert client.query_calls[0][1]["filter"]["rich_text"]["equals"] == source_item.dedupe_key


def test_upsert_source_updates_existing(source_item) -> None:
    client = StubNotionClient(
        query_results=[{"results": [{"id": "existing_page"}]}],
        update_results=[{"id": "existing_page"}],
    )

    response = upsert_source(client, "db_sources", source_item)

    assert response["id"] == "existing_page"
    assert client.create_calls == []
