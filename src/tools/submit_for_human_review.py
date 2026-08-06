import json

from src.database import get_connection
from src.schemas.cocktail import CocktailExtraction


def submit_for_human_review(
    extraction: CocktailExtraction,
    validation: dict,
    reason: str,
) -> int:
    """
    Add an extraction to the human-review queue.
    """
    if not reason.strip():
        raise ValueError("A human-review reason is required.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO human_review_queue (
                source_file,
                extraction_json,
                validation_json,
                reason
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                extraction.source_file,
                extraction.model_dump_json(),
                json.dumps(validation),
                reason,
            ),
        )

        return int(cursor.lastrowid)