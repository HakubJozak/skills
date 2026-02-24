---
name: anthropic-ruby
description: This skill should be used when the user is working with the Anthropic API in Ruby, using the anthropic gem, building LLM-powered Ruby/Rails applications, integrating Claude models into Ruby code, or needs help with messages API, streaming, tool use, vision, or error handling in Ruby. Also use when the user asks about "claude API ruby", "anthropic ruby gem", "ruby llm", or "calling claude from ruby".
---

# Anthropic Ruby SDK

Use this skill when working with the Anthropic API in Ruby applications. The official gem is `anthropic` (not `anthropic-sdk-ruby`).

## Setup

**Gemfile:**
```ruby
gem "anthropic", "~> 1.23"
```

**Requirements:** Ruby >= 3.2.0

**Client initialization:**
```ruby
require "anthropic"

# Reads ANTHROPIC_API_KEY from environment automatically
client = Anthropic::Client.new

# Or explicit key
client = Anthropic::Client.new(api_key: ENV["ANTHROPIC_API_KEY"])
```

## Current Models

| Alias | Model ID | Best For |
|-------|----------|----------|
| Opus 4.6 | `claude-opus-4-6` | Hardest tasks, agents, coding |
| Sonnet 4.6 | `claude-sonnet-4-6` | Best speed/intelligence balance |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Fast, cost-efficient |

Always prefer the short alias (e.g. `claude-opus-4-6`) over dated snapshots unless pinning a version deliberately.

## Basic Message

```ruby
message = client.messages.create(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "Explain Ruby blocks in one paragraph." }
  ]
)

puts message.content.first.text
# message.usage.input_tokens / output_tokens
# message.stop_reason  → "end_turn" | "max_tokens" | "tool_use"
```

**With system prompt:**
```ruby
client.messages.create(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: "You are a senior Ruby engineer. Be concise.",
  messages: [{ role: "user", content: "What is memoization?" }]
)
```

**Common parameters:**

| Parameter | Type | Notes |
|-----------|------|-------|
| `model` | String | Required |
| `max_tokens` | Integer | Required |
| `messages` | Array | Required |
| `system` | String | Optional system prompt |
| `temperature` | Float | 0.0–1.0, default 1.0 |
| `top_p` | Float | Nucleus sampling |
| `top_k` | Integer | Top-k sampling |

## Streaming

```ruby
# Stream text chunks
client.messages.stream(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a haiku about Ruby." }]
) do |stream|
  stream.text.each { |chunk| print chunk }
end

# Accumulate final message after streaming
stream = client.messages.stream(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }]
)
final = stream.final_message
puts final.content.first.text
```

## Multi-Turn Conversation

```ruby
messages = [
  { role: "user", content: "What is 2+2?" },
  { role: "assistant", content: "4." },
  { role: "user", content: "Multiply that by 10." }
]

response = client.messages.create(
  model: "claude-sonnet-4-6",
  max_tokens: 512,
  messages: messages
)

# Append to continue conversation
messages << { role: "assistant", content: response.content.first.text }
messages << { role: "user", content: "Now subtract 5." }
```

## Tool Use

**Manual approach (plain hash tools):**
```ruby
tools = [
  {
    name: "get_weather",
    description: "Get current weather for a city",
    input_schema: {
      type: "object",
      properties: {
        city: { type: "string", description: "City name" }
      },
      required: ["city"]
    }
  }
]

response = client.messages.create(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  tools: tools,
  messages: [{ role: "user", content: "What's the weather in Prague?" }]
)

if response.stop_reason == "tool_use"
  tool_use = response.content.find { |b| b.type == "tool_use" }
  tool_result = fetch_weather(tool_use.input["city"])  # your implementation

  # Return result and continue
  client.messages.create(
    model: "claude-sonnet-4-6",
    max_tokens: 1024,
    tools: tools,
    messages: [
      { role: "user", content: "What's the weather in Prague?" },
      { role: "assistant", content: response.content },
      { role: "user", content: [
          { type: "tool_result", tool_use_id: tool_use.id, content: tool_result.to_json }
        ]
      }
    ]
  )
end
```

**Automatic tool runner (beta):**
```ruby
result = client.beta.messages.tool_runner(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "What's 25 × 4?" }],
  tools: [Calculator.new]  # Subclass of Anthropic::BaseTool
)
```

See `references/tool-use.md` for typed tool classes using `Anthropic::BaseTool`.

## Vision / Images

**Base64 image:**
```ruby
require "base64"

image_data = Base64.strict_encode64(File.binread("/path/to/image.png"))

client.messages.create(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: [
        { type: "image", source: { type: "base64", media_type: "image/png", data: image_data } },
        { type: "text", text: "What do you see in this image?" }
      ]
    }
  ]
)
```

**URL image:**
```ruby
content: [
  { type: "image", source: { type: "url", url: "https://example.com/photo.jpg" } },
  { type: "text", text: "Describe this." }
]
```

**Supported formats:** JPEG, PNG, GIF, WebP. Max 5 MB per image, 100 images per request.

## Error Handling

```ruby
begin
  client.messages.create(...)
rescue Anthropic::Errors::AuthenticationError  # 401 - bad API key
rescue Anthropic::Errors::PermissionDeniedError # 403
rescue Anthropic::Errors::RateLimitError        # 429 - back off and retry
rescue Anthropic::Errors::BadRequestError       # 400 - check params
rescue Anthropic::Errors::NotFoundError         # 404
rescue Anthropic::Errors::InternalServerError   # 500+
rescue Anthropic::Errors::APITimeoutError       # request timed out
rescue Anthropic::Errors::APIConnectionError    # network error
rescue Anthropic::Errors::APIError => e         # catch-all
  puts "#{e.status}: #{e.message}"
end
```

The SDK automatically retries on 408, 429, and 5xx errors with exponential backoff (2 retries by default).

**Configure retries/timeout:**
```ruby
client = Anthropic::Client.new(max_retries: 5, timeout: 30)

# Or per-request
client.messages.create(..., request_options: { max_retries: 0, timeout: 10 })
```

## Platform Integrations

**AWS Bedrock:**
```ruby
# gem 'aws-sdk-bedrockruntime' required
client = Anthropic::BedrockClient.new
client.messages.create(model: "anthropic.claude-sonnet-4-6-v1", ...)
```

**Google Vertex AI:**
```ruby
# gem 'googleauth' required
client = Anthropic::VertexClient.new(project_id: "my-project", region: "us-east5")
client.messages.create(model: "claude-sonnet-4-6", ...)
```

## Admin API (not in gem)

Endpoints for org management, billing, and usage analytics require an **Admin API key** (`sk-ant-admin...`) and must be called directly over HTTP. Use the `http` gem (`gem "http"`):

```ruby
require "http"

res = HTTP
  .headers(
    "x-api-key"         => ENV.fetch("ANTHROPIC_ADMIN_KEY"),
    "anthropic-version" => "2023-06-01"
  )
  .get("https://api.anthropic.com/v1/organizations/cost_report", params: {
    starting_at:  "2026-02-01T00:00:00Z",
    ending_at:    "2026-02-23T23:59:59Z",
    bucket_width: "1d"
  })
  .parse(:json)
```

See **`references/admin-api.md`** for all 19 endpoints across: cost/usage reports, API key management, users, invites, workspaces, workspace members.

## Reference Files

- **`references/admin-api.md`** — Admin API: cost report, usage report, Claude Code analytics, API key/user/workspace management (all require `sk-ant-admin...`)
- **`references/tool-use.md`** — Typed tools with `Anthropic::BaseTool`, structured inputs, and automatic tool loop patterns
- **`references/api-reference.md`** — Full response object structure, Files API, structured outputs, pagination, Sorbet types
