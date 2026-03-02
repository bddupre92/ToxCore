"""
Storage estimation script for ToxScore database.
Projects the total database size for different data volumes
against the 500MB Supabase free tier limit.
"""


def estimate_storage(
    num_chemicals: int = 10_000,
    num_synonyms_per_chemical: int = 10,
    num_regulatory_entries: int = 15_000,
    num_products: int = 50_000,
    avg_ingredients_per_product: int = 15,
    num_ai_explanations: int = 5_000,
    num_name_mappings: int = 30_000,
) -> dict[str, float]:
    """Estimate storage in MB for each table and total."""

    estimates: dict[str, float] = {}

    # Chemicals: ~1KB per row (UUID + text fields + JSONB + tsvector)
    estimates["chemicals"] = num_chemicals * 1.0 / 1024  # MB

    # Chemical synonyms: ~100B per row
    num_synonyms = num_chemicals * num_synonyms_per_chemical
    estimates["chemical_synonyms"] = num_synonyms * 0.1 / 1024

    # Regulatory lists: negligible (~10 rows)
    estimates["regulatory_lists"] = 0.01

    # Chemical regulatory status: ~200B per row
    estimates["chemical_regulatory_status"] = num_regulatory_entries * 0.2 / 1024

    # Products: ~1.5KB per row (includes raw_ingredients text + tsvector)
    estimates["products"] = num_products * 1.5 / 1024

    # Product ingredients: ~150B per row
    num_ingredients = num_products * avg_ingredients_per_product
    # Deduplication reduces this by ~40%
    effective_ingredients = int(num_ingredients * 0.6)
    estimates["product_ingredients"] = effective_ingredients * 0.15 / 1024

    # Product scores: ~500B per row (includes JSONB details)
    estimates["product_scores"] = num_products * 0.5 / 1024

    # Name mappings: ~200B per row
    estimates["name_mappings"] = num_name_mappings * 0.2 / 1024

    # AI explanations: ~2KB per row (includes full text content)
    estimates["ai_explanations"] = num_ai_explanations * 2.0 / 1024

    # Indexes: roughly 30-40% of data size
    data_total = sum(estimates.values())
    estimates["indexes"] = data_total * 0.35

    # System overhead: ~30MB
    estimates["system_overhead"] = 30.0

    return estimates


def print_report(estimates: dict[str, float]) -> None:
    total = sum(estimates.values())
    limit = 500.0

    print("=" * 60)
    print("ToxScore Database Storage Estimate")
    print("=" * 60)
    print()
    print(f"{'Table':<35} {'Size (MB)':>10}")
    print("-" * 47)

    for table, size_mb in sorted(estimates.items(), key=lambda x: -x[1]):
        print(f"  {table:<33} {size_mb:>8.1f} MB")

    print("-" * 47)
    print(f"  {'TOTAL':<33} {total:>8.1f} MB")
    print()
    print(f"  Supabase Free Tier Limit:          {limit:.0f} MB")
    print(f"  Headroom:                          {limit - total:.1f} MB")
    print(f"  Usage:                             {total / limit * 100:.1f}%")
    print()

    if total > limit:
        print("  WARNING: Projected size exceeds free tier limit!")
    elif total > limit * 0.8:
        print("  CAUTION: Approaching free tier limit (>80%).")
    else:
        print("  OK: Comfortable headroom available.")
    print()


if __name__ == "__main__":
    print("\n--- Default Estimates (50K products, 10K chemicals) ---")
    estimates = estimate_storage()
    print_report(estimates)

    print("\n--- Conservative Estimates (30K products, 8K chemicals) ---")
    estimates = estimate_storage(
        num_chemicals=8_000,
        num_products=30_000,
        num_ai_explanations=3_000,
        num_name_mappings=20_000,
    )
    print_report(estimates)

    print("\n--- High Estimates (80K products, 15K chemicals) ---")
    estimates = estimate_storage(
        num_chemicals=15_000,
        num_products=80_000,
        num_ai_explanations=10_000,
        num_name_mappings=50_000,
    )
    print_report(estimates)
