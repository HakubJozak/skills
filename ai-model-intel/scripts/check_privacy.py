#!/usr/bin/env python3
"""
Review privacy policies and data handling practices for AI providers.
"""

import json
import sys
from pathlib import Path

# Get script directory
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"
PRICING_FILE = REFERENCES_DIR / "pricing_data.json"


def load_pricing_data():
    """Load pricing data from JSON file"""
    if not PRICING_FILE.exists():
        print(f"Error: Pricing data not found at {PRICING_FILE}")
        print("Run: python3 fetch_pricing.py")
        sys.exit(1)

    with open(PRICING_FILE, 'r') as f:
        return json.load(f)


def score_privacy(privacy_data):
    """Score privacy practices (0-10, 10 being best)"""
    score = 0

    # No training data usage (+4 points)
    if 'not used' in privacy_data.get('training_data_usage', '').lower():
        score += 4

    # Zero retention default (+3 points)
    if 'no retention' in privacy_data.get('data_retention', '').lower() or \
       'no data retention' in privacy_data.get('zero_retention', '').lower() or \
       'default' in privacy_data.get('zero_retention', '').lower():
        score += 3
    elif 'available' in privacy_data.get('zero_retention', '').lower():
        score += 1

    # Compliance certifications (+3 points max)
    compliance = privacy_data.get('compliance', [])
    if isinstance(compliance, list):
        score += min(len(compliance), 3)

    return min(score, 10)


def print_provider_privacy(provider_name, provider_data):
    """Print privacy details for a single provider"""
    privacy = provider_data.get('privacy', {})
    score = score_privacy(privacy)

    # Privacy score visual
    filled_bars = '█' * score
    empty_bars = '░' * (10 - score)
    score_visual = f"{filled_bars}{empty_bars}"

    print(f"\n{'=' * 80}")
    print(f"{provider_name.upper()}")
    print(f"{'=' * 80}")
    print(f"Privacy Score: {score_visual} ({score}/10)")
    print()

    print(f"Training Data Usage:")
    print(f"  {privacy.get('training_data_usage', 'N/A')}")

    print(f"\nData Retention:")
    print(f"  {privacy.get('data_retention', 'N/A')}")

    print(f"\nZero Retention Option:")
    print(f"  {privacy.get('zero_retention', 'N/A')}")

    print(f"\nCompliance Certifications:")
    compliance = privacy.get('compliance', ['N/A'])
    for cert in compliance:
        print(f"  • {cert}")


def print_privacy_ranking(pricing_data):
    """Print providers ranked by privacy score"""
    print(f"\n{'=' * 80}")
    print("PRIVACY RANKING (Best to Worst)")
    print(f"{'=' * 80}")

    rankings = []
    for provider_name, provider_data in pricing_data['providers'].items():
        privacy = provider_data.get('privacy', {})
        score = score_privacy(privacy)
        rankings.append({
            'provider': provider_name,
            'score': score,
            'training': privacy.get('training_data_usage', 'N/A'),
            'retention': privacy.get('zero_retention', 'N/A')
        })

    # Sort by score (descending)
    rankings.sort(key=lambda x: x['score'], reverse=True)

    print(f"\n{'Rank':<6} {'Provider':<15} {'Score':<8} {'Training Usage':<30} {'Zero Retention'}")
    print("-" * 80)

    for i, rank in enumerate(rankings, 1):
        provider = rank['provider'].capitalize()
        score = f"{rank['score']}/10"
        training = rank['training'][:28]  # Truncate
        retention = rank['retention']

        print(f"{i:<6} {provider:<15} {score:<8} {training:<30} {retention}")


def print_recommendations():
    """Print privacy best practices and recommendations"""
    print(f"\n{'=' * 80}")
    print("PRIVACY RECOMMENDATIONS")
    print(f"{'=' * 80}")

    print("""
1. Zero Retention: Choose providers with zero data retention by default
   → Anthropic and Mistral offer this out of the box

2. Training Opt-Out: Ensure API data is not used for model training
   → OpenAI requires explicit opt-out
   → Anthropic never uses API data

3. Enterprise Agreements: Consider enterprise plans for enhanced privacy
   → Often include BAA (HIPAA), DPA (GDPR), and custom retention policies

4. Data Minimization: Send only necessary data in prompts
   → Remove PII before API calls
   → Use prompt engineering to reduce sensitive data

5. Regional Compliance: Verify provider compliance with local regulations
   → GDPR (EU), CCPA (California), LGPD (Brazil), etc.

6. Self-Hosting: For maximum control, consider open-source models
   → Llama models can be self-hosted
   → Full control over data and privacy

7. Audit Logs: Enable comprehensive logging for compliance
   → Track all API calls and data processing
   → Required for SOC2, ISO27001, HIPAA

8. Regular Reviews: Privacy policies change - review quarterly
   → Check for policy updates
   → Verify zero retention status
    """)


def print_compliance_matrix():
    """Print compliance certification matrix"""
    print(f"\n{'=' * 80}")
    print("COMPLIANCE CERTIFICATION MATRIX")
    print(f"{'=' * 80}")

    data = load_pricing_data()

    print(f"\n{'Provider':<15} {'SOC2':<8} {'HIPAA':<8} {'GDPR':<8} {'ISO27001'}")
    print("-" * 55)

    for provider_name, provider_data in sorted(data['providers'].items()):
        compliance = provider_data.get('privacy', {}).get('compliance', [])
        compliance_lower = [c.lower() for c in compliance]

        provider = provider_name.capitalize()
        soc2 = '✓' if 'soc2' in compliance_lower else '✗'
        hipaa = '✓' if 'hipaa' in compliance_lower else '✗'
        gdpr = '✓' if 'gdpr' in compliance_lower else '✗'
        iso = '✓' if 'iso27001' in compliance_lower else '✗'

        print(f"{provider:<15} {soc2:<8} {hipaa:<8} {gdpr:<8} {iso}")


def main():
    """Main function"""
    pricing_data = load_pricing_data()

    print(f"AI Provider Privacy & Data Handling Review")
    print(f"Last Updated: {pricing_data['last_updated']}")

    # Print each provider's privacy details
    for provider_name, provider_data in sorted(pricing_data['providers'].items()):
        print_provider_privacy(provider_name, provider_data)

    # Print rankings
    print_privacy_ranking(pricing_data)

    # Print compliance matrix
    print_compliance_matrix()

    # Print recommendations
    print_recommendations()

    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    main()
