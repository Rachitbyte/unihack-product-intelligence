import logging
from app.schemas.schemas import ProductRow
from app.services.identity import identity_resolver
from app.services.retrieval import retrieval_service
from app.services.extraction import extraction_service
from app.services.normalization import normalization_service
from app.services.content_generation import content_generation_service
from app.services.digital_assets import digital_asset_service

logger = logging.getLogger(__name__)

def process_product_row(row: ProductRow) -> ProductRow:
    """
    Executes the full UPIE product intelligence pipeline on a single row.
    """
    try:
        # Phase 3: Identity
        row.identity = identity_resolver.resolve(row)
        
        # Phase 4: Retrieval
        retrieved_source = None
        if row.identity and row.identity.official_source_url and row.identity.status in ["OFFICIAL_SOURCE_FOUND", "OFFICIAL_DOCUMENT_FOUND", "OFFICIAL_SOURCE_BLOCKED"]:
            retrieved_source = retrieval_service.fetch_source(row.identity)
            
        # Assign retrieved content to row for extraction
        if retrieved_source and retrieved_source.content:
            row.retrieved_content = retrieved_source.content
        
        # Phase 5: Extraction
        if row.retrieved_content:
            row.extraction = extraction_service.extract(row)
        else:
            # Mark extraction as failed if no content
            row.extraction = None 
            
        # Phase 6: Normalization and Validation
        normalization_service.normalize(row)
        
        # Phase 7: Content Generation
        row.content = content_generation_service.generate(row)
        
        # Phase 8: Digital Assets
        if retrieved_source and retrieved_source.candidates:
            digital_asset_service.process_assets(row, retrieved_source.candidates)
            
        # Pipeline finished for this row
        return row

    except Exception as e:
        logger.error(f"Pipeline error for row {row.row_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        # If it blows up, we just return the row in whatever state it made it to
        return row
