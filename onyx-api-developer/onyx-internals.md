# Onyx Architecture Internals

Source-code-verified reference for the Onyx platform internals. Use this to understand **why** the API behaves the way it does, debug integration issues, and build reliable clients.

## Project Structure

```
backend/onyx/
├── server/                  # FastAPI API layer
│   ├── query_and_chat/      # Chat & search endpoints
│   │   ├── chat_backend.py  # Chat session & message endpoints
│   │   ├── streaming_models.py  # All streaming packet types
│   │   └── models.py        # Request/response Pydantic models
│   ├── documents/           # Document & credential management
│   ├── manage/              # Connector & admin endpoints
│   ├── onyx_api/            # Public API (ingestion)
│   └── middleware/          # Rate limiting, auth
├── chat/                    # Core chat logic
│   ├── process_message.py   # Main message processing flow
│   ├── llm_loop.py          # LLM call loop with tool execution
│   ├── citation_processor.py # Citation detection & formatting
│   ├── chat_state.py        # Thread-safe state accumulator
│   └── emitter.py           # Queue-based packet emission
├── llm/                     # LLM provider abstraction
│   ├── interfaces.py        # LLM base interface
│   ├── factory.py           # Provider resolution
│   └── multi_llm.py         # LiteLLM wrapper
├── tools/                   # Tool system
│   ├── interface.py         # Tool ABC
│   ├── models.py            # Tool data models
│   └── tool_implementations/
├── connectors/              # 40+ data source connectors
├── indexing/                # Chunking & embedding pipeline
├── context/search/          # Search & retrieval
├── background/celery/       # Async job processing
├── db/models.py             # SQLAlchemy models (~3000+ lines)
└── main.py                  # FastAPI app bootstrap
```

## Chat System Internals

### SendMessageRequest — The Real Input Model

The chat API accepts far more than `message` + `chat_session_id`. Key fields:

```python
class SendMessageRequest(BaseModel):
    message: str
    chat_session_id: UUID | None          # Existing session; None to create new
    chat_session_info: ChatSessionCreationRequest | None  # Inline session creation
    file_descriptors: list[FileDescriptor] # Attached files (IMAGE, DOC, PLAIN_TEXT, CSV)
    stream: bool = True                    # NDJSON streaming vs single response
    include_citations: bool = True
    deep_research: bool = False            # High token consumption mode
    allowed_tool_ids: list[int] | None     # Restrict available tools
    forced_tool_id: int | None             # Force a specific tool
    parent_message_id: int | None = -1     # Conversation tree placement
    llm_override: LLMOverride | None       # Override model/temperature per-request
    mcp_headers: dict[str, str] | None     # Headers for MCP tool calls
    origin: MessageOrigin                  # Track source (webapp, API, etc.)
```

**parent_message_id semantics:**
- `-1` (default): Append after latest message in chain
- `None`: Regenerate from root (resets history)
- Specific int: Branch conversation from that message

### Chat Session Lifecycle

1. **Create**: `POST /chat/create-chat-session` with `persona_id` → returns UUID
2. **Send messages**: `POST /chat/send-chat-message` with session UUID
3. **Override model**: `PUT /chat/update-chat-session-model` per-session
4. **Override temperature**: `PUT /chat/update-chat-session-temperature`
5. **Rename**: `PUT /chat/rename-chat-session` (explicit name or LLM-generated)
6. **Retrieve history**: `GET /chat/get-chat-session/{id}` returns all messages + streaming packets

### Message Processing Flow

```
handle_send_chat_message()
  → handle_stream_message_objects()
    ├─ Create/load chat session
    ├─ Build conversation history chain (parent_message_id tree)
    ├─ Verify and load attached files
    ├─ Load project files if in project context
    ├─ Construct tool list from persona config
    └─ run_llm_loop()
       ├─ Build system prompt (base + persona override)
       ├─ Compress conversation history if over token limit
       ├─ Call LLM (streaming)
       │  ├─ Emit ReasoningStart → ReasoningDelta → ReasoningDone
       │  ├─ Extract tool calls from LLM response
       │  └─ Emit tool-specific packets
       ├─ Execute tool calls (parallel when possible)
       ├─ Update citation mapping from tool results
       ├─ Loop back to LLM with tool results (max 6 cycles)
       └─ Generate final answer with citations
          ├─ Emit MessageStart (with final_documents)
          ├─ Emit MessageDelta chunks
          └─ Emit CitationInfo packets
```

**MAX_LLM_CYCLES = 6** — The LLM can call tools up to 6 times per user message.

### Streaming Protocol (NDJSON)

Streaming responses are **newline-delimited JSON** (NOT SSE `data:` format). Each line is a JSON object with:

```json
{
  "placement": {"turn_index": 0, "tab_index": 0, "sub_turn_index": null},
  "obj": {"type": "<StreamingType>", ...fields}
}
```

**All packet types by category:**

#### Control
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `SECTION_END` | — | End of a streaming section |
| `STOP` | `stop_reason` | Stream termination |
| `TOP_LEVEL_BRANCHING` | `num_parallel_branches` | Pre-announce parallel branches |
| `ERROR` | `exception` | Error during processing |

#### Agent Response
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `MESSAGE_START` | `final_documents`, `pre_answer_processing_seconds` | Begin answer |
| `MESSAGE_DELTA` | `content: str` | Answer text chunk |
| `CITATION_INFO` | `citation_number`, `document_id` | Citation reference |
| `TOOL_CALL_DEBUG` | `tool_call_id`, `tool_name`, `tool_args` | Debug info |

#### Reasoning (for reasoning-capable models)
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `REASONING_START` | — | Begin reasoning block |
| `REASONING_DELTA` | `reasoning: str` | Reasoning text chunk |
| `REASONING_DONE` | — | Reasoning complete |

#### Search Tool
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `SEARCH_TOOL_START` | `is_internet_search` | Search initiated |
| `SEARCH_TOOL_QUERIES_DELTA` | `queries: list[str]` | Generated queries |
| `SEARCH_TOOL_DOCUMENTS_DELTA` | `documents: list[SearchDoc]` | Retrieved docs |

#### OpenURL Tool
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `OPEN_URL_START` | — | URL crawling started |
| `OPEN_URL_URLS` | `urls: list[str]` | URLs being fetched |
| `OPEN_URL_DOCUMENTS` | `documents: list[SearchDoc]` | Crawled content |

#### Image Generation
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `IMAGE_GENERATION_START` | — | Starting |
| `IMAGE_GENERATION_HEARTBEAT` | — | Keep-alive |
| `IMAGE_GENERATION_FINAL` | `images: list[GeneratedImage]` | Results |

#### Code Execution
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `PYTHON_TOOL_START` | `code` | Code to execute |
| `PYTHON_TOOL_DELTA` | `stdout`, `stderr`, `file_ids` | Execution output |

#### Custom/MCP Tools
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `CUSTOM_TOOL_START` | `tool_name` | Tool execution begins |
| `CUSTOM_TOOL_DELTA` | `tool_name`, `response_type`, `data`, `file_ids` | Result |

#### Deep Research
| Type | Key Fields | Meaning |
|------|-----------|---------|
| `DEEP_RESEARCH_PLAN_START` | — | Research plan begins |
| `DEEP_RESEARCH_PLAN_DELTA` | `content` | Plan content |
| `RESEARCH_AGENT_START` | `research_task` | Agent task started |
| `INTERMEDIATE_REPORT_START` | — | Report section |
| `INTERMEDIATE_REPORT_DELTA` | `content` | Report content |
| `INTERMEDIATE_REPORT_CITED_DOCS` | `cited_docs` | Documents cited |

### Non-Streaming Response

When `stream: false`, the response is a single JSON object collecting all packets. The response structure matches the accumulated streaming state.

### Error Packets in Stream

```json
{
  "placement": {"turn_index": 0, "tab_index": 0},
  "obj": {
    "type": "ERROR",
    "error": "Human-readable message",
    "stack_trace": null,
    "error_code": "RATE_LIMIT",
    "is_retryable": true,
    "details": {"model_name": "gpt-4"}
  }
}
```

Error codes: `VALIDATION_ERROR`, `RATE_LIMIT`, `AUTH_ERROR`, `TIMEOUT`, `INIT_FAILED`

## Ingestion API Internals

### POST /onyx-api/ingestion — What Really Happens

**Request body:**
```json
{
  "cc_pair_id": 1,
  "document": {
    "id": "my_unique_id",
    "semantic_identifier": "Display Title",
    "title": "Document Title",
    "sections": [
      {"text": "Content here", "link": "https://source-url.com"}
    ],
    "source": "ingestion_api",
    "metadata": {"key": "value"},
    "doc_updated_at": "2024-01-01T00:00:00Z",
    "primary_owners": [{"email": "user@example.com"}],
    "secondary_owners": [],
    "from_ingestion_api": true
  }
}
```

**Internal pipeline (synchronous!):**
1. Validates the CC-pair exists and is accessible
2. Converts `DocumentBase` → `Document` with `from_ingestion_api = True`
3. Auto-generates ID if missing: `"ingestion_api_" + url_safe(semantic_identifier)`
4. Fetches active search settings (primary + secondary indices)
5. Creates `DefaultIndexingEmbedder` from search settings
6. Runs `run_indexing_pipeline()` with `ignore_time_skip=True`:
   - **Chunking**: Splits content into chunks (configurable size via `DOC_EMBEDDING_CONTEXT_SIZE`)
   - **Metadata injection**: Converts metadata to natural language prefix (capped at 25% of chunk)
   - **Embedding**: Generates vector embeddings via configured model
   - **Vespa insertion**: Stores chunks with embeddings in Vespa index
   - **PostgreSQL update**: Updates document metadata record
7. If secondary index exists, indexes there too

**Response:**
```json
{
  "document_id": "my_unique_id",
  "already_existed": false
}
```

**Key insight**: Ingestion is **synchronous** — the API returns only after full indexing completes. For bulk operations, use background jobs on your side.

**Deletion**: `DELETE /onyx-api/ingestion/{document_id}` removes from both indices + database.

### Document Model Details

Sections can be `TextSection` or `ImageSection`:
- `TextSection`: `text` (content) + `link` (optional source URL)
- `ImageSection`: `file_id` referencing uploaded image

Metadata is stored as `dict[str, str | list[str]]` and converted to natural language for embedding:
```
Metadata:
    category - procurement
    region - EU
```

## Connector & CC-Pair System

### Connector Interface Hierarchy

```
BaseConnector (ABC)
├── LoadConnector         # Full state load: load_from_state()
├── PollConnector         # Incremental: poll_source(start, end)
├── SlimConnector         # IDs only: retrieve_all_slim_docs()
├── SlimConnectorWithPermSync  # IDs + permissions
└── CheckpointedConnector # Stateful with checkpoint: load_from_checkpoint()
```

All connectors yield `GenerateDocumentsOutput` = `Iterator[list[Document]]`

### CC-Pair States

| Status | Meaning |
|--------|---------|
| `INITIAL_INDEXING` | First index in progress |
| `ACTIVE` | Running normally |
| `PAUSED` | User-paused or error-paused |

**Access types on CC-pairs:**
- `PUBLIC`: All users see documents
- `PRIVATE`: Only creator/authorized users
- `SYNC`: External permission sync (Google Workspace, etc.)

### CC-Pair Key Fields
- `connector_id` + `credential_id` = composite primary key
- `total_docs_indexed`: Running count
- `last_successful_index_time`: For incremental polling
- `indexing_trigger`: `REINDEX` (full) or `UPDATE` (incremental)
- `processing_mode`: `REGULAR` (full pipeline) or `FILE_SYSTEM` (sandbox)
- `in_repeated_error_state`: Separate from status — tracks persistent failures

### Background Processing

Jobs run via **Celery** with Redis backend:

1. **Document Fetching** (`docfetching_task`): Calls connector's poll/load method, yields documents to batch storage
2. **Document Processing** (`docprocessing_task`): Chunking → Embedding → Vespa insertion
3. **Pruning** (`prune_generator_task`): Removes documents no longer in source
4. **Permission Sync** (EE): Syncs document-level permissions from external sources

**IndexAttempt** tracks each job run with status: `NOT_STARTED` → `IN_PROGRESS` → `SUCCESS`/`FAILED`/`CANCELED`

**Cancellation**: Redis-based stop signals allow real-time cancellation of in-flight jobs.

## Search Internals

### Hybrid Search Pipeline

```
Query → Query Embedding + Keyword Extraction
  ↓
Vespa Hybrid Retrieval
  ├─ Semantic: embedding cosine similarity
  ├─ Keyword: BM25 scoring
  └─ hybrid_alpha: configurable blend ratio (0=keyword, 1=semantic)
  ↓
Access Control Filtering (per-user ACLs)
  ↓
Recency Bias (time decay multiplier)
  ↓
Chunk Merging (adjacent chunks from same doc → InferenceSection)
  ↓
Results: list[InferenceChunk] with scores
```

### IndexFilters (search-time filtering)

```python
class IndexFilters:
    source_type: list[DocumentSource] | None    # Filter by connector source
    document_set: list[str] | None              # Filter by document set name
    time_cutoff: datetime | None                # Only docs after this date
    tags: list[str] | None                      # Metadata tag filtering
    access_control_list: list[AccessFilter]     # Per-user ACLs (automatic)
    tenant_id: str | None                       # Multi-tenant isolation
```

### Access Control at Search Time

Multi-level access control is **always applied** at search time:
1. CC-pair level: PUBLIC/PRIVATE/SYNC
2. Document level: `external_user_emails`, `external_user_group_ids`, `is_public`
3. Document set level: `is_public` + explicit user/group assignments
4. User group membership checked against all levels

## LLM Provider Abstraction

Uses **LiteLLM** under the hood for multi-provider support.

### Provider Resolution Order
1. Per-request `llm_override` (from `SendMessageRequest`)
2. Persona/Agent-configured provider
3. System default provider

### Supported Providers
OpenAI, Anthropic, Vertex AI, Ollama, AWS Bedrock, OpenRouter, Azure OpenAI, and any LiteLLM-compatible provider.

### LLM Interface
```python
class LLM:
    def invoke(prompt, tools=None, tool_choice=None, ...) -> ModelResponse
    def stream(prompt, tools=None, ...) -> Iterator[ModelResponseStream]
```

Key options: `reasoning_effort` (for o1/Claude), `structured_response_format` (JSON schema), `user_identity` (cost tracking).

## Tool System

### Built-in Tools
| Tool | Description |
|------|-------------|
| Search | Internal knowledge base search with query expansion |
| Web Search | Internet search (Google, Serper, Exa, Firecrawl) |
| OpenURL | Fetch and crawl URLs |
| Python/Code Interpreter | Execute Python code |
| Image Generation | DALL-E or similar |
| Custom Tools | User-defined via OpenAPI specs |
| MCP Tools | Model Context Protocol integration |

### Tool Execution
- Tools extracted from LLM response automatically
- Run in parallel when independent (differentiated by `tab_index`)
- Results fed back to LLM for next cycle
- Each tool emits progress packets via thread-safe `Emitter` queue

### ToolResponse Structure
```python
class ToolResponse:
    rich_response: SearchDocsResponse | CustomToolCallSummary | str | None
    llm_facing_response: str   # Text inserted into LLM conversation history
    tool_call: ToolCallKickoff | None
```

## Citation System

- Citations detected as `[1]`, `[1,2]`, `[[1]]`, or Unicode variants `【】`, `［］`
- Skipped inside code blocks (triple backticks)
- Dynamic mapping: `citation_number → SearchDoc` updated as tools return results
- Modes: `REMOVE` (strip), `KEEP_MARKERS` (preserve `[1]`), `HYPERLINK` (markdown links)
- Stored in DB: `ChatMessage.citations = {1: "doc_id_abc", 2: "doc_id_def"}`

## Rate Limiting

- FastAPI-Limiter with Redis backend
- Config: `RATE_LIMIT_MAX_REQUESTS` per `RATE_LIMIT_WINDOW_SECONDS`
- Key: IP + User-Agent combined
- Additional token-based rate limiting on chat endpoints
- Cost limit checking for Onyx-managed API keys (`check_llm_cost_limit_for_provider()`)

## Credential Storage

- Credentials encrypted at rest via `EncryptedJson` column type
- API responses mask sensitive values (`***MASKED***`)
- Credentials linked to connectors via CC-pairs
- Support for file-based credentials (e.g., service account JSON) via `POST /manage/credential/private-key`

## Key Gotchas for API Consumers

1. **Streaming is NDJSON, not SSE**: Parse line-by-line JSON, not `data:` prefixed events
2. **Ingestion is synchronous**: The POST blocks until chunking + embedding + indexing completes
3. **Document IDs must be URL-compatible**: Auto-generated if not provided
4. **CC-pair is required for ingestion**: Documents not linked to a CC-pair won't appear in Admin Panel
5. **Chat sessions have tree structure**: Messages form a tree via `parent_message_id`, not a flat list
6. **Tool calls loop up to 6 times**: A single user message can trigger multiple LLM rounds
7. **Access control is always enforced**: Even search results are filtered per-user ACLs
8. **Metadata becomes part of embeddings**: Metadata is converted to natural language and embedded alongside content (max 25% of chunk)
9. **`from_ingestion_api` flag**: Documents ingested via API are marked differently from connector-ingested docs
10. **Secondary index**: Onyx can maintain two indices simultaneously during model transitions; ingestion writes to both
