import json
from pathlib import Path
from typing import Any


RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "reference_rules"
    / "cocktail_rules.json"
)


class RuleNotFoundError(Exception):
    """Raised when a requested rule does not exist."""


def retrieve_reference_rule(
    category: str,
    rule_name: str | None = None,
) -> Any:
    """
    Retrieve a cocktail validation rule.

    Examples:
        retrieve_reference_rule("general")
        retrieve_reference_rule("techniques", "shaken")
    """
    with RULES_PATH.open("r", encoding="utf-8") as file:
        rules = json.load(file)

    if category not in rules:
        raise RuleNotFoundError(
            f"Unknown rule category: {category}"
        )

    category_rules = rules[category]

    if rule_name is None:
        return category_rules

    if rule_name not in category_rules:
        raise RuleNotFoundError(
            f"Unknown rule: {category}.{rule_name}"
        )

    return category_rules[rule_name]