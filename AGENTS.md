# Je Pro Agent Operating Rules

Always use the connected MCP stack for Research Agent work when it improves fidelity:

- `exa` for source discovery, competitor expansion, founder search, and quick web research
- `firecrawl` for structured scraping, clean page extraction, and search + scrape flows
- `apify` for actor-backed collection when platform-specific extraction is needed
- `playwright` for rendered public pages, interaction-heavy pages, and browser fallback

Research Agent operating order:

1. Run compliance checks first
2. Prefer public feeds and metadata before heavier extraction
3. Require evidence fields before Workflow A or Workflow B handoff:
   - source URL
   - timestamp
   - raw excerpt
   - confidence score
4. Route signals explicitly:
   - video refs -> Workflow A
   - market/founder/text insight -> Workflow B
   - strong video plus textual depth -> both
   - weak or unsupported signal -> drop

Environment notes:

- `FIRECRAWL_API_KEY` is required for the `firecrawl` MCP server
- `APIFY_TOKEN` is required for the `apify` MCP server
- `exa` is configured without a token by default
- `playwright` runs locally through `npx @playwright/mcp@latest`
