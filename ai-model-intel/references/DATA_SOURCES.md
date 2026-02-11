# Data Sources and Update Schedule

## Pricing Data Sources

### OpenAI
- Official Pricing: https://openai.com/api/pricing/
- Models: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, o1 series
- Update frequency: Check monthly, update immediately on new releases

### Anthropic
- Official Pricing: https://www.anthropic.com/pricing
- Models: Claude 3 family (Opus, Sonnet, Haiku)
- Update frequency: Check monthly, update immediately on new releases

### Google
- Official Pricing: https://ai.google.dev/pricing
- Models: Gemini 1.5 Pro, Flash, Gemini 2.0
- Update frequency: Check monthly
- Note: Pricing may vary by region

### Mistral AI
- Official Pricing: https://mistral.ai/technology/#pricing
- Models: Large, Medium, Small
- Update frequency: Check monthly

### Meta (Llama)
- Via Together.ai: https://www.together.ai/pricing
- Via Replicate: https://replicate.com/pricing
- Models: Llama 3.1, 3.3 series
- Update frequency: Check monthly
- Note: Pricing varies by hosting provider

## Privacy Policy Sources

### OpenAI
- Privacy Policy: https://openai.com/policies/privacy-policy
- Terms of Use: https://openai.com/policies/terms-of-use
- API Data Usage: https://openai.com/policies/api-data-usage-policies

### Anthropic
- Privacy Policy: https://www.anthropic.com/legal/privacy
- Commercial Terms: https://www.anthropic.com/legal/commercial-terms

### Google
- Privacy Policy: https://policies.google.com/privacy
- Cloud Privacy Notice: https://cloud.google.com/terms/cloud-privacy-notice
- AI/ML Privacy: https://ai.google/responsibility/privacy/

### Mistral AI
- Privacy Policy: https://mistral.ai/terms/#privacy-policy
- Terms of Service: https://mistral.ai/terms/

### Meta
- Privacy Policy: Depends on hosting provider
- For self-hosted: Your own privacy policy applies

## Update Schedule

### Monthly Review (1st of each month)
- Check all provider pricing pages for updates
- Run `python3 scripts/fetch_pricing.py --force`
- Commit updated pricing_data.json to git

### Immediate Updates Required
- New model launches (within 24 hours)
- Pricing changes announced by providers
- Major privacy policy updates
- New compliance certifications

## Manual Updates

When updating manually, edit `scripts/fetch_pricing.py`:

1. Update model pricing in respective functions
2. Update context window sizes
3. Update capabilities lists
4. Update privacy information
5. Run script to validate JSON structure
6. Commit changes

## Validation Checklist

Before committing updates:
- [ ] All prices are per 1M tokens
- [ ] Context windows are in tokens (not characters)
- [ ] Privacy scores still make sense (run check_privacy.py)
- [ ] All models have required fields
- [ ] JSON structure is valid
- [ ] Date is updated to current

## Historical Data

Consider keeping old pricing_data.json files:
```bash
cp references/pricing_data.json references/pricing_data_2026_01.json
```

This allows tracking pricing changes over time.
