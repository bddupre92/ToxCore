"""Tests for the INCI name resolution pipeline."""

import sys
from pathlib import Path

# Add data directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "data"))

from etl.name_resolution.build_mapping import NameResolver


def test_normalize_basic():
    resolver = NameResolver()
    assert resolver.normalize_name("  sodium lauryl sulfate  ") == "SODIUM LAURYL SULFATE"
    assert resolver.normalize_name("aqua") == "AQUA"
    assert resolver.normalize_name("GLYCERIN") == "GLYCERIN"


def test_normalize_strips_organic_markers():
    resolver = NameResolver()
    assert resolver.normalize_name("ALOE BARBADENSIS LEAF JUICE*") == "ALOE BARBADENSIS LEAF JUICE"
    assert resolver.normalize_name("GLYCERIN**") == "GLYCERIN"


def test_normalize_strips_concentrations():
    resolver = NameResolver()
    assert resolver.normalize_name("SODIUM FLUORIDE (0.24%)") == "SODIUM FLUORIDE"


def test_parse_simple_list():
    resolver = NameResolver()
    ingredients = resolver.parse_ingredient_list("AQUA, GLYCERIN, SODIUM LAURYL SULFATE")
    assert len(ingredients) == 3
    assert ingredients[0]["normalized_name"] == "AQUA"
    assert ingredients[0]["position"] == 1
    assert ingredients[2]["normalized_name"] == "SODIUM LAURYL SULFATE"
    assert ingredients[2]["position"] == 3


def test_parse_nested_parentheses():
    resolver = NameResolver()
    ingredients = resolver.parse_ingredient_list(
        "AQUA, PARFUM (FRAGRANCE), GLYCERIN"
    )
    assert len(ingredients) == 3
    assert "PARFUM (FRAGRANCE)" in ingredients[1]["raw_name"]


def test_parse_empty():
    resolver = NameResolver()
    assert resolver.parse_ingredient_list("") == []
    assert resolver.parse_ingredient_list("   ") == []


def test_resolve_exact_match():
    resolver = NameResolver()
    ingredients = [
        {"normalized_name": "AQUA", "raw_name": "Aqua", "position": 1},
        {"normalized_name": "GLYCERIN", "raw_name": "Glycerin", "position": 2},
    ]
    known_names = {"AQUA": "chem-water", "GLYCERIN": "chem-glycerin"}

    resolved = resolver.resolve_batch(ingredients, known_names, {})
    assert resolved[0]["chemical_id"] == "chem-water"
    assert resolved[0]["resolution_method"] == "exact"
    assert resolved[0]["confidence"] == 1.0


def test_resolve_synonym_match():
    resolver = NameResolver()
    ingredients = [
        {"normalized_name": "WATER", "raw_name": "Water", "position": 1},
    ]
    known_names = {"AQUA": "chem-water"}
    known_synonyms = {"WATER": "chem-water"}

    resolved = resolver.resolve_batch(ingredients, known_names, known_synonyms)
    assert resolved[0]["chemical_id"] == "chem-water"
    assert resolved[0]["resolution_method"] == "synonym"
    assert resolved[0]["confidence"] == 0.95


def test_resolve_unresolved():
    resolver = NameResolver()
    ingredients = [
        {"normalized_name": "UNKNOWN_INGREDIENT_XYZ", "raw_name": "Unknown", "position": 1},
    ]

    resolved = resolver.resolve_batch(ingredients, {}, {})
    assert resolved[0]["chemical_id"] is None
    assert resolved[0]["resolution_method"] == "unresolved"
    assert resolved[0]["confidence"] == 0.0


def test_resolve_mixed():
    resolver = NameResolver()
    ingredients = [
        {"normalized_name": "AQUA", "raw_name": "Aqua", "position": 1},
        {"normalized_name": "PARFUM", "raw_name": "Parfum", "position": 2},
        {"normalized_name": "UNKNOWN", "raw_name": "Unknown", "position": 3},
    ]
    known_names = {"AQUA": "chem-water"}
    known_synonyms = {"PARFUM": "chem-fragrance"}

    resolved = resolver.resolve_batch(ingredients, known_names, known_synonyms)
    assert resolved[0]["resolution_method"] == "exact"
    assert resolved[1]["resolution_method"] == "synonym"
    assert resolved[2]["resolution_method"] == "unresolved"
