# Tool Use Reference

## Typed Tool Classes (Recommended)

Use `Anthropic::BaseTool` and `Anthropic::BaseModel` for strongly-typed tools with Sorbet support.

```ruby
require "anthropic"

class WeatherInput < Anthropic::BaseModel
  required :city, String
  required :unit, Anthropic::InputSchema::EnumOf[:celsius, :fahrenheit]
end

class GetWeather < Anthropic::BaseTool
  input_schema WeatherInput

  def call(input)
    # input.city and input.unit are typed
    fetch_from_api(input.city, input.unit)
  end
end

class CalculatorInput < Anthropic::BaseModel
  required :lhs, Float
  required :rhs, Float
  required :operator, Anthropic::InputSchema::EnumOf[:+, :-, :*, :/]
end

class Calculator < Anthropic::BaseTool
  input_schema CalculatorInput

  def call(input)
    input.lhs.public_send(input.operator, input.rhs)
  end
end
```

## Automatic Tool Runner (Beta)

The tool runner handles the full agentic loop automatically — calling tools, returning results, and repeating until `stop_reason == "end_turn"`.

```ruby
client = Anthropic::Client.new

result = client.beta.messages.tool_runner(
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "What is 12 * 7, then add 5?" }],
  tools: [Calculator.new, GetWeather.new]
)

# Iterate all messages exchanged during the loop
result.each_message do |message|
  puts message.content
end

# Or get the final message directly
puts result.final_message.content.first.text
```

## Manual Tool Loop

For full control over tool execution:

```ruby
def run_tool_loop(client, messages, tools)
  loop do
    response = client.messages.create(
      model: "claude-sonnet-4-6",
      max_tokens: 1024,
      tools: tools,
      messages: messages
    )

    messages << { role: "assistant", content: response.content }

    break if response.stop_reason == "end_turn"

    # Process all tool_use blocks
    tool_results = response.content
      .select { |b| b.type == "tool_use" }
      .map do |tool_use|
        result = dispatch_tool(tool_use.name, tool_use.input)
        { type: "tool_result", tool_use_id: tool_use.id, content: result.to_s }
      end

    messages << { role: "user", content: tool_results }
  end

  messages
end

def dispatch_tool(name, input)
  case name
  when "get_weather" then fetch_weather(input["city"])
  when "calculator"  then calculate(input)
  else raise "Unknown tool: #{name}"
  end
end
```

## Parallel Tool Use

Claude may call multiple tools in a single response. Always handle all `tool_use` blocks before continuing:

```ruby
tool_use_blocks = response.content.select { |b| b.type == "tool_use" }

# Execute in parallel if desired
results = tool_use_blocks.map do |block|
  { type: "tool_result", tool_use_id: block.id, content: run_tool(block) }
end

messages << { role: "user", content: results }
```

## Tool Result with Error

```ruby
{ type: "tool_result", tool_use_id: tool_use.id, content: "Error: City not found", is_error: true }
```

## Forcing Tool Use

```ruby
# Force Claude to use a specific tool
client.messages.create(
  ...,
  tool_choice: { type: "tool", name: "get_weather" }
)

# Require any tool (not end_turn)
client.messages.create(
  ...,
  tool_choice: { type: "any" }
)

# Default: Claude decides
# tool_choice: { type: "auto" }
```

## Plain Hash Tool Definition

When not using typed classes, define tools as plain hashes:

```ruby
{
  name: "search_database",
  description: "Search the product database by query string",
  input_schema: {
    type: "object",
    properties: {
      query:  { type: "string",  description: "Search terms" },
      limit:  { type: "integer", description: "Max results", default: 10 },
      filter: {
        type: "string",
        enum: ["all", "in_stock", "sale"],
        description: "Filter results"
      }
    },
    required: ["query"]
  }
}
```
