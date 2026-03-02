"""
INCI Name Resolution Pipeline

Resolves product ingredient names to chemicals in the Knowledge Graph.
Pipeline: Raw Name -> Normalize -> Exact Match -> Synonym Match -> Fuzzy Match

This is the critical bridge between product labels and the Chemical Knowledge Graph.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class NameResolver:
    """Resolve ingredient names to chemical IDs."""

    # Common suffixes/annotations to strip
    STRIP_PATTERNS = [
        r"\s*\*+\s*$",           # Organic markers (*)
        r"\s*\([^)]*%[^)]*\)",   # Concentration markers (0.24%)
        r"\s*\d+\.?\d*\s*%\s*$", # Trailing percentages
        r"\s*\(CI\s*\d+\)\s*$",  # CI color codes at end
    ]

    # Common non-ingredient tokens to skip
    SKIP_TOKENS = {
        "and", "or", "may contain", "contains", "+/-", "±",
        "ingredients:", "ingredients", "composition:",
    }

    def normalize_name(self, raw_name: str) -> str:
        """
        Normalize an ingredient name for matching.

        Steps:
        1. Strip whitespace and convert to uppercase
        2. Remove organic markers (*), concentration markers
        3. Remove parenthetical annotations
        4. Standardize spacing
        """
        name = raw_name.strip().upper()

        # Apply strip patterns
        for pattern in self.STRIP_PATTERNS:
            name = re.sub(pattern, "", name, flags=re.IGNORECASE)

        # Remove leading/trailing parentheses that wrap the whole name
        if name.startswith("(") and name.endswith(")"):
            name = name[1:-1]

        # Standardize whitespace
        name = re.sub(r"\s+", " ", name).strip()

        return name

    def parse_ingredient_list(self, raw_text: str) -> list[dict[str, Any]]:
        """
        Parse a comma-separated ingredient list into individual ingredients.

        Handles:
        - Comma separation
        - Nested parentheses: "PARFUM (FRAGRANCE)"
        - CI color codes: "CI 77891"
        - Slashes: "SODIUM C14-16 OLEFIN SULFONATE"
        """
        if not raw_text:
            return []

        ingredients = []
        # Split on commas, but not commas inside parentheses
        parts = self._split_respecting_parens(raw_text)

        for position, part in enumerate(parts, start=1):
            name = part.strip()
            if not name:
                continue

            # Skip non-ingredient tokens
            if name.lower() in self.SKIP_TOKENS:
                continue

            normalized = self.normalize_name(name)
            if not normalized:
                continue

            ingredients.append({
                "raw_name": name,
                "normalized_name": normalized,
                "position": position,
            })

        return ingredients

    def _split_respecting_parens(self, text: str) -> list[str]:
        """Split on commas, respecting parenthetical groups."""
        parts = []
        depth = 0
        current = []

        for char in text:
            if char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth = max(0, depth - 1)
                current.append(char)
            elif char == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current))

        return parts

    def resolve_batch(
        self,
        ingredients: list[dict[str, Any]],
        known_names: dict[str, str],
        known_synonyms: dict[str, str],
    ) -> list[dict[str, Any]]:
        """
        Resolve a batch of ingredients against known chemicals.

        Args:
            ingredients: List of parsed ingredients
            known_names: Dict of normalized_name -> chemical_id
            known_synonyms: Dict of synonym -> chemical_id

        Returns:
            Ingredients with chemical_id and resolution_method added.
        """
        resolved = []

        for ingredient in ingredients:
            norm = ingredient["normalized_name"]
            result = dict(ingredient)

            # Step 1: Exact match on normalized name
            if norm in known_names:
                result["chemical_id"] = known_names[norm]
                result["resolution_method"] = "exact"
                result["confidence"] = 1.0
            # Step 2: Synonym match
            elif norm in known_synonyms:
                result["chemical_id"] = known_synonyms[norm]
                result["resolution_method"] = "synonym"
                result["confidence"] = 0.95
            else:
                result["chemical_id"] = None
                result["resolution_method"] = "unresolved"
                result["confidence"] = 0.0

            resolved.append(result)

        return resolved
