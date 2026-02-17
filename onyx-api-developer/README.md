# Onyx API Developer Skill

Expert guidance for building Onyx API integrations and bridges.

## What This Skill Does

This skill provides comprehensive knowledge and practical guidance for:

- Building API bridges to Onyx platform
- Implementing authentication and authorization
- Creating chat, search, and ingestion integrations
- Managing connectors and credentials programmatically
- Following best practices for production deployments

## Files Included

1. **skill.md** - Main skill prompt with patterns, examples, and best practices
2. **onyx-api-documentation.md** - Complete Onyx API reference documentation scraped from https://docs.onyx.app
3. **README.md** - This file

## Usage

Activate this skill when working on Onyx API integration tasks:

```
Use the onyx-api-developer skill to help me build an API bridge to Onyx
```

## What You Get

### Documentation Coverage

- **Authentication:** API keys, Bearer tokens, security best practices
- **Core Concepts:** Agents, Actions, Connectors, Documents, Chat architecture
- **API Reference:** Complete endpoint documentation for:
  - Chat API (send messages, manage sessions)
  - Agent API (list, create, update agents)
  - Search API (internal and web search)
  - Connector API (manage data sources)
  - Ingestion API (programmatic document indexing)
  - Project, User, and Admin APIs

### Code Examples

- **Rails Integration:** Service objects, models, controllers
- **Error Handling:** Custom exceptions, retry logic
- **Streaming Support:** Server-sent events for real-time chat
- **Background Jobs:** Bulk ingestion, sync operations
- **Testing:** RSpec examples with mocking and stubbing

### Best Practices

- Security and API key management
- Rate limiting and error handling
- Pagination and caching strategies
- Asynchronous processing patterns
- Production deployment considerations

## Common Use Cases

### Chat Integration

Build conversational interfaces with Onyx agents:

```ruby
service = OnyxChatService.new
result = service.ask("What are our Q4 results?", filters: { sources: ['salesforce'] })
```

### Data Ingestion

Sync external data into Onyx:

```ruby
service = OnyxIngestionService.new
service.ingest_record(tender, cc_pair_id: ENV['ONYX_CC_PAIR_ID'])
```

### Connector Management

Programmatically create and manage connectors:

```ruby
connector = OnyxConnector.create(client,
  name: 'GitHub Main Repo',
  source: 'github',
  config: { repo_owner: 'org', repo_name: 'repo' }
)
```

### Search Integration

Direct search over indexed documents:

```ruby
results = client.search('helicopter procurement', filters: { time_cutoff: 1.month.ago })
```

## Quick Reference

### Environment Setup

```bash
# .env
ONYX_API_KEY=your_api_key_here
ONYX_API_BASE_URL=https://cloud.onyx.app/api
ONYX_CC_PAIR_ID=1
```

### Client Initialization

```ruby
client = OnyxApiClient.new
# or with specific key
client = OnyxApiClient.new('your_api_key')
```

### Key Endpoints

- Chat: `POST /chat/send-chat-message`
- Agents: `GET /agents`, `POST /agents`
- Search: `POST /search/handle-search-request`
- Connectors: `GET /manage/connector`, `POST /manage/admin/connector`
- Ingestion: `POST /onyx-api/ingestion`

## Documentation Sources

All documentation was scraped from official Onyx sources on 2026-02-16:

- https://docs.onyx.app/developers/overview
- https://docs.onyx.app/developers/core_concepts
- https://docs.onyx.app/developers/guides/chat_new_guide
- https://docs.onyx.app/developers/guides/create_connector
- https://docs.onyx.app/developers/guides/index_files_ingestion_api
- API reference endpoints from https://docs.onyx.app/llms.txt

## Additional Resources

- **OpenAPI Explorer:** Available at `https://your-instance.com/api/docs`
- **Community Discord:** https://discord.gg/TDJ59cGV2X
- **Full Documentation Index:** https://docs.onyx.app/llms.txt
- **Official Docs:** https://docs.onyx.app

## Scope

This skill is available in **all** contexts (`scope: all`).

## Updates

To update this skill with the latest Onyx API documentation, re-scrape from https://docs.onyx.app and update `onyx-api-documentation.md`.

## License

This skill and documentation are provided for use with the Onyx platform. Onyx is open source - see https://github.com/onyx-dot-app/onyx for more information.
