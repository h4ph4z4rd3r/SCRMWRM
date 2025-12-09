import pytest
from app.contract.parser import PDFParser, FileSizeLimitExceeded, SecurityCheckError

@pytest.mark.asyncio
async def test_parser_file_size_limit():
    parser = PDFParser()
    # Create a fake large file (11MB)
    large_file = b"%PDF" + b"0" * (11 * 1024 * 1024)
    
    with pytest.raises(FileSizeLimitExceeded):
        await parser.parse(large_file, "large.pdf")

@pytest.mark.asyncio
async def test_parser_invalid_magic_bytes():
    parser = PDFParser()
    # Invalid header
    bad_file = b"NOT_A_PDF_HEADER"
    
    with pytest.raises(SecurityCheckError):
        await parser.parse(bad_file, "malware.exe")

@pytest.mark.asyncio
async def test_parser_valid_pdf_mock(mocker):
    # Mock pypdf logic since we don't have a real PDF file handy in unit tests easily
    # or we can use a small bytes structure if pypdf is lenient.
    # For now, we assume magic bytes check passes and we mock pypdf.PdfReader
    
    parser = PDFParser()
    valid_header = b"%PDF-1.4\n..."
    
    mock_reader = mocker.patch("app.contract.parser.pypdf.PdfReader")
    mock_page = mocker.Mock()
    mock_page.extract_text.return_value = "Safe content"
    mock_reader.return_value.pages = [mock_page]
    
    result = await parser.parse(valid_header, "safe.pdf")
    assert "Safe content" in result
