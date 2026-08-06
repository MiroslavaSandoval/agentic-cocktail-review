import json
import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

from src.schemas.cocktail import CocktailExtraction

load_dotenv()


class ExtractionError(Exception):
    """Raised when structured extraction fails."""


EXTRACTION_TOOL: dict[str, Any] = {
    "name": "record_cocktail_recipe",
    "description": (
        "Extract one cocktail recipe from the provided document. "
        "Use only information explicitly present in the source. "
        "Return null when an optional value is absent. "
        "Do not invent quantities, units, glassware, garnishes or techniques."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "cocktail_name": {"type": "string"},
            "ingredients": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "quantity": {
                            "type": ["number", "null"]
                        },
                        "unit": {
                            "type": ["string", "null"]
                        },
                        "preparation": {
                            "type": ["string", "null"]
                        },
                    },
                    "required": [
                        "name",
                        "quantity",
                        "unit",
                        "preparation",
                    ],
                    "additionalProperties": False,
                },
            },
            "instructions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "glassware": {"type": ["string", "null"]},
            "garnish": {"type": ["string", "null"]},
            "technique": {"type": ["string", "null"]},
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
        },
        "required": [
            "cocktail_name",
            "ingredients",
            "instructions",
            "glassware",
            "garnish",
            "technique",
            "confidence",
        ],
        "additionalProperties": False,
    },
}


def extract_document_fields(
    document: dict,
    *,
    model: str | None = None,
) -> CocktailExtraction:
    """
    Extract structured cocktail fields from loaded document text.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ExtractionError(
            "ANTHROPIC_API_KEY is missing from the environment."
        )

    selected_model = model or os.getenv("ANTHROPIC_MODEL")

    if not selected_model:
        raise ExtractionError(
            "ANTHROPIC_MODEL is missing from the environment."
        )

    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=selected_model,
        max_tokens=2000,
        tools=[EXTRACTION_TOOL],
        tool_choice={
            "type": "tool",
            "name": "record_cocktail_recipe",
        },
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract the cocktail recipe from this document.\n\n"
                    f"Source filename: {document['file_name']}\n\n"
                    f"Document:\n{document['text']}"
                ),
            }
        ],
    )

    tool_blocks = [
        block
        for block in response.content
        if block.type == "tool_use"
        and block.name == "record_cocktail_recipe"
    ]

    if not tool_blocks:
        raise ExtractionError(
            f"Claude did not return the extraction tool. "
            f"stop_reason={response.stop_reason}"
        )

    extracted_data = tool_blocks[0].input
    extracted_data["source_file"] = document["file_name"]

    try:
        return CocktailExtraction.model_validate(extracted_data)
    except Exception as exc:
        formatted = json.dumps(extracted_data, indent=2)
        raise ExtractionError(
            f"Extracted data failed validation:\n{formatted}\n\n{exc}"
        ) from exc