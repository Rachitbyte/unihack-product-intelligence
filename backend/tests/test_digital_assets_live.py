import os
from dotenv import load_dotenv
from app.schemas.schemas import ProductRow, IdentityResult, AssetCandidate
from app.services.digital_assets import digital_asset_service
from app.services.output_builder import map_to_output, load_expected_headers

load_dotenv()

def test_live_digital_assets():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Skipping live test.")
        return

    print("Running LIVE Gemini Asset Classification Test...")

    candidates = [
        # An ambiguous doc that requires Gemini
        AssetCandidate(
            url="https://www.diablotools.com/assets/doc/some-weird-doc-1234.pdf", 
            asset_type="DOCUMENT", 
            filename="some-weird-doc-1234.pdf",
            link_text="Click here to view safety info",
            alt_text="",
            source_page_url="https://www.diablotools.com"
        )
    ]

    row = ProductRow(
        row_id=1,
        mfg_part_num="DCB518ASTS06G",
        identity=IdentityResult(official_source_url="https://www.diablotools.com/products/DCB518ASTS06G")
    )

    digital_asset_service.process_assets(row, candidates)

    asset = row.asset_result.assets[0]
    print(f"URL: {asset.url}")
    print(f"Classification: {asset.classification}")
    print(f"Status: {asset.status}")

    # We just want to ensure it hit Gemini and didn't crash
    assert asset.status == "ACCEPTED" or asset.status == "NEEDS_REVIEW"

    print("Live Asset Classification Test Passed!")

if __name__ == "__main__":
    test_live_digital_assets()
