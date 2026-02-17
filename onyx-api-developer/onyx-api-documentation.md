# Onyx API Developer Documentation

## Overview

Onyx is an Open Source AI Platform for Work that provides REST-based APIs accessible at `https://cloud.onyx.app/api` or self-hosted instances. Nearly all Onyx features are available through these endpoints, which use JSON for requests and responses.

**Versioning:** The system follows SemVer 2.0.0, where major version changes indicate breaking modifications.

**Base URL:** `https://cloud.onyx.app/api` (or `https://your-self-hosted-onyx.com/api`)

**Complete documentation index:** https://docs.onyx.app/llms.txt

---

## Authentication

### API Key Types

Onyx offers three API key types, each functioning as a distinct user for activity tracking and session privacy:

1. **Admin API Keys**
   - Full system access including administrative endpoints
   - Suitable for user management, data analytics, and complete feature access
   - ⚠️ **Warning:** Unrestricted access requires careful handling

2. **Basic API Keys** *(Recommended for most applications)*
   - Access to Search, Chat, Agents, and Actions endpoints
   - Suitable for most application development scenarios

3. **Limited API Keys**
   - Read-only Agent access
   - Chat message posting capability but no history access
   - For restricted environments requiring minimal permissions

### Authentication Methods

- **API Keys:** Generated from the Onyx Admin Console
- **Personal Access Tokens (PATs):** Created through User Settings (authenticate with individual user permissions)
- **Coming Soon:** User-scoped tokens tied to specific user permissions

### Authentication Header Format

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

---

## Core Concepts

### Agents (formerly Personas)

Agents are AI assistants with custom instructions, Actions, and data access that extend the base LLM's capabilities. The terms "Personas," "Assistants," and "Agents" are interchangeable in Onyx.

**Built-in Agents:**
- Search Agent (id: 0)
- General Agent (id: -1)
- Paraphrase Agent (id: -2)
- Art Agent (id: -3)

### Actions (Tools)

Actions enable agents to interact with external systems. Built-in actions include:
- **Internal Search:** Search through your organization's indexed documents
- **Web Search:** Real-time internet searching via Google, Serper, Exa, or Firecrawl
- **Code Interpreter:** Python execution and data analysis
- **Image Generation:** Text-to-image via OpenAI or Azure

Custom actions support REST APIs, database operations, workflow automation, and file manipulation through **OpenAPI specifications** or **Model Context Protocol (MCP)**.

### Connectors

Connectors define indexed data sources through configurations specifying:
- Document source type (40+ integrations supported)
- Input type: `load_state` (single), `poll` (continuous), `event` (event-based), or `slim_retrieval` (permission sync)
- Refresh and pruning frequencies
- Optional indexing start date

**Supported sources:** Slack, GitHub, Confluence, Notion, Salesforce, Jira, cloud storage (S3, Google Drive, SharePoint), and many more.

### Credentials

Authenticate access via API keys, OAuth tokens, personal access tokens (PATs), or service account credentials.

### ConnectorCredentialPairs (CC-pairs)

CC-pairs combine connectors with credentials for active synchronization. They manage access control, monitoring, and configuration within the Admin panel.

### Documents

**DocumentBase** represents the core document model with:
- Unique identifier
- Content sections (TextSection with text/links; ImageSection with file IDs)
- Document source and semantic identifier
- Metadata tags, ownership information, and update timestamps
- Chunk count for processing

**Access Types:**
- `PUBLIC`: All users
- `PRIVATE`: Creator and specified groups only
- `SYNC`: Permission synchronization with source systems

### Chat Architecture

The chat system uses **packet-based streaming** with sequential indexing. Core packet types include:

- **Message packets:** `MessageStart`, `MessageDelta`
- **Control packets:** `OverallStop`, `SectionEnd`
- **Specialized packets:** `ReasoningStart/Delta`, `SearchToolStart/Delta`, `ImageGenerationTool`, `CustomToolStart/Delta`, `CitationStart/Delta`

---

## API Reference

### Chat Endpoints

#### Send Chat Message

**Endpoint:** `POST /chat/send-chat-message`

**Description:** Send a message to Onyx programmatically. Supports both streaming and complete responses.

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | Yes | — | The chat message content |
| `stream` | boolean | No | true | Enable SSE streaming or receive complete response |
| `include_citations` | boolean | No | true | Include source citations in response |
| `llm_override` | LLMOverride | No | null | Override model provider, version, or temperature |
| `allowed_tool_ids` | integer[] | No | null | Restrict which tools the LLM can use |
| `forced_tool_id` | integer | No | null | Force use of a specific tool |
| `file_descriptors` | FileDescriptor[] | No | [] | Attach files (image, document, plain_text, csv) |
| `internal_search_filters` | BaseFilters | No | null | Filter search by source type, document set, time, tags |
| `deep_research` | boolean | No | false | Enable deep research mode (⚠️ high token consumption) |
| `parent_message_id` | integer | No | -1 | Reference a previous message in conversation |
| `chat_session_id` | UUID | No | null | Specify existing chat session |
| `chat_session_info` | ChatSessionCreationRequest | No | null | Create new session with persona and project |
| `origin` | MessageOrigin | No | unset | Track message origin (webapp, api, slackbot, etc.) |

**Response:**
- `stream=true`: `StreamingResponse` with server-sent events
- `stream=false`: `ChatFullResponse` with complete message data including:
  - `answer` and `answer_citationless`
  - `pre_answer_reasoning`
  - `tool_calls` list
  - `top_documents` and `citation_info`
  - `message_id` and `chat_session_id`

**Example (Python):**
```python
import requests

API_KEY = "your_api_key"
API_BASE_URL = "https://cloud.onyx.app/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{API_BASE_URL}/chat/send-chat-message",
    headers=headers,
    json={
        "message": "What is Onyx?",
        "stream": false,
        "include_citations": true
    }
)

print(response.json()["answer"])
```

**Example (Bash):**
```bash
curl -X POST "${API_BASE_URL}/chat/send-chat-message" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Onyx?",
    "stream": false
  }'
```

#### Other Chat Endpoints

- `POST /chat/create-chat-session` - Create a new chat session
- `GET /chat/get-user-chat-sessions` - Get user's chat sessions
- `GET /chat/get-chat-session` - Get specific chat session
- `DELETE /chat/chat-session/{session_id}` - Delete chat session by ID
- `DELETE /chat/delete-all-chat-sessions` - Delete all chat sessions
- `GET /chat/file/{file_id}` - Fetch chat file
- `POST /chat/search-chats` - Search for chat sessions
- `POST /chat/seed-chat` - Seed a chat
- `POST /chat/stop-chat-session` - Stop a chat session

---

### Agent Endpoints

#### List Agents (Paginated)

**Endpoint:** `GET /agents`

**Description:** Paginated endpoint for listing agents available to the user.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page_num` | integer | No | 0 | Page number (0-indexed) |
| `page_size` | integer | No | 10 | Items per page (1-1000 max) |
| `include_deleted` | boolean | No | false | Include removed personas |
| `get_editable` | boolean | No | false | Return only editable personas |
| `include_default` | boolean | No | true | Includes builtin/default personas |

**Response (200):**
```json
{
  "items": [MinimalPersonaSnapshot],
  "total_items": integer
}
```

Each persona includes tools, document sets, starter messages, labels, and owner information.

#### Other Agent Endpoints

- `POST /agents` - Create Agent
- `GET /agents/{agent_id}` - Get Agent
- `PATCH /agents/{agent_id}` - Update Agent
- `DELETE /agents/{agent_id}` - Delete Agent
- `POST /agents/{agent_id}/undelete` - Undelete Agent
- `GET /admin/agents` - List Agents Admin (all agents)
- `GET /admin/agents/paginated` - Get Agents Admin Paginated

---

### Search Endpoints

#### Handle Search Request

**Endpoint:** `POST /search/handle-search-request`

**Description:** Execute a search across indexed documents.

#### Execute Web Search

**Endpoint:** `POST /search/web-search`

**Description:** Perform a web search and immediately fetch content for the returned URLs. Use this when you want both snippets and page contents from one call.

#### Execute Web Search Lite

**Endpoint:** `POST /search/web-search-lite`

**Description:** Lightweight search-only endpoint. Returns search snippets and URLs without fetching page contents. Pair with `/open-urls` if you need to fetch content later.

#### Execute Open URLs

**Endpoint:** `POST /search/open-urls`

**Description:** Fetch content for specific URLs using the configured content provider. Intended to complement `/search-lite` when you need content for a subset of URLs.

---

### Connector Endpoints

#### List Connectors

**Endpoint:** `GET /manage/connector`

**Description:** Retrieves all configured connectors in the Onyx system.

**Response (200):** Returns an array of connector objects (ConnectorSnapshot)

**ConnectorSnapshot Structure:**

```json
{
  "name": "string",
  "source": "DocumentSource",
  "input_type": "poll|load_state|event|slim_retrieval",
  "connector_specific_config": {},
  "refresh_freq": 3600,
  "prune_freq": 86400,
  "indexing_start": "2024-01-01T00:00:00Z",
  "id": 1,
  "credential_ids": [1, 2],
  "time_created": "2024-01-01T00:00:00Z",
  "time_updated": "2024-01-15T00:00:00Z"
}
```

#### Create Connector

**Endpoint:** `POST /manage/admin/connector`

**Description:** Create a new connector.

**Request Body Example (Jira):**
```json
{
  "name": "Jira Project XYZ",
  "source": "jira",
  "input_type": "poll",
  "access_type": "PUBLIC",
  "connector_specific_config": {
    "jira_base_url": "https://your-company.atlassian.net",
    "project_key": "XYZ",
    "comment_email_blacklist": ["legal@company.com"]
  },
  "refresh_freq": 3600,
  "prune_freq": 86400
}
```

#### Other Connector Endpoints

- `GET /manage/connector/{connector_id}` - Get Connector By ID
- `DELETE /manage/admin/connector/{connector_id}` - Delete Connector By ID
- `GET /manage/connector/indexing-status` - Get Connector Indexing Status
- `GET /manage/connector/{connector_id}/status` - Get Connector Status
- `POST /manage/admin/connector/run-once` - Trigger indexing on cc_pairs
- `PUT /manage/admin/connector/{connector_id}/credential/{credential_id}` - Associate Credential To Connector
- `DELETE /manage/admin/connector/{connector_id}/credential/{credential_id}` - Dissociate Credential From Connector

#### Credential Endpoints

- `GET /manage/credential` - List Credentials
- `GET /manage/admin/credential` - List Credentials Admin (all public credentials)
- `POST /manage/credential` - Create Credential From Model
- `GET /manage/credential/{credential_id}` - Get Credential By ID
- `PATCH /manage/credential/{credential_id}` - Update Credential From Model
- `DELETE /manage/credential/{credential_id}` - Delete Credential By ID
- `DELETE /manage/admin/credential/{credential_id}` - Delete Credential By ID Admin
- `DELETE /manage/admin/credential/{credential_id}/force` - Force Delete Credential

---

### Ingestion API

#### Upsert Ingestion Document

**Endpoint:** `POST /onyx-api/ingestion`

**Description:** Programmatically index documents into Onyx. Designed for scenarios where built-in connectors are unavailable or supplemental data is needed.

**Use Cases:**
- Adding content from systems lacking native connectors
- Enriching existing connector data with supplementary materials
- Modifying documents when source system updates aren't possible
- Embedding document indexing into existing data workflows

**Minimum Request:**
```json
{
  "document": {
    "id": "unique-doc-id",
    "semantic_identifier": "Display Name",
    "sections": [
      {
        "text": "Document content here",
        "link": "https://optional-url.com"
      }
    ],
    "source": "custom_source"
  },
  "cc_pair_id": 1
}
```

**Full Request Structure:**
```json
{
  "document": {
    "id": "unique-doc-id",
    "semantic_identifier": "Display Name",
    "title": "Search-specific title",
    "sections": [
      {
        "text": "Document content",
        "link": "https://optional-url.com"
      }
    ],
    "source": "custom_source",
    "metadata": {
      "custom_key": "custom_value"
    },
    "doc_updated_at": "2024-01-15T10:30:00Z",
    "primary_owners": [
      {
        "email": "owner@company.com"
      }
    ],
    "secondary_owners": []
  },
  "cc_pair_id": 1
}
```

**Key Notes:**
- Set `cc_pair_id` to associate documents with existing connectors for Admin Panel visibility
- The API returns success upon acceptance
- Actual indexing proceeds asynchronously
- Successful responses don't guarantee completion

#### Other Ingestion Endpoints

- `GET /onyx-api/ingestion` - Get Ingestion Docs
- `DELETE /onyx-api/ingestion/{doc_id}` - Delete Ingestion Doc

---

### Project Endpoints

Projects allow organizing files and chat sessions.

- `GET /projects` - Get Projects
- `POST /projects` - Create Project
- `GET /projects/{project_id}` - Get Project
- `GET /projects/{project_id}/details` - Get Project Details
- `PATCH /projects/{project_id}` - Update Project
- `DELETE /projects/{project_id}` - Delete Project
- `GET /projects/{project_id}/files` - Get Files In Project
- `POST /projects/files/upload` - Upload User Files
- `GET /projects/files/{file_id}` - Get User File
- `DELETE /projects/files/{file_id}` - Delete User File
- `POST /projects/{project_id}/files/{file_id}/link` - Link User File To Project
- `DELETE /projects/{project_id}/files/{file_id}/unlink` - Unlink User File From Project
- `GET /projects/files/statuses` - Get User File Statuses
- `GET /projects/instructions/{project_id}` - Get Project Instructions
- `PUT /projects/instructions/{project_id}` - Upsert Project Instructions
- `GET /chat-session/{chat_session_id}/project-files` - Get Chat Session Project Files

---

### Actions (Tools) Endpoints

- `GET /tools` - List Tools
- `GET /tools/openapi` - List OpenAPI Tools
- `POST /tools/custom` - Create Custom Tool
- `GET /tools/custom/{tool_id}` - Get Custom Tool
- `PATCH /tools/custom/{tool_id}` - Update Custom Tool
- `DELETE /tools/custom/{tool_id}` - Delete Custom Tool
- `POST /tools/validate` - Validate Tool

---

### User Management Endpoints

- `GET /users` - List All Users
- `GET /users/basic-info` - List All Users Basic Info
- `GET /users/accepted` - List Accepted Users
- `GET /users/invited` - List Invited Users
- `POST /users/invite` - Bulk Invite Users
- `DELETE /users/invited/{user_email}` - Remove Invited User
- `PATCH /users/{user_id}/activate` - Activate User
- `PATCH /users/{user_id}/deactivate` - Deactivate User
- `DELETE /users/{user_id}` - Delete User
- `GET /users/me/role` - Get User Role
- `PATCH /users/{user_id}/role` - Set User Role
- `GET /auth/type` - Get Auth Type
- `GET /auth/verify` - Verify User Logged In

---

### Miscellaneous Endpoints

- `GET /health` - Healthcheck
- `GET /version` - Get Backend Version
- `GET /versions` - Get Latest App Version Tags (Docker images)
- `GET /token-limit-settings` - Get Global Token Limit Settings
- `POST /token-limit-settings` - Create Global Token Limit Settings
- `PATCH /token-limit-settings` - Update Token Limit Settings
- `DELETE /token-limit-settings/{settings_id}` - Delete Token Limit Settings

---

## OpenAPI Explorer

Your Onyx instance provides an interactive API explorer at:

**URL:** `https://your-instance.onyx.app/api/docs`

This provides complete endpoint reference with request/response schemas and the ability to test API calls directly.

---

## Best Practices

### Chat API
- Use `file_descriptors` to attach relevant documents
- Apply `internal_search_filters` to focus Agent searches
- Enable `include_citations` for source transparency
- Exercise caution with `deep_research` due to token costs
- Use `llm_override` to customize model behavior per request

### Connector Management
- Always associate credentials to connectors after creation
- Set appropriate `refresh_freq` and `prune_freq` based on data volatility
- Use `access_type: PUBLIC` for organization-wide data
- Monitor indexing status via status endpoints

### Ingestion API
- Always set `cc_pair_id` for Admin Panel visibility
- Use unique, stable document IDs
- Include meaningful `semantic_identifier` for user-friendly display
- Provide `doc_updated_at` for version tracking
- Handle asynchronous processing (API returns success before indexing completes)

### Authentication & Security
- Use Basic API Keys for most application development
- Reserve Admin API Keys for administrative operations
- Rotate API keys regularly
- Never commit API keys to version control
- Use environment variables for API key storage

---

## Rate Limiting

Rate limiting is enforced at three levels:
- **User level:** Per-user request limits
- **Group level:** Shared limits across user groups
- **Global level:** Instance-wide limits

Monitor rate limit headers in responses and implement exponential backoff for retries.

---

## Error Handling

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid or missing API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error (detailed field validation messages)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

**Example Error Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Migration Notes

**Deprecated Endpoints:**
- `/chat/send-message` - Migrate to `/chat/send-chat-message` by February 1st, 2026
- `/chat/send-message-simple-api` - Migrate to `/chat/send-chat-message` by February 1st, 2026

---

## Community & Support

- **Discord:** https://discord.gg/TDJ59cGV2X
- **Documentation:** https://docs.onyx.app
- **OpenAPI Spec:** Available at `/api/docs` on your instance

---

## Quick Start Examples

### Python: Send a Chat Message

```python
import requests

API_KEY = "your_api_key"
API_BASE_URL = "https://cloud.onyx.app/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Simple message
response = requests.post(
    f"{API_BASE_URL}/chat/send-chat-message",
    headers=headers,
    json={
        "message": "Summarize our recent sales data",
        "stream": False
    }
)

print(response.json()["answer"])

# With filters and citations
response = requests.post(
    f"{API_BASE_URL}/chat/send-chat-message",
    headers=headers,
    json={
        "message": "What are the latest updates?",
        "stream": False,
        "include_citations": True,
        "internal_search_filters": {
            "source_type": ["slack", "notion"],
            "time_cutoff": "2024-01-01T00:00:00Z"
        }
    }
)

print(response.json()["answer"])
for citation in response.json()["citation_info"]:
    print(f"Source: {citation}")
```

### Python: Create a Connector

```python
import requests

API_KEY = "your_admin_api_key"
API_BASE_URL = "https://cloud.onyx.app/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create connector
connector_response = requests.post(
    f"{API_BASE_URL}/manage/admin/connector",
    headers=headers,
    json={
        "name": "GitHub Main Repo",
        "source": "github",
        "input_type": "poll",
        "access_type": "PUBLIC",
        "connector_specific_config": {
            "repo_owner": "your-org",
            "repo_name": "main-repo"
        },
        "refresh_freq": 3600,  # 1 hour
        "prune_freq": 86400    # 1 day
    }
)

connector_id = connector_response.json()["id"]

# Associate credential (assuming you have credential_id)
credential_id = 1  # Get this from /manage/credential endpoint

requests.put(
    f"{API_BASE_URL}/manage/admin/connector/{connector_id}/credential/{credential_id}",
    headers=headers
)

print(f"Connector {connector_id} created and associated with credential {credential_id}")
```

### Python: Ingest Custom Document

```python
import requests
from datetime import datetime

API_KEY = "your_api_key"
API_BASE_URL = "https://cloud.onyx.app/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Ingest document
response = requests.post(
    f"{API_BASE_URL}/onyx-api/ingestion",
    headers=headers,
    json={
        "document": {
            "id": "custom-doc-001",
            "semantic_identifier": "Q4 2024 Sales Report",
            "title": "Q4 2024 Sales Report - Executive Summary",
            "sections": [
                {
                    "text": "Executive Summary: Q4 2024 exceeded projections with 25% growth...",
                    "link": "https://internal.company.com/reports/q4-2024"
                }
            ],
            "source": "internal_reports",
            "metadata": {
                "department": "sales",
                "quarter": "Q4",
                "year": "2024",
                "classification": "internal"
            },
            "doc_updated_at": datetime.now().isoformat(),
            "primary_owners": [
                {"email": "sales-director@company.com"}
            ]
        },
        "cc_pair_id": 1  # Associate with existing connector
    }
)

print("Document ingested successfully:", response.json())
```

### Bash: List All Agents

```bash
#!/bin/bash

API_KEY="your_api_key"
API_BASE_URL="https://cloud.onyx.app/api"

curl -X GET "${API_BASE_URL}/agents?page_num=0&page_size=20&include_default=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"
```

---

## Document Source Types (DocumentSource Enum)

Supported connector sources include:

- `web` - Web pages
- `file` - Local files
- `slack` - Slack messages
- `github` - GitHub repositories
- `google_drive` - Google Drive
- `gmail` - Gmail
- `bookstack` - BookStack
- `confluence` - Confluence
- `jira` - Jira
- `productboard` - Productboard
- `slab` - Slab
- `notion` - Notion
- `guru` - Guru
- `gong` - Gong
- `linear` - Linear
- `hubspot` - HubSpot
- `document360` - Document360
- `requesttracker` - Request Tracker
- `google_sites` - Google Sites
- `zendesk` - Zendesk
- `discourse` - Discourse
- `axero` - Axero
- `clickup` - ClickUp
- `mediawiki` - MediaWiki
- `wikipedia` - Wikipedia
- `sharepoint` - SharePoint
- `teams` - Microsoft Teams
- `salesforce` - Salesforce
- `discourse` - Discourse
- `airtable` - Airtable
- `asana` - Asana
- `s3` - Amazon S3
- `r2` - Cloudflare R2
- `google_cloud_storage` - Google Cloud Storage
- `oci_storage` - Oracle Cloud Storage
- `xenforo` - XenForo
- `freshdesk` - Freshdesk
- `fireflies` - Fireflies
- `dropbox` - Dropbox
- `gitlab` - GitLab
- `gitbook` - GitBook
- `discord` - Discord
- `zulip` - Zulip
- `egnyte` - Egnyte
- `highspot` - Highspot
- `drupal_wiki` - Drupal Wiki
- `bitbucket` - Bitbucket

---

## Changelog

Stay up to date with the latest features and changes:

**Documentation:** https://docs.onyx.app/changelog.md
