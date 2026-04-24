DRAFTS_DB_SCHEMA = {
    "Draft ID": "rich_text",
    "Title": "title",
    "Draft text RU": "rich_text",
    "Draft text EN": "rich_text",
    "Platform": "select",
    "Platform lane": "select",
    "Language mode": "select",
    "Audience portrait": "select",
    "Voice register": "select",
    "Funnel role": "select",
    "Version": "number",
    "Working language": "select",
    "Publish language": "select",
    "Workflow stage": "select",
    "Review decision": "select",
    "Review Notes": "rich_text",
    "Parent draft": "rich_text",
    "Review requested at": "date",
    "Approval decided at": "date",
    "AI edited": "checkbox",
    "7-point test passed": "checkbox",
    "Factual safety": "select",
    "Linked brief": "rich_text",
    "Linked calendar": "rich_text",
    "Archived": "checkbox",
}

BRIEFS_DB_SCHEMA = {
    "Brief ID": "rich_text",
    "Title": "title",
    "Audience portrait": "select",
    "Platform lane": "select",
    "Language mode": "select",
    "Funnel role": "select",
    "Workflow stage": "select",
    "Review decision": "select",
    "Linked draft": "rich_text",
    "Revision requested at": "date",
    "Review notes": "rich_text",
    "Source rigor": "select",
    "Reference sources": "rich_text",
}

CONTENT_CALENDAR_SCHEMA = {
    "Platform": "select",
    "Platform lane": "select",
    "Language mode": "select",
    "Working language": "select",
    "Publish language": "select",
    "Audience portrait": "select",
    "Voice register used": "select",
    "Pillar": "select",
    "Funnel role": "select",
    "Hook": "rich_text",
    "Final text RU": "rich_text",
    "Final text EN": "rich_text",
    "Source draft": "rich_text",
    "Publish date target": "date",
    "Approval status": "select",
    "Approval decided at": "date",
    "Repurpose status": "select",
}

DISCOVERY_QUEUE_SCHEMA = {
    "Handle": "title",
    "Platform": "select",
    "Segment": "select",
    "Score": "number",
    "Why relevant": "rich_text",
    "Approved": "select",
    "Added to monitoring": "checkbox",
}

MONITORING_RUN_SCHEMA = {
    "Run ID": "title",
    "Connector": "select",
    "Source name": "rich_text",
    "Started at": "date",
    "Finished at": "date",
    "Fetched count": "number",
    "Failed count": "number",
    "Last success at": "date",
    "Error type": "select",
    "Retry count": "number",
    "Staleness hours": "number",
    "Run status": "select",
}

SOURCES_DB_SCHEMA = {
    "Title": "title",
    "Platform": "select",
    "Raw text": "rich_text",
    "External item ID": "rich_text",
    "Dedupe key": "rich_text",
    "Content hash": "rich_text",
    "Ingestion status": "select",
}

INSIGHTS_DB_SCHEMA = {
    "Topic": "rich_text",
    "Angle": "rich_text",
    "Audience portrait": "select",
    "Narrative type": "select",
    "Emotional trigger": "rich_text",
    "Reuse score": "number",
}

IDEAS_DB_SCHEMA = {
    "Title": "title",
    "Platform": "select",
    "Platform lane": "select",
    "Language mode": "select",
    "Funnel role": "select",
    "Audience portrait": "select",
    "Emotional hook": "rich_text",
    "Desired reaction": "rich_text",
    "Gate passed": "checkbox",
    "Status": "select",
}

ORCHESTRATION_EVENT_SCHEMA = {
    "Event name": "select",
    "Entity type": "select",
    "Entity ID": "rich_text",
    "Status": "select",
    "Triggered at": "date",
    "Draft ID": "rich_text",
    "Brief ID": "rich_text",
    "Calendar item ID": "rich_text",
    "Payload ref": "rich_text",
}

SCRIPTS_QUEUE_SCHEMA = {
    "Title": "title",
    "Hook": "rich_text",
    "Platform": "select",
    "Script text": "rich_text",
    "Filming priority": "number",
    "Status": "select",
}

FILMING_CARDS_SCHEMA = {
    "Linked script": "rich_text",
    "Shoot date": "date",
    "Filmed": "checkbox",
    "Raw file link": "url",
}

VIDEO_PUBLISH_CALENDAR_SCHEMA = {
    "Platform": "select",
    "Publish date": "date",
    "Caption": "rich_text",
    "Status": "select",
}

VIDEO_PERFORMANCE_SCHEMA = {
    "Linked video": "relation",
    "Views": "number",
    "Saves": "number",
    "Hook type": "select",
    "Performance tier": "select",
    "Fed back to RA": "checkbox",
}

CONTENT_PERFORMANCE_SCHEMA = {
    "Linked content item": "rich_text",
    "Platform": "select",
    "Reach": "number",
    "Impressions": "number",
    "Saves": "number",
    "Shares": "number",
    "Comments": "number",
    "Profile visits": "number",
    "DMs received": "number",
    "Inquiry type": "select",
    "Likes": "number",
    "Engagement rate": "number",
    "CTR": "number",
    "Attribution model": "select",
    "Deal influenced": "checkbox",
    "Performance tier": "select",
}

RESEARCH_FEEDBACK_SIGNAL_SCHEMA = {
    "Signal scope": "select",
    "Dimension value": "rich_text",
    "Signal type": "select",
    "Performance tier": "select",
    "Score": "number",
    "Reason": "rich_text",
    "Applied": "checkbox",
}
