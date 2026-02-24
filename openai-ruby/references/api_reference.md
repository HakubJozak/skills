# OpenAI Ruby SDK — API Reference

Official gem: `openai` (github.com/openai/openai-ruby)
Requires Ruby 3.2+

---

## Installation

```ruby
# Gemfile
gem "openai", "~> 0.50.0"
```

---

## Client Initialization

```ruby
require "openai"

openai = OpenAI::Client.new(api_key: ENV["OPENAI_API_KEY"])

# With options
openai = OpenAI::Client.new(
  api_key: ENV["OPENAI_API_KEY"],
  max_retries: 2,   # default: 2
  timeout: 600      # seconds, default: 600
)
```

Per-request overrides:

```ruby
openai.chat.completions.create(
  ...,
  request_options: { max_retries: 5, timeout: 1200 }
)
```

---

## Chat Completions

```ruby
response = openai.chat.completions.create(
  model: "gpt-4o",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user",   content: "Hello!" }
  ]
)

puts response.choices[0].message.content
```

### Streaming

```ruby
stream = openai.chat.completions.stream(
  model: "gpt-4o",
  messages: [{ role: "user", content: "Write a haiku." }]
)

stream.each do |event|
  print event.choices[0].delta.content if event.choices[0].delta.content
end
```

**Important:** Close lazy streams that are not fully consumed:

```ruby
stream.close unless stream.consumed?
```

---

## Structured Outputs

### JSON mode

```ruby
response = openai.chat.completions.create(
  model: "gpt-4o",
  messages: [{ role: "user", content: "Return a recipe as JSON." }],
  response_format: { type: "json_object" }
)

data = JSON.parse(response.choices[0].message.content)
```

### Typed schema with `OpenAI::BaseModel`

```ruby
class Ingredient < OpenAI::BaseModel
  required :name, String
  required :quantity, String
end

class Recipe < OpenAI::BaseModel
  required :name, String
  required :ingredients, OpenAI::ArrayOf[Ingredient]
  required :prep_time_minutes, Integer
end

response = openai.chat.completions.create(
  model: "gpt-4o-2024-08-06",
  messages: [{ role: "user", content: "Give me a pasta recipe." }],
  response_format: {
    type: "json_schema",
    json_schema: { name: "Recipe", schema: Recipe.json_schema, strict: true }
  }
)

recipe = response.choices[0].message.parsed
puts recipe.name
puts recipe.prep_time_minutes
```

**BaseModel type helpers:**

| Helper | Example |
|--------|---------|
| `OpenAI::EnumOf[:a, :b]` | Status enum |
| `OpenAI::ArrayOf[Type]` | Typed array |
| `OpenAI::UnionOf[T1, T2]` | Union type |
| `required :field, Type` | Required field |
| `optional :field, Type` | Optional field |

---

## Embeddings

```ruby
response = openai.embeddings.create(
  model: "text-embedding-3-small",
  input: "The food was delicious."
)

vector = response.data[0].embedding  # Array of floats

# Multiple inputs
response = openai.embeddings.create(
  model: "text-embedding-3-large",
  input: ["text one", "text two", "text three"]
)
response.data.each { |d| puts d.embedding.length }
```

Models: `text-embedding-3-small` (1536d), `text-embedding-3-large` (3072d), `text-embedding-ada-002` (1536d, legacy)

---

## Image Generation (DALL-E)

```ruby
response = openai.images.generate(
  model: "dall-e-3",
  prompt: "An astronaut in a tropical resort, pixel art",
  size: "1024x1024",   # also: "1792x1024", "1024x1792"
  quality: "standard", # or "hd"
  n: 1
)

puts response.data[0].url
```

---

## Audio

### Transcription (Whisper)

```ruby
require "pathname"

response = openai.audio.transcriptions.create(
  model: "whisper-1",
  file: Pathname("audio.mp3"),
  language: "en",           # optional
  prompt: "meeting notes"   # optional context
)

puts response.text
```

### Text-to-Speech

```ruby
response = openai.audio.speech.create(
  model: "tts-1",       # or "tts-1-hd"
  voice: "alloy",       # alloy, echo, fable, onyx, nova, shimmer
  input: "Hello, world!",
  response_format: "mp3" # mp3, opus, aac, flac
)

File.write("output.mp3", response)
```

---

## File Uploads

```ruby
require "pathname"

file = openai.files.create(
  file: Pathname("data.jsonl"),
  purpose: "fine-tune"
)
puts file.id
```

Custom content type:

```ruby
image = OpenAI::FilePart.new(Pathname("photo.jpg"), content_type: "image/jpeg")
openai.files.create(file: image, purpose: "vision")
```

---

## Pagination

```ruby
# Auto-paging
openai.fine_tuning.jobs.list(limit: 20).auto_paging_each do |job|
  puts job.id
end

# Manual
page = openai.files.list(limit: 10)
loop do
  page.data.each { |f| puts f.filename }
  break unless page.next_page?
  page = page.next_page
end
```

---

## Error Handling

```ruby
begin
  openai.chat.completions.create(...)
rescue OpenAI::Errors::AuthenticationError => e
  # Invalid API key
rescue OpenAI::Errors::RateLimitError => e
  # HTTP 429 — implement backoff
rescue OpenAI::Errors::APIConnectionError => e
  # Network / server unreachable
rescue OpenAI::Errors::BadRequestError => e
  # HTTP 400
rescue OpenAI::Errors::NotFoundError => e
  # HTTP 404
rescue OpenAI::Errors::InternalServerError => e
  # HTTP 5xx (auto-retried by default)
rescue OpenAI::Errors::APITimeoutError => e
  # Request timed out
rescue OpenAI::Errors::APIError => e
  # Catch-all; e.status for HTTP code
end
```

Exponential backoff example:

```ruby
def with_backoff(max_retries: 3)
  retries = 0
  begin
    yield
  rescue OpenAI::Errors::RateLimitError
    raise if retries >= max_retries
    sleep(2 ** retries)
    retries += 1
    retry
  end
end
```

---

## Response Access

Responses support both method-style and hash-style access:

```ruby
response.choices[0].message.content          # method
response["choices"][0]["message"]["content"] # hash
```

---

## Concurrency

The gem uses `connection_pool` for thread-safe HTTP pooling:

```ruby
threads = 5.times.map do
  Thread.new { openai.chat.completions.create(model: "gpt-4o", messages: [...]) }
end
results = threads.map(&:value)
```
