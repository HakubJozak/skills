# API Reference

## Response Object Structure

```ruby
message = client.messages.create(...)

message.id           # "msg_01Xfn..."
message.type         # "message"
message.role         # "assistant"
message.model        # "claude-sonnet-4-6"
message.stop_reason  # "end_turn" | "max_tokens" | "tool_use" | "stop_sequence"
message.stop_sequence # nil or matched stop sequence string

# Content blocks array
message.content      # Array of content blocks
message.content.first.type  # "text" or "tool_use"
message.content.first.text  # For text blocks

# Tool use block
tool_block = message.content.find { |b| b.type == "tool_use" }
tool_block.id     # "toolu_01..."
tool_block.name   # "get_weather"
tool_block.input  # Hash with tool arguments

# Token usage
message.usage.input_tokens   # Integer
message.usage.output_tokens  # Integer
```

## Streaming Events

When using `messages.stream`, events are SSE objects:

| Event Type | Description |
|------------|-------------|
| `message_start` | Message metadata (model, usage estimate) |
| `content_block_start` | Start of a content block |
| `content_block_delta` | Incremental text/thinking content |
| `content_block_stop` | End of a content block |
| `message_delta` | Final stop_reason and usage |
| `message_stop` | Stream complete |

```ruby
stream = client.messages.stream(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }]
)

stream.each do |event|
  case event.type
  when "content_block_delta"
    print event.delta.text if event.delta.type == "text_delta"
  when "message_stop"
    puts "\nDone"
  end
end
```

## Files API (Beta)

Upload files once and reuse them across requests:

```ruby
# Upload
file = client.beta.files.upload(file: Pathname("/path/to/document.pdf"))
file.id       # "file_01..."
file.filename # "document.pdf"
file.size     # bytes

# Use in messages
content: [
  { type: "document", source: { type: "file", file_id: file.id } },
  { type: "text", text: "Summarize this document." }
]

# Or for images
content: [
  { type: "image", source: { type: "file", file_id: file.id } },
  { type: "text", text: "Describe this image." }
]

# List files
client.beta.files.list.each { |f| puts f.id }

# Delete
client.beta.files.delete(file.id)
```

## Structured Outputs

Constrain the model to return well-typed JSON matching a schema:

```ruby
class ProductInfo < Anthropic::BaseModel
  required :name, String
  required :price, Float
  required :in_stock, Anthropic::BooleanModel
  optional :description, String
end

class ExtractedProducts < Anthropic::BaseModel
  required :products, Anthropic::ArrayOf[ProductInfo]
end

message = client.messages.create(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "List 3 products from our catalog." }],
  output_config: { format: ExtractedProducts }
)

result = message.parsed_output  # ExtractedProducts instance
result.products.first.name      # Typed access
```

## Stop Sequences

```ruby
client.messages.create(
  ...,
  stop_sequences: ["</answer>", "END"]
)
# message.stop_reason == "stop_sequence"
# message.stop_sequence == "</answer>"
```

## Extended Thinking (Opus)

```ruby
client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [{ role: "user", content: "Solve this complex problem..." }]
)

# Response includes thinking blocks
message.content.each do |block|
  if block.type == "thinking"
    puts "Thinking: #{block.thinking}"
  elsif block.type == "text"
    puts "Answer: #{block.text}"
  end
end
```

## Pagination (List Endpoints)

```ruby
# Auto-paging iterator
client.beta.files.list.auto_paging_each do |file|
  puts file.id
end

# Manual pagination
page = client.beta.files.list(limit: 10)
page.data         # Array of items
page.has_more     # Boolean
page.first_id     # Cursor for before
page.last_id      # Cursor for after

next_page = client.beta.files.list(after: page.last_id, limit: 10)
```

## Rails Integration

**In a Rails service object:**
```ruby
# app/services/claude_service.rb
class ClaudeService
  def initialize
    @client = Anthropic::Client.new  # reads ANTHROPIC_API_KEY
  end

  def chat(user_message, system: nil)
    params = {
      model: "claude-sonnet-4-6",
      max_tokens: 2048,
      messages: [{ role: "user", content: user_message }]
    }
    params[:system] = system if system

    response = @client.messages.create(**params)
    response.content.first.text
  rescue Anthropic::Errors::RateLimitError
    raise "Rate limited. Please try again in a moment."
  rescue Anthropic::Errors::APIError => e
    raise "API error #{e.status}: #{e.message}"
  end
end
```

**Environment config (`config/credentials.yml.enc` or `.env`):**
```
ANTHROPIC_API_KEY=sk-ant-...
```

**Caching responses:**
```ruby
def cached_chat(prompt)
  Rails.cache.fetch(["claude", Digest::MD5.hexdigest(prompt)], expires_in: 1.hour) do
    chat(prompt)
  end
end
```

## Sorbet / RBS Types

The gem ships full type definitions:

```ruby
# T::Sig usage with Sorbet
sig { params(text: String).returns(String) }
def ask_claude(text)
  client = T.let(Anthropic::Client.new, Anthropic::Client)
  response = client.messages.create(
    model: "claude-sonnet-4-6",
    max_tokens: 512,
    messages: [{ role: "user", content: text }]
  )
  T.cast(response.content.first, Anthropic::Models::TextBlock).text
end
```

## Connection Pooling & Thread Safety

- Default connection pool: 99 connections per client
- Clients are thread-safe — share a single instance across threads
- For Rails: initialize once in an initializer, not per-request

```ruby
# config/initializers/anthropic.rb
ANTHROPIC_CLIENT = Anthropic::Client.new(
  max_retries: 3,
  timeout: 60
)
```

## Useful Links

- GitHub: https://github.com/anthropics/anthropic-sdk-ruby
- Models overview: https://docs.anthropic.com/en/docs/about-claude/models/overview
- Messages API: https://docs.anthropic.com/en/api/messages
- Tool use guide: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- Vision guide: https://docs.anthropic.com/en/docs/build-with-claude/vision
