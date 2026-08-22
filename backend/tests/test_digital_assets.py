from unittest.mock import patch, MagicMock
from app.schemas.schemas import ProductRow, IdentityResult, AssetCandidate, DigitalAsset, AssetResult
from app.services.digital_assets import digital_asset_service
from app.services.output_builder import map_to_output, load_expected_headers

def test_digital_assets_processing():
    print("Testing Digital Assets Processing...")

    # Set up candidate assets
    candidates = [
        # Image extraction, filename classification, official domain
        AssetCandidate(url="https://official.com/img1.jpg", asset_type="IMAGE", filename="img1.jpg", source_page_url="https://official.com"),
        # Primary vs alternate image assignment
        AssetCandidate(url="https://official.com/img2.jpg", asset_type="IMAGE", filename="img2.jpg", source_page_url="https://official.com"),
        # PDF link extraction, classification using link text
        AssetCandidate(url="https://official.com/doc.pdf", asset_type="DOCUMENT", link_text="Safety Data Sheet", source_page_url="https://official.com"),
        # Non-extension PDF URL using Content-Type
        AssetCandidate(url="https://official.com/download/123", asset_type="DOCUMENT", link_text="Specifications", source_page_url="https://official.com"),
        # Third-party asset rejection
        AssetCandidate(url="https://amazon.com/img.jpg", asset_type="IMAGE", filename="img.jpg", source_page_url="https://official.com"),
        # Duplicate asset URLs
        AssetCandidate(url="https://official.com/img1.jpg", asset_type="IMAGE", filename="img1.jpg", source_page_url="https://official.com"),
        # Ambiguous asset classification (will fallback to Gemini)
        AssetCandidate(url="https://official.com/weird.pdf", asset_type="DOCUMENT", filename="weird.pdf", link_text="weird doc", source_page_url="https://official.com")
    ]

    row = ProductRow(
        row_id=1,
        mfg_part_num="TEST-MPN",
        identity=IdentityResult(official_source_url="https://official.com/product/123")
    )

    # We patch _fetch_content_type and Gemini
    def mock_fetch_content_type(url):
        if "download/123" in url:
            return "application/pdf"
        return ""
        
    mock_gemini_resp = MagicMock()
    mock_gemini_resp.text = "Instruction/Installation Manual"
    digital_asset_service.model = MagicMock()

    with patch.object(digital_asset_service, '_fetch_content_type', side_effect=mock_fetch_content_type):
        with patch.object(digital_asset_service.model, 'generate_content', return_value=mock_gemini_resp):
            digital_asset_service.process_assets(row, candidates)

    assets = row.asset_result.assets
    
    # duplicate URL dropped
    assert len(assets) == 6 
    
    # Primary Image (img1)
    img1 = next(a for a in assets if "img1.jpg" in a.url)
    assert img1.classification == "Product Image"
    assert img1.status == "ACCEPTED"
    assert img1.official_domain_verified == True

    # Alternate Image (img2)
    img2 = next(a for a in assets if "img2.jpg" in a.url)
    assert img2.classification == "Alternate Image 1"

    # Deterministic Document (SDS)
    sds = next(a for a in assets if "doc.pdf" in a.url)
    assert sds.classification == "SDS"

    # Non-extension using Content Type
    spec = next(a for a in assets if "download/123" in a.url)
    assert spec.classification == "Specification Sheet" # 'spec' in link text

    # Third-party rejection
    amz = next(a for a in assets if "amazon.com" in a.url)
    assert amz.status == "REJECTED_NON_OFFICIAL"
    assert amz.official_domain_verified == False

    # Ambiguous falling back to Gemini
    weird = next(a for a in assets if "weird.pdf" in a.url)
    assert weird.classification == "Instruction/Installation Manual"

    print("Digital Assets processing passed!")
    
    # ----------------------------------------------------
    # Test output mapping
    headers = load_expected_headers()
    output_rows = map_to_output([row], headers)
    out = output_rows[0]

    # Exact output-column mapping
    assert out["Product Image"] == "https://official.com/img1.jpg"
    assert out["Alternate Image 1"] == "https://official.com/img2.jpg"
    assert out["SDS"] == "https://official.com/doc.pdf"
    assert out["Specification Sheet"] == "https://official.com/download/123"
    
    # Amazon image should NOT be mapped (REJECTED_NON_OFFICIAL)
    assert "https://amazon.com/img.jpg" not in out.values()

    # 252-column integrity
    assert list(out.keys()) == headers
    assert len(out) == 252

    print("Output builder digital assets mapping passed!")

if __name__ == "__main__":
    test_digital_assets_processing()
