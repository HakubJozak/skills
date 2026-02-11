---
name: ai-model-intel
description: "Report current capabilities and costs of major AI models (OpenAI, Anthropic, Google, Meta, Mistral). Use when you need to compare AI models, estimate API costs, check token pricing, analyze privacy policies, or calculate monthly run costs based on user base and model usage patterns."
allowed-tools:
  - Bash
  - Read
  - WebFetch
---

# AI Model Intelligence

Report on current capabilities, token pricing, privacy agreements, and cost estimates for major AI model providers.

## When to Use This Skill

- Compare capabilities across different AI models
- Get latest token pricing for API usage
- Estimate monthly costs based on user base and usage patterns
- Review privacy policies and data handling practices
- Plan AI infrastructure budget

## Quick Start

### 1. Update Pricing Data

```bash
python3 ~/skills/ai-model-intel/scripts/fetch_pricing.py
```

This fetches current pricing from:
- OpenAI (GPT-4, GPT-3.5, embeddings)
- Anthropic (Claude 3 family)
- Google (Gemini models)
- Mistral AI
- Meta (Llama via various providers)

Data is saved to `~/skills/ai-model-intel/references/pricing_data.json`

### 2. View Current Pricing

```bash
python3 ~/skills/ai-model-intel/scripts/view_pricing.py
```

Displays formatted pricing table with:
- Model name and provider
- Input token cost (per 1M tokens)
- Output token cost (per 1M tokens)
- Context window size
- Special capabilities

### 3. Estimate Monthly Costs

```bash
python3 ~/skills/ai-model-intel/scripts/estimate_costs.py \
  --users 1000 \
  --requests-per-user 50 \
  --avg-input-tokens 500 \
  --avg-output-tokens 200 \
  --model "gpt-4-turbo"
```

Calculates:
- Total monthly tokens (input + output)
- Cost per user
- Total monthly cost
- Cost comparison across models

### 4. Check Privacy Policies

```bash
python3 ~/skills/ai-model-intel/scripts/check_privacy.py
```

Reviews and summarizes:
- Data retention policies
- Training data usage
- Zero data retention options
- Enterprise vs API differences
- GDPR/compliance status

## Cost Estimation Examples

### Small SaaS (1K users, light usage)
```bash
python3 ~/skills/ai-model-intel/scripts/estimate_costs.py \
  --users 1000 \
  --requests-per-user 20 \
  --avg-input-tokens 300 \
  --avg-output-tokens 150
```

### Medium SaaS (10K users, moderate usage)
```bash
python3 ~/skills/ai-model-intel/scripts/estimate_costs.py \
  --users 10000 \
  --requests-per-user 50 \
  --avg-input-tokens 500 \
  --avg-output-tokens 200
```

### High-Volume API (100K users, heavy usage)
```bash
python3 ~/skills/ai-model-intel/scripts/estimate_costs.py \
  --users 100000 \
  --requests-per-user 100 \
  --avg-input-tokens 800 \
  --avg-output-tokens 400
```

## Model Capabilities Overview

The skill tracks these key capabilities:
- **Context Window**: Maximum tokens (input + output)
- **Function Calling**: Native tool/function calling support
- **Vision**: Image understanding capabilities
- **JSON Mode**: Structured output guarantees
- **Streaming**: Real-time response streaming
- **Fine-tuning**: Custom model training availability

## Privacy & Data Handling

Key considerations tracked:
1. **Training Data Usage**: Does the provider use API data for training?
2. **Data Retention**: How long is data stored?
3. **Zero Retention**: Options to opt out of data storage
4. **Enterprise Plans**: Enhanced privacy guarantees
5. **Compliance**: GDPR, HIPAA, SOC2 status

## Pricing Data Structure

The `pricing_data.json` file contains:
```json
{
  "last_updated": "2026-01-26",
  "providers": {
    "openai": {
      "models": {
        "gpt-4-turbo": {
          "input_price_per_1m": 10.00,
          "output_price_per_1m": 30.00,
          "context_window": 128000,
          "capabilities": ["function_calling", "vision", "json_mode"]
        }
      }
    }
  }
}
```

## Maintenance

Update pricing data monthly or when new models launch:
```bash
python3 ~/skills/ai-model-intel/scripts/fetch_pricing.py --force
```

The `--force` flag bypasses cache and fetches fresh data from all providers.

## Tips

1. **Compare apples to apples**: Use same input/output token counts across models
2. **Account for retries**: Add 10-20% buffer for failed requests and retries
3. **Monitor actual usage**: Start with estimates, refine with real metrics
4. **Consider caching**: Aggressive caching can reduce costs by 50-80%
5. **Mix models**: Use cheaper models for simple tasks, premium for complex ones
