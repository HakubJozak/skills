# Usage Examples

## Quick Start

### 1. Initial Setup
```bash
# Fetch latest pricing data
python3 ~/skills/ai-model-intel/scripts/fetch_pricing.py

# Or use the launcher
~/skills/ai-model-intel/scripts/ai-intel update
```

### 2. View All Pricing
```bash
# View comprehensive pricing report
~/skills/ai-model-intel/scripts/ai-intel pricing
```

## Cost Estimation Scenarios

### Startup (Small Scale)
**Scenario:** MVP with 500 active users, light usage
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 500 \
  --requests-per-user 20 \
  --avg-input-tokens 400 \
  --avg-output-tokens 150 \
  --compare

# Expected monthly cost range: $20-$500 depending on model
```

### Growing SaaS (Medium Scale)
**Scenario:** Product-market fit, 5000 users, moderate usage
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 5000 \
  --requests-per-user 50 \
  --avg-input-tokens 600 \
  --avg-output-tokens 250 \
  --compare

# Expected monthly cost range: $100-$2000 depending on model
```

### Enterprise (Large Scale)
**Scenario:** Established product, 50000 users, heavy usage
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 50000 \
  --requests-per-user 100 \
  --avg-input-tokens 800 \
  --avg-output-tokens 400 \
  --compare

# Expected monthly cost range: $2000-$30000 depending on model
```

### Chatbot/Assistant
**Scenario:** Customer support chatbot, high interaction rate
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 10000 \
  --requests-per-user 200 \
  --avg-input-tokens 300 \
  --avg-output-tokens 150 \
  --model "gpt-3.5-turbo"

# Chatbots typically have:
# - High request volume per user
# - Lower token counts per request
# - Need for fast responses (favor cheaper models)
```

### Code Assistant
**Scenario:** Developer tool, code generation/review
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 1000 \
  --requests-per-user 30 \
  --avg-input-tokens 2000 \
  --avg-output-tokens 800 \
  --model "claude-sonnet-4-5"

# Code assistants typically have:
# - Lower request volume
# - High token counts (context + generated code)
# - Need for high quality (favor premium models)
```

### Content Generation
**Scenario:** Blog post/article generation tool
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 2000 \
  --requests-per-user 10 \
  --avg-input-tokens 500 \
  --avg-output-tokens 1500 \
  --model "gpt-4-turbo"

# Content generation typically has:
# - Very low request volume
# - High output token counts
# - Quality matters (favor premium models)
```

## Privacy Analysis

### Check All Providers
```bash
~/skills/ai-model-intel/scripts/ai-intel privacy
```

### Privacy Priorities by Use Case

**Healthcare/Medical:**
- MUST use providers with HIPAA compliance
- Anthropic Claude or OpenAI Enterprise recommended
- Zero data retention is critical

**Financial Services:**
- Need SOC2 Type II compliance
- Consider self-hosted Llama for sensitive data
- Review data residency requirements

**EU Users:**
- GDPR compliance required
- Check data processing locations
- Consider European providers or self-hosting

**General SaaS:**
- SOC2 recommended
- Zero retention preferred
- Compare based on use case

## Cost Optimization Strategies

### Strategy 1: Model Tiering
Use cheap models for simple tasks, premium for complex:
```bash
# Simple tasks (classification, extraction)
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 10000 \
  --requests-per-user 100 \
  --avg-input-tokens 200 \
  --avg-output-tokens 50 \
  --model "gpt-3.5-turbo"

# Complex tasks (analysis, generation)
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 10000 \
  --requests-per-user 20 \
  --avg-input-tokens 800 \
  --avg-output-tokens 400 \
  --model "gpt-4-turbo"
```

### Strategy 2: Aggressive Caching
Cache common responses to reduce API calls:
```bash
# Without caching
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 10000 \
  --requests-per-user 100 \
  --avg-input-tokens 500 \
  --avg-output-tokens 200

# With 70% cache hit rate (30% actual API calls)
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 10000 \
  --requests-per-user 30 \
  --avg-input-tokens 500 \
  --avg-output-tokens 200

# Savings: ~70% reduction in costs
```

### Strategy 3: Prompt Optimization
Reduce token usage through better prompts:
```bash
# Before optimization (verbose instructions)
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 5000 \
  --requests-per-user 50 \
  --avg-input-tokens 1000 \
  --avg-output-tokens 300

# After optimization (concise instructions)
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 5000 \
  --requests-per-user 50 \
  --avg-input-tokens 400 \
  --avg-output-tokens 300

# Savings: ~40% reduction in input costs
```

## Budget Planning

### Monthly Budget: $500
```bash
# Find best model mix for $500/month
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 3000 \
  --requests-per-user 40 \
  --avg-input-tokens 500 \
  --avg-output-tokens 200 \
  --compare

# Look for models in $300-500 range to leave buffer
```

### Monthly Budget: $2000
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 10000 \
  --requests-per-user 50 \
  --avg-input-tokens 600 \
  --avg-output-tokens 250 \
  --compare

# Can afford premium models with this budget
```

### Monthly Budget: $10000
```bash
~/skills/ai-model-intel/scripts/ai-intel estimate \
  --users 50000 \
  --requests-per-user 60 \
  --avg-input-tokens 700 \
  --avg-output-tokens 300 \
  --compare

# Can serve large user base with premium models
```

## Monitoring and Adjustment

### Monthly Review Checklist
1. Update pricing data:
   ```bash
   ~/skills/ai-model-intel/scripts/ai-intel update
   ```

2. Compare actual vs estimated usage:
   - Get actual metrics from your API logs
   - Re-run estimates with real numbers
   - Adjust projections

3. Check for new models:
   ```bash
   ~/skills/ai-model-intel/scripts/ai-intel pricing | grep "Last Updated"
   ```

4. Review privacy compliance:
   ```bash
   ~/skills/ai-model-intel/scripts/ai-intel privacy
   ```

### Scaling Triggers
When to re-evaluate your model choice:
- 2x increase in users
- Change in usage patterns
- New model releases
- Budget constraints
- Privacy requirement changes
- Performance issues
