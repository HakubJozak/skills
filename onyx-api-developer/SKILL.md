---
description: Integrate Onyx API into your application. Use when you are using Onyx, Onyx API, writing connectors or deploying Onyx. Contains insights about Onyx internals and implementation. 
scope: all
---

# Onyx API Developer Skill

You are an expert in building integrations with the Onyx API platform. You have comprehensive knowledge of Onyx's REST APIs, authentication methods, data models, and best practices.

## Your Expertise

You specialize in:
- Designing and implementing Onyx API bridges and integrations
- Working with Onyx's Chat, Agent, Search, Connector, and Ingestion APIs
- Building authentication and authorization flows
- Implementing proper error handling and rate limiting
- Creating robust document ingestion pipelines
- Managing connectors and credentials programmatically
- Optimizing API usage and performance

## Available Resources

- **API Documentation:** `~/skills/onyx-api-developer/onyx-api-documentation.md` — endpoint specs, request/response formats
- **Architecture Internals:** `~/skills/onyx-api-developer/onyx-internals.md` — source-code-verified internals: streaming protocol, ingestion pipeline, data models, tool system, search pipeline
- **Onyx Source Code:** `~/code/onyx` — full source code for deep investigation

**Always reference the documentation and internals** when answering questions about Onyx APIs. The internals file is especially important for understanding streaming packet types, the ingestion pipeline, and debugging integration issues.

## Core Concepts to Remember

### Authentication
- Three API key types: Admin (full access), Basic (recommended), Limited (restricted)
- Always use Bearer token authentication: `Authorization: Bearer YOUR_API_KEY`
- Store API keys in environment variables, never in code

### API Base URLs
- Onyx Cloud: `https://cloud.onyx.app/api`
- Self-hosted: `https://your-instance.com/api`
- OpenAPI Explorer: `https://your-instance.com/api/docs`

### Key Endpoints
- **Chat:** `POST /chat/send-chat-message`
- **Agents:** `GET /agents` (list), `POST /agents` (create)
- **Search:** `POST /search/handle-search-request`
- **Connectors:** `GET /manage/connector` (list), `POST /manage/admin/connector` (create)
- **Ingestion:** `POST /onyx-api/ingestion`

### Data Models
- **Agents:** AI assistants with custom instructions, tools, and data access
- **Connectors:** Define indexed data sources (40+ integrations)
- **CC-Pairs:** ConnectorCredentialPairs link connectors with credentials
- **Documents:** Core content model with sections, metadata, and access control

## Building an API Bridge

### Step 1: Authentication Setup

```ruby
# In Rails, create a service object for Onyx API client
class OnyxApiClient
  include HTTParty
  base_uri ENV.fetch('ONYX_API_BASE_URL', 'https://cloud.onyx.app/api')

  def initialize(api_key = nil)
    @api_key = api_key || ENV['ONYX_API_KEY']
    @options = {
      headers: {
        'Authorization' => "Bearer #{@api_key}",
        'Content-Type' => 'application/json'
      }
    }
  end

  def headers
    @options[:headers]
  end
end
```

### Step 2: Implement Core API Methods

```ruby
# Chat API
def send_message(message, options = {})
  payload = {
    message: message,
    stream: options.fetch(:stream, false),
    include_citations: options.fetch(:include_citations, true)
  }

  # Add optional parameters
  payload[:chat_session_id] = options[:chat_session_id] if options[:chat_session_id]
  payload[:internal_search_filters] = options[:filters] if options[:filters]
  payload[:llm_override] = options[:llm_override] if options[:llm_override]

  response = self.class.post('/chat/send-chat-message', @options.merge(body: payload.to_json))
  handle_response(response)
end

# Agent API
def list_agents(page: 0, page_size: 10, include_default: true)
  query = { page_num: page, page_size: page_size, include_default: include_default }
  response = self.class.get('/agents', @options.merge(query: query))
  handle_response(response)
end

# Search API
def search(query, filters = {})
  payload = { query: query }.merge(filters)
  response = self.class.post('/search/handle-search-request', @options.merge(body: payload.to_json))
  handle_response(response)
end

# Connector API
def list_connectors
  response = self.class.get('/manage/connector', @options)
  handle_response(response)
end

def create_connector(name:, source:, config:, refresh_freq: 3600, prune_freq: 86400)
  payload = {
    name: name,
    source: source,
    input_type: 'poll',
    access_type: 'PUBLIC',
    connector_specific_config: config,
    refresh_freq: refresh_freq,
    prune_freq: prune_freq
  }

  response = self.class.post('/manage/admin/connector', @options.merge(body: payload.to_json))
  handle_response(response)
end

def associate_credential(connector_id, credential_id)
  response = self.class.put(
    "/manage/admin/connector/#{connector_id}/credential/#{credential_id}",
    @options
  )
  handle_response(response)
end

# Ingestion API
def ingest_document(document, cc_pair_id:)
  payload = {
    document: document,
    cc_pair_id: cc_pair_id
  }

  response = self.class.post('/onyx-api/ingestion', @options.merge(body: payload.to_json))
  handle_response(response)
end

# Error handling
def handle_response(response)
  case response.code
  when 200..299
    response.parsed_response
  when 401
    raise OnyxAuthError, 'Invalid or missing API key'
  when 403
    raise OnyxAuthError, 'Insufficient permissions'
  when 422
    raise OnyxValidationError, response.parsed_response['detail']
  when 429
    raise OnyxRateLimitError, 'Rate limit exceeded'
  else
    raise OnyxApiError, "API error: #{response.code} - #{response.message}"
  end
end

# Custom exceptions
class OnyxApiError < StandardError; end
class OnyxAuthError < OnyxApiError; end
class OnyxValidationError < OnyxApiError; end
class OnyxRateLimitError < OnyxApiError; end
```

### Step 3: Implement Streaming Support

**IMPORTANT**: Onyx streaming uses **NDJSON** (newline-delimited JSON), NOT SSE (`data:` prefix).
Each line is a complete JSON object with `placement` and `obj` fields.
See `~/skills/onyx-api-developer/onyx-internals.md` for the full streaming protocol reference.

```ruby
# For streaming chat responses (NDJSON format, NOT SSE)
def send_message_streaming(message, options = {}, &block)
  payload = {
    message: message,
    stream: true,
    include_citations: options.fetch(:include_citations, true)
  }

  # Add optional parameters
  payload[:chat_session_id] = options[:chat_session_id] if options[:chat_session_id]

  uri = URI("#{self.class.base_uri}/chat/send-chat-message")
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = uri.scheme == 'https'

  request = Net::HTTP::Post.new(uri.path)
  request['Authorization'] = "Bearer #{@api_key}"
  request['Content-Type'] = 'application/json'
  request.body = payload.to_json

  buffer = ""
  http.request(request) do |response|
    response.read_body do |chunk|
      buffer << chunk
      # NDJSON: each line is a complete JSON packet
      while (line_end = buffer.index("\n"))
        line = buffer.slice!(0..line_end).strip
        next if line.empty?

        packet = JSON.parse(line)
        # packet["obj"]["type"] identifies the packet kind:
        # MESSAGE_DELTA (answer text), CITATION_INFO, SEARCH_TOOL_START, etc.
        block.call(packet) if block_given?
      end
    end
  end
end
```

### Step 4: Create Models

```ruby
# app/models/onyx_agent.rb
class OnyxAgent
  attr_reader :id, :name, :description, :tools, :document_sets

  def initialize(attrs)
    @id = attrs['id']
    @name = attrs['name']
    @description = attrs['description']
    @tools = attrs['tools'] || []
    @document_sets = attrs['document_sets'] || []
  end

  def self.all(client)
    response = client.list_agents(page_size: 100)
    response['items'].map { |attrs| new(attrs) }
  end
end

# app/models/onyx_connector.rb
class OnyxConnector
  attr_reader :id, :name, :source, :input_type, :config

  def initialize(attrs)
    @id = attrs['id']
    @name = attrs['name']
    @source = attrs['source']
    @input_type = attrs['input_type']
    @config = attrs['connector_specific_config']
  end

  def self.all(client)
    client.list_connectors.map { |attrs| new(attrs) }
  end

  def self.create(client, **params)
    attrs = client.create_connector(**params)
    new(attrs)
  end
end

# app/models/onyx_document.rb
class OnyxDocument
  def self.build(id:, title:, content:, source:, **options)
    {
      id: id,
      semantic_identifier: title,
      title: options[:title] || title,
      sections: [
        {
          text: content,
          link: options[:link]
        }.compact
      ],
      source: source,
      metadata: options[:metadata] || {},
      doc_updated_at: options[:updated_at]&.iso8601 || Time.current.iso8601,
      primary_owners: options[:owners]&.map { |email| { email: email } } || []
    }
  end

  def self.ingest(client, document, cc_pair_id:)
    client.ingest_document(document, cc_pair_id: cc_pair_id)
  end
end
```

### Step 5: Create Service Objects

```ruby
# app/services/onyx_chat_service.rb
class OnyxChatService
  def initialize(client = nil)
    @client = client || OnyxApiClient.new
  end

  def ask(question, filters: nil, citations: true)
    options = {
      stream: false,
      include_citations: citations
    }

    options[:filters] = filters if filters.present?

    @client.send_message(question, options)
  end

  def ask_with_session(question, session_id, filters: nil)
    options = {
      stream: false,
      chat_session_id: session_id
    }

    options[:filters] = filters if filters.present?

    @client.send_message(question, options)
  end
end

# app/services/onyx_ingestion_service.rb
class OnyxIngestionService
  def initialize(client = nil)
    @client = client || OnyxApiClient.new
  end

  def ingest_record(record, cc_pair_id:)
    document = build_document_from_record(record)
    @client.ingest_document(document, cc_pair_id: cc_pair_id)
  end

  def bulk_ingest(records, cc_pair_id:)
    results = { success: [], failed: [] }

    records.each do |record|
      begin
        ingest_record(record, cc_pair_id: cc_pair_id)
        results[:success] << record.id
      rescue => e
        results[:failed] << { record_id: record.id, error: e.message }
      end
    end

    results
  end

  private

  def build_document_from_record(record)
    OnyxDocument.build(
      id: "#{record.class.name.underscore}_#{record.id}",
      title: record.title,
      content: record.content,
      source: record.class.name.underscore,
      metadata: record.metadata,
      updated_at: record.updated_at,
      owners: [record.owner&.email].compact
    )
  end
end
```

## Best Practices

### Error Handling
1. Always wrap API calls in begin/rescue blocks
2. Implement exponential backoff for rate limit errors
3. Log all API errors with context
4. Provide meaningful error messages to users

### Rate Limiting
1. Monitor rate limit headers in responses
2. Implement request queuing for high-volume operations
3. Use background jobs for bulk operations
4. Cache responses when appropriate

### Security
1. Store API keys in environment variables or encrypted credentials
2. Use Basic API keys for most operations
3. Reserve Admin API keys for administrative tasks
4. Never expose API keys in logs or error messages
5. Rotate API keys regularly

### Performance
1. Use pagination for large result sets
2. Enable streaming for real-time chat interactions
3. Implement caching for frequently accessed data
4. Use background jobs for ingestion operations
5. Batch operations when possible

### Data Ingestion
1. Always set `cc_pair_id` for Admin Panel visibility
2. Use stable, unique document IDs
3. Include meaningful `semantic_identifier` values
4. Provide `doc_updated_at` for version tracking
5. Handle asynchronous processing (API returns before completion)

### Search & Chat
1. Use `internal_search_filters` to focus searches
2. Enable `include_citations` for transparency
3. Be cautious with `deep_research` (high token consumption)
4. Provide relevant `file_descriptors` when available
5. Reuse `chat_session_id` for conversation continuity

## Common Patterns

### Pattern: Syncing External Data to Onyx

```ruby
# app/jobs/sync_to_onyx_job.rb
class SyncToOnyxJob < ApplicationJob
  queue_as :default

  def perform(record_type, record_ids)
    client = OnyxApiClient.new
    service = OnyxIngestionService.new(client)
    records = record_type.constantize.where(id: record_ids)

    results = service.bulk_ingest(records, cc_pair_id: ENV['ONYX_CC_PAIR_ID'])

    # Log results
    Rails.logger.info("Onyx sync completed: #{results[:success].count} succeeded, #{results[:failed].count} failed")

    # Handle failures
    results[:failed].each do |failure|
      Rails.logger.error("Failed to sync #{failure[:record_id]}: #{failure[:error]}")
    end
  end
end
```

### Pattern: Interactive Chat Interface

```ruby
# app/controllers/onyx_chat_controller.rb
class OnyxChatController < ApplicationController
  def create
    service = OnyxChatService.new

    result = service.ask(
      params[:message],
      filters: build_filters,
      citations: true
    )

    render json: {
      answer: result['answer'],
      citations: result['citation_info'],
      message_id: result['message_id'],
      session_id: result['chat_session_id']
    }
  rescue OnyxApiError => e
    render json: { error: e.message }, status: :unprocessable_entity
  end

  private

  def build_filters
    return nil unless params[:filters].present?

    {
      source_type: params[:filters][:sources],
      time_cutoff: params[:filters][:since]&.to_datetime&.iso8601
    }.compact
  end
end
```

### Pattern: Webhook Integration

```ruby
# app/controllers/webhooks/onyx_connector_controller.rb
class Webhooks::OnyxConnectorController < ApplicationController
  skip_before_action :verify_authenticity_token

  def ingest
    # Webhook from external system
    service = OnyxIngestionService.new

    document = OnyxDocument.build(
      id: params[:external_id],
      title: params[:title],
      content: params[:content],
      source: 'webhook',
      metadata: params[:metadata]
    )

    result = OnyxDocument.ingest(
      OnyxApiClient.new,
      document,
      cc_pair_id: ENV['ONYX_WEBHOOK_CC_PAIR_ID']
    )

    head :ok
  rescue => e
    Rails.logger.error("Onyx webhook ingestion failed: #{e.message}")
    head :unprocessable_entity
  end
end
```

## Testing

### RSpec Examples

```ruby
# spec/services/onyx_chat_service_spec.rb
RSpec.describe OnyxChatService do
  let(:client) { instance_double(OnyxApiClient) }
  let(:service) { described_class.new(client) }

  describe '#ask' do
    it 'sends a message and returns the response' do
      response = {
        'answer' => 'Test answer',
        'message_id' => 123,
        'chat_session_id' => 'uuid'
      }

      expect(client).to receive(:send_message).with(
        'Test question',
        hash_including(stream: false, include_citations: true)
      ).and_return(response)

      result = service.ask('Test question')
      expect(result['answer']).to eq('Test answer')
    end
  end
end

# spec/requests/onyx_chat_spec.rb
RSpec.describe 'Onyx Chat API', type: :request do
  describe 'POST /onyx_chat' do
    before do
      stub_request(:post, "#{ENV['ONYX_API_BASE_URL']}/chat/send-chat-message")
        .to_return(
          status: 200,
          body: {
            answer: 'Test answer',
            message_id: 123,
            chat_session_id: 'uuid'
          }.to_json,
          headers: { 'Content-Type' => 'application/json' }
        )
    end

    it 'returns a chat response' do
      post onyx_chat_path, params: { message: 'Test question' }

      expect(response).to have_http_status(:ok)
      expect(JSON.parse(response.body)['answer']).to eq('Test answer')
    end
  end
end
```

## When to Use Each API

### Chat API
- Building conversational interfaces
- Q&A systems over organizational knowledge
- Interactive AI assistants
- Customer support automation

### Ingestion API
- Syncing external data sources
- Custom connector implementations
- Real-time document updates
- Event-driven indexing

### Connector API
- Programmatic connector management
- Multi-tenant deployments
- Dynamic data source configuration
- Automated setup workflows

### Search API
- Direct search without chat interface
- Custom search UIs
- Analytics and reporting
- Content discovery tools

### Agent API
- Managing custom AI assistants
- Template-based agent creation
- Multi-agent systems
- Domain-specific assistants

## Quick Reference

### Environment Variables
```bash
ONYX_API_KEY=your_api_key_here
ONYX_API_BASE_URL=https://cloud.onyx.app/api
ONYX_CC_PAIR_ID=1
```

### Common HTTP Headers
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### HTTP Status Codes
- `200` - Success
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Critical Gotchas (Source-Code Verified)

1. **Streaming is NDJSON, not SSE**: Parse line-by-line JSON objects, NOT `data:` prefixed events
2. **Ingestion is synchronous**: `POST /onyx-api/ingestion` blocks until chunking + embedding + Vespa indexing completes — use background jobs for bulk operations
3. **Document IDs must be URL-compatible**: Auto-generated as `"ingestion_api_" + url_safe(semantic_identifier)` if not provided
4. **CC-pair required for ingestion**: Documents not linked to a CC-pair won't appear in Admin Panel
5. **Chat sessions have tree structure**: Messages form a tree via `parent_message_id`, not a flat list
6. **Tool calls loop up to 6 times**: A single user message can trigger up to `MAX_LLM_CYCLES = 6` LLM rounds with tool execution
7. **Access control always enforced**: Search results are filtered per-user ACLs at query time
8. **Metadata embedded in chunks**: Metadata is converted to natural language and embedded alongside content (capped at 25% of chunk size)
9. **`from_ingestion_api` flag**: Documents ingested via API are marked differently from connector-ingested docs
10. **Dual index support**: Onyx can maintain two indices during model transitions; ingestion writes to both

## Resources

- **API Documentation:** `~/skills/onyx-api-developer/onyx-api-documentation.md`
- **Architecture Internals:** `~/skills/onyx-api-developer/onyx-internals.md`
- **Onyx Source Code:** `~/code/onyx`
- **OpenAPI Explorer:** `https://your-instance.com/api/docs`
- **Community Discord:** https://discord.gg/TDJ59cGV2X
- **Index:** https://docs.onyx.app/llms.txt

## Your Approach

When helping with Onyx API integration:

1. **Reference both docs** - Check `onyx-api-documentation.md` for endpoint specs AND `onyx-internals.md` for how things work under the hood
2. **Check source code when uncertain** - The Onyx source at `~/code/onyx` is the ground truth; read it when documentation is ambiguous
3. **Provide complete examples** - Include error handling, authentication, and best practices
4. **Explain trade-offs** - Discuss different approaches and their implications
5. **Follow Rails conventions** - Use service objects, models, and jobs appropriately
6. **Emphasize security** - Highlight API key management and secure practices
7. **Consider scale** - Suggest background jobs, caching, and pagination for production use
8. **Test thoroughly** - Provide RSpec examples and testing strategies

Remember: You're building a production-grade API bridge. Code should be robust, maintainable, and follow best practices for Rails applications.
