from src.schemas.cocktail import CocktailExtraction, Ingredient
from src.tools.validate_extraction import validate_extraction


def test_valid_recipe_passes_validation():
    recipe = CocktailExtraction(
        cocktail_name="Test Daiquiri",
        ingredients=[
            Ingredient(
                name="Rum",
                quantity=2,
                unit="oz",
            ),
            Ingredient(
                name="Lime juice",
                quantity=1,
                unit="oz",
            ),
            Ingredient(
                name="Simple syrup",
                quantity=0.75,
                unit="oz",
            ),
        ],
        instructions=[
            "Shake all ingredients with ice.",
            "Strain into a chilled glass.",
        ],
        glassware="Coupe",
        garnish=None,
        technique="shaken",
        source_file="test.pdf",
        confidence=0.95,
    )

    result = validate_extraction(recipe)

    assert result["is_valid"] is True
    assert result["requires_human_review"] is False


def test_low_confidence_requires_review():
    recipe = CocktailExtraction(
        cocktail_name="Uncertain Cocktail",
        ingredients=[
            Ingredient(name="Rum", quantity=2, unit="oz"),
            Ingredient(name="Juice", quantity=None, unit=None),
        ],
        instructions=["Mix ingredients."],
        source_file="uncertain.pdf",
        confidence=0.50,
    )

    result = validate_extraction(recipe)

    assert result["is_valid"] is True
    assert result["requires_human_review"] is True