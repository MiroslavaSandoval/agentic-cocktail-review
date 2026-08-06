from pydantic import ValidationError

from src.schemas.cocktail import CocktailExtraction
from src.tools.retrieve_reference_rule import retrieve_reference_rule


def validate_extraction(
    extraction: CocktailExtraction | dict,
) -> dict:
    """
    Validate schema requirements and deterministic business rules.
    """
    errors: list[dict] = []
    warnings: list[dict] = []

    try:
        if isinstance(extraction, dict):
            recipe = CocktailExtraction.model_validate(extraction)
        else:
            recipe = extraction

    except ValidationError as exc:
        return {
            "is_valid": False,
            "errors": [
                {
                    "category": "schema",
                    "message": error["msg"],
                    "location": ".".join(
                        str(item) for item in error["loc"]
                    ),
                    "is_retryable": True,
                }
                for error in exc.errors()
            ],
            "warnings": [],
        }

    rules = retrieve_reference_rule("general")

    if len(recipe.ingredients) < rules["minimum_ingredients"]:
        errors.append(
            {
                "category": "business_rule",
                "message": (
                    "The recipe contains fewer than "
                    f"{rules['minimum_ingredients']} ingredients."
                ),
                "is_retryable": True,
            }
        )

    if len(recipe.instructions) < rules["minimum_instruction_steps"]:
        errors.append(
            {
                "category": "business_rule",
                "message": "The recipe has no usable instructions.",
                "is_retryable": True,
            }
        )

    allowed_units = {
        unit.casefold() for unit in rules["allowed_units"]
    }

    for index, ingredient in enumerate(recipe.ingredients):
        if ingredient.quantity is not None and ingredient.unit is None:
            warnings.append(
                {
                    "category": "missing_value",
                    "field": f"ingredients.{index}.unit",
                    "message": (
                        f"'{ingredient.name}' has a quantity but no unit."
                    ),
                }
            )

        if (
            ingredient.unit is not None
            and ingredient.unit.casefold() not in allowed_units
        ):
            warnings.append(
                {
                    "category": "unknown_unit",
                    "field": f"ingredients.{index}.unit",
                    "message": (
                        f"Unrecognized unit: {ingredient.unit}"
                    ),
                }
            )

    if recipe.confidence < 0.75:
        warnings.append(
            {
                "category": "low_confidence",
                "field": "confidence",
                "message": (
                    f"Extraction confidence is {recipe.confidence:.2f}."
                ),
            }
        )

    return {
        "is_valid": len(errors) == 0,
        "requires_human_review": (
            len(errors) > 0
            or len(warnings) > 0
            or recipe.confidence < 0.75
        ),
        "errors": errors,
        "warnings": warnings,
    }