import argparse
import json
import logging

from src.database import initialize_database
from src.tools.extract_document_fields import extract_document_fields
from src.tools.load_document import load_document
from src.tools.save_result import save_result
from src.tools.submit_for_human_review import submit_for_human_review
from src.tools.validate_extraction import validate_extraction


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def process_cocktail(file_path: str) -> dict:
    """
    Coordinate the complete cocktail extraction workflow.
    """
    logger.info("Loading %s", file_path)
    document = load_document(file_path)

    logger.info("Extracting cocktail fields")
    extraction = extract_document_fields(document)

    logger.info("Validating extraction")
    validation = validate_extraction(extraction)

    result_id = save_result(extraction, validation)

    review_id: int | None = None

    if validation["requires_human_review"]:
        reasons = [
            item["message"]
            for item in validation["errors"] + validation["warnings"]
        ]

        review_id = submit_for_human_review(
            extraction=extraction,
            validation=validation,
            reason="; ".join(reasons),
        )

        logger.warning(
            "Sent extraction to human review: %s",
            review_id,
        )
    else:
        logger.info("Extraction passed automatic validation")

    return {
        "result_id": result_id,
        "review_id": review_id,
        "extraction": extraction.model_dump(),
        "validation": validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", help="Path to a cocktail PDF")
    args = parser.parse_args()

    initialize_database()
    result = process_cocktail(args.pdf_path)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()