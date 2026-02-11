#!/usr/bin/env python3
"""
Estimate monthly AI API costs based on user base and usage patterns.
"""

import argparse
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


def find_model(pricing_data, model_name):
    """Find model pricing by name"""
    model_name_lower = model_name.lower()

    for provider_name, provider_data in pricing_data['providers'].items():
        for model, data in provider_data['models'].items():
            if model.lower() == model_name_lower or model_name_lower in model.lower():
                return {
                    'provider': provider_name,
                    'model': model,
                    **data
                }

    return None


def calculate_cost(model_data, users, requests_per_user, avg_input_tokens, avg_output_tokens):
    """Calculate monthly cost for given usage pattern"""
    # Total monthly requests
    total_requests = users * requests_per_user

    # Total tokens per month
    total_input_tokens = total_requests * avg_input_tokens
    total_output_tokens = total_requests * avg_output_tokens

    # Convert to millions
    input_millions = total_input_tokens / 1_000_000
    output_millions = total_output_tokens / 1_000_000

    # Calculate costs
    input_cost = input_millions * model_data['input_price_per_1m']
    output_cost = output_millions * model_data['output_price_per_1m']
    total_cost = input_cost + output_cost

    # Cost per user
    cost_per_user = total_cost / users if users > 0 else 0

    return {
        'total_requests': total_requests,
        'total_input_tokens': total_input_tokens,
        'total_output_tokens': total_output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
        'cost_per_user': cost_per_user
    }


def format_number(num):
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    return f"{num:.0f}"


def print_estimate(model_data, usage_params, costs):
    """Print cost estimate in a formatted way"""
    print(f"\n{'=' * 80}")
    print(f"COST ESTIMATE: {model_data['model']} ({model_data['provider'].upper()})")
    print(f"{'=' * 80}")

    print(f"\nUsage Parameters:")
    print(f"  • Users: {format_number(usage_params['users'])}")
    print(f"  • Requests per user: {usage_params['requests_per_user']}")
    print(f"  • Avg input tokens: {usage_params['avg_input_tokens']}")
    print(f"  • Avg output tokens: {usage_params['avg_output_tokens']}")

    print(f"\nMonthly Volume:")
    print(f"  • Total requests: {format_number(costs['total_requests'])}")
    print(f"  • Total input tokens: {format_number(costs['total_input_tokens'])}")
    print(f"  • Total output tokens: {format_number(costs['total_output_tokens'])}")

    print(f"\nMonthly Costs:")
    print(f"  • Input cost: ${costs['input_cost']:,.2f}")
    print(f"  • Output cost: ${costs['output_cost']:,.2f}")
    print(f"  • Total cost: ${costs['total_cost']:,.2f}")
    print(f"  • Cost per user: ${costs['cost_per_user']:.4f}")

    print(f"\nAnnual Projection:")
    print(f"  • Annual cost: ${costs['total_cost'] * 12:,.2f}")


def compare_models(pricing_data, usage_params, top_n=5):
    """Compare costs across different models"""
    print(f"\n{'=' * 80}")
    print(f"MODEL COMPARISON (Top {top_n} Cheapest)")
    print(f"{'=' * 80}")

    results = []

    for provider_name, provider_data in pricing_data['providers'].items():
        for model_name, model_data in provider_data['models'].items():
            model_info = {
                'provider': provider_name,
                'model': model_name,
                **model_data
            }

            costs = calculate_cost(
                model_info,
                usage_params['users'],
                usage_params['requests_per_user'],
                usage_params['avg_input_tokens'],
                usage_params['avg_output_tokens']
            )

            results.append({
                'provider': provider_name,
                'model': model_name,
                'total_cost': costs['total_cost'],
                'cost_per_user': costs['cost_per_user']
            })

    # Sort by total cost
    results.sort(key=lambda x: x['total_cost'])

    print(f"\n{'Provider':<15} {'Model':<30} {'Monthly Cost':<15} {'Per User'}")
    print("-" * 80)

    for result in results[:top_n]:
        provider = result['provider'].capitalize()
        model = result['model']
        total = f"${result['total_cost']:,.2f}"
        per_user = f"${result['cost_per_user']:.4f}"

        print(f"{provider:<15} {model:<30} {total:<15} {per_user}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Estimate monthly AI API costs"
    )
    parser.add_argument('--users', type=int, required=True, help='Number of users')
    parser.add_argument('--requests-per-user', type=int, required=True, help='Requests per user per month')
    parser.add_argument('--avg-input-tokens', type=int, required=True, help='Average input tokens per request')
    parser.add_argument('--avg-output-tokens', type=int, required=True, help='Average output tokens per request')
    parser.add_argument('--model', type=str, help='Specific model to estimate (optional)')
    parser.add_argument('--compare', action='store_true', help='Compare across all models')

    args = parser.parse_args()

    pricing_data = load_pricing_data()

    usage_params = {
        'users': args.users,
        'requests_per_user': args.requests_per_user,
        'avg_input_tokens': args.avg_input_tokens,
        'avg_output_tokens': args.avg_output_tokens
    }

    if args.model:
        # Specific model estimate
        model_data = find_model(pricing_data, args.model)

        if not model_data:
            print(f"Error: Model '{args.model}' not found")
            print("\nRun 'python3 view_pricing.py' to see available models")
            sys.exit(1)

        costs = calculate_cost(model_data, **usage_params)
        print_estimate(model_data, usage_params, costs)

    if args.compare or not args.model:
        # Compare across models
        compare_models(pricing_data, usage_params)

    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    main()
