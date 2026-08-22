from app.services.retrieval import retrieval_service
from app.schemas.schemas import IdentityResult

from unittest.mock import patch, MagicMock

def test_source_retrieval():
    # Mock an identity result with a known safe URL (e.g., example.com)
    identity = IdentityResult(
        mpn="TEST_MPN",
        official_source_url="https://example.com",
        status="VERIFIED"
    )
    
    print(f"Fetching source: {identity.official_source_url}")
    
    # Mock the HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>Example Domain</h1><p>Test content.</p></body></html>"
    
    with patch.object(retrieval_service.session, 'get', return_value=mock_response):
        result = retrieval_service.fetch_source(identity)
    
    assert result is not None
    assert result.status_code == 200
    assert result.success is True
    assert "Example Domain" in result.content
    
    print("Source retrieval test passed! Content preview:")
    print(result.content[:100] + "...")

if __name__ == "__main__":
    test_source_retrieval()
