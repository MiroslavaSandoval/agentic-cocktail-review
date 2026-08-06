from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    name: str = Field(min_length=1)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = None
    preparation: str | None = None


class CocktailExtraction(BaseModel):
    cocktail_name: str = Field(min_length=1)
    ingredients: list[Ingredient] = Field(min_length=1)
    instructions: list[str] = Field(min_length=1)

    glassware: str | None = None
    garnish: str | None = None
    technique: str | None = None

    source_file: str
    confidence: float = Field(ge=0, le=1)