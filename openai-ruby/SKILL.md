---
name: openai-ruby
description: Use the official OpenAI Ruby SDK (`openai` gem) to call GPT models, generate embeddings, create images, transcribe audio, and more. This skill should be used when Ruby or Rails code uses or will use the `openai` gem, when the user asks to call GPT/OpenAI APIs from Ruby, or when working with chat completions, streaming, structured outputs, DALL-E, Whisper, or TTS in a Ruby context.
---

# OpenAI Ruby

Integrate the official OpenAI Ruby SDK into Ruby/Rails applications using the `openai` gem.

## Quick Start

```ruby
# Gemfile
gem "openai", "~> 0.50.0"
```

```ruby
require "openai"

openai = OpenAI::Client.new(api_key: ENV["OPENAI_API_KEY"])

response = openai.chat.completions.create(
  model: "gpt-4o",
  messages: [{ role: "user", content: "Hello!" }]
)
puts response.choices[0].message.content
```

Requirements: Ruby 3.2+, API key from platform.openai.com.

## Key Capabilities

| Task | Method |
|------|--------|
| Chat completion | `openai.chat.completions.create(...)` |
| Streaming | `openai.chat.completions.stream(...)` |
| Structured output | `response_format: { type: "json_schema", ... }` |
| Embeddings | `openai.embeddings.create(...)` |
| Image generation | `openai.images.generate(...)` |
| Audio transcription | `openai.audio.transcriptions.create(...)` |
| Text-to-speech | `openai.audio.speech.create(...)` |

## Structured Outputs with BaseModel

To extract typed data, define schema classes inheriting from `OpenAI::BaseModel`:

```ruby
class Event < OpenAI::BaseModel
  required :name, String
  required :date, String
  required :status, OpenAI::EnumOf[:confirmed, :tentative, :cancelled]
  required :attendees, OpenAI::ArrayOf[String]
  optional :location, String
end

response = openai.chat.completions.create(
  model: "gpt-4o-2024-08-06",
  messages: [{ role: "user", content: "Extract: Team lunch on Friday, confirmed, Alice and Bob attending" }],
  response_format: {
    type: "json_schema",
    json_schema: { name: "Event", schema: Event.json_schema, strict: true }
  }
)

event = response.choices[0].message.parsed  # typed object
puts event.name
```

Use `OpenAI::ArrayOf[T]`, `OpenAI::EnumOf[:a, :b]`, `OpenAI::UnionOf[T1, T2]` for complex types.

## Streaming

```ruby
stream = openai.chat.completions.stream(
  model: "gpt-4o",
  messages: [{ role: "user", content: "Tell me a story." }]
)

stream.each do |event|
  print event.choices[0].delta.content if event.choices[0].delta.content
end

# Always close unused lazy streams
stream.close unless stream.consumed?
```

## Error Handling

The SDK auto-retries on 5xx errors (default: 2 retries). Handle client-side errors explicitly:

```ruby
rescue OpenAI::Errors::AuthenticationError  # bad API key
rescue OpenAI::Errors::RateLimitError       # 429, implement backoff
rescue OpenAI::Errors::BadRequestError      # 400, invalid params
rescue OpenAI::Errors::APIConnectionError   # network issues
rescue OpenAI::Errors::APIError             # catch-all
```

## HTTP Client Preference

When making raw HTTP calls to OpenAI endpoints not covered by the SDK (e.g. billing/credits), use the `http` gem (`http.rb`) — not `net/http`:

```ruby
# Gemfile
gem "http"
```

```ruby
response = HTTP
  .auth("Bearer #{api_key}")
  .get("https://api.openai.com/v1/dashboard/billing/credit_grants")

data = JSON.parse(response.body.to_s, symbolize_names: true)
```

## Reference

For full code examples covering all APIs (embeddings, DALL-E, Whisper, TTS, file uploads, pagination, concurrency), read:

`references/api_reference.md`
