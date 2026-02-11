#!/usr/bin/env python3
"""
View AI model pricing data in formatted tables.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

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


def format_price(price):
    """Format price for display"""
    return f"${price:.2f}"


def format_context(tokens):
    """Format context window for display"""
    if tokens >= 1_000_000:
        return f"{tokens/1_000_000:.1f}M"
    elif tokens >= 1000:
        return f"{tokens/1000:.0f}K"
    return str(tokens)


def print_provider_pricing(provider_name, provider_data):
    """Print pricing for a single provider"""
    print(f"\n{'=' * 100}")
    print(f"{provider_name.upper()}")
    print(f"{'=' * 100}")

    # Header
    print(f"{'Model':<30} {'Input/1M':<12} {'Output/1M':<12} {'Context':<10} {'Capabilities'}")
    print("-" * 100)

    # Models
    for model_name, model_data in sorted(provider_data['models'].items()):
        input_price = format_price(model_data['input_price_per_1m'])
        output_price = format_price(model_data['output_price_per_1m'])
        context = format_context(model_data['context_window'])
        capabilities = ', '.join(model_data.get('capabilities', [])[:3])  # First 3

        print(f"{model_name:<30} {input_price:<12} {output_price:<12} {context:<10} {capabilities}")

    # Privacy info
    print(f"\nPrivacy & Data Handling:")
    privacy = provider_data.get('privacy', {})
    print(f"  • Training data usage: {privacy.get('training_data_usage', 'N/A')}")
    print(f"  • Data retention: {privacy.get('data_retention', 'N/A')}")
    print(f"  • Zero retention: {privacy.get('zero_retention', 'N/A')}")
    print(f"  • Compliance: {', '.join(privacy.get('compliance', ['N/A']))}")


def print_comparison_table(pricing_data):
    """Print comparison of cheapest models"""
    print(f"\n{'=' * 100}")
    print("COST COMPARISON (Cheapest Options)")
    print(f"{'=' * 100}")

    models = []
    for provider_name, provider_data in pricing_data['providers'].items():
        for model_name, model_data in provider_data['models'].items():
            models.append({
                'provider': provider_name,
                'model': model_name,
                'input': model_data['input_price_per_1m'],
                'output': model_data['output_price_per_1m'],
                'context': model_data['context_window']
            })

    # Sort by total cost (assuming equal input/output usage)
    models.sort(key=lambda x: x['input'] + x['output'])

    print(f"{'Provider':<15} {'Model':<30} {'Input/1M':<12} {'Output/1M':<12} {'Context'}")
    print("-" * 100)

    for model in models[:10]:  # Top 10 cheapest
        provider = model['provider'].capitalize()
        model_name = model['model']
        input_price = format_price(model['input'])
        output_price = format_price(model['output'])
        context = format_context(model['context'])

        print(f"{provider:<15} {model_name:<30} {input_price:<12} {output_price:<12} {context}")


def print_premium_models(pricing_data):
    """Print most expensive/premium models"""
    print(f"\n{'=' * 100}")
    print("PREMIUM MODELS (Highest Performance)")
    print(f"{'=' * 100}")

    models = []
    for provider_name, provider_data in pricing_data['providers'].items():
        for model_name, model_data in provider_data['models'].items():
            # Filter for premium (typically > $10 input)
            if model_data['input_price_per_1m'] >= 10.0:
                models.append({
                    'provider': provider_name,
                    'model': model_name,
                    'input': model_data['input_price_per_1m'],
                    'output': model_data['output_price_per_1m'],
                    'context': model_data['context_window'],
                    'capabilities': model_data.get('capabilities', [])
                })

    # Sort by input price (descending)
    models.sort(key=lambda x: x['input'], reverse=True)

    print(f"{'Provider':<15} {'Model':<30} {'Input/1M':<12} {'Output/1M':<12} {'Capabilities'}")
    print("-" * 100)

    for model in models:
        provider = model['provider'].capitalize()
        model_name = model['model']
        input_price = format_price(model['input'])
        output_price = format_price(model['output'])
        capabilities = ', '.join(model['capabilities'][:4])

        print(f"{provider:<15} {model_name:<30} {input_price:<12} {output_price:<12} {capabilities}")


def main():
    """Main function"""
    pricing_data = load_pricing_data()

    print(f"AI Model Pricing Report")
    print(f"Last Updated: {pricing_data['last_updated']}")

    # Print each provider
    for provider_name, provider_data in sorted(pricing_data['providers'].items()):
        print_provider_pricing(provider_name, provider_data)

    # Print comparison tables
    print_comparison_table(pricing_data)
    print_premium_models(pricing_data)

    print(f"\n{'=' * 100}")


if __name__ == "__main__":
    main()
