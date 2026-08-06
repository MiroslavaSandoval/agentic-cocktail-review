import json

from src.database import get_connection
from src.schemas.cocktail import CocktailExtraction


def save_result(
    extraction: CocktailExtraction,
    validation: dict,
) -> int:
    """
    Store a completed extraction and return its database ID.
    """
    status = (
        "valid"
        if validation["is_valid"]
        and not validation["requires_human_review"]
        else "needs_review"
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO extraction_results (
                source_file,
                cocktail_name,
                extraction_json,
                validation_json,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                extraction.source_file,
                extraction.cocktail_name,
                extraction.model_dump_json(),
                json.dumps(validation),
                status,
            ),
        )

        return int(cursor.lastrowid)