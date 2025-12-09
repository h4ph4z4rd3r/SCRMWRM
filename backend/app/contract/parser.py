from abc import ABC, abstractmethod
import io
import logging
from typing import Optional
import pypdf

logger = logging.getLogger(__name__)

# Security Constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"application/pdf"}

class DocumentParsingError(Exception):
    """Raised when document parsing fails."""
    pass

class FileSizeLimitExceeded(DocumentParsingError):
    """Raised when the uploaded file exceeds the allowed size limit."""
    pass

class SecurityCheckError(DocumentParsingError):
    """Raised when the file fails security validation checks."""
    pass

class AbstractParser(ABC):
    """
    Abstract base class for all document parsers.
    
    This interface ensures that all parser implementations provide a consistent
    method for converting raw file content into text.
    """

    @abstractmethod
    async def parse(self, file_content: bytes, filename: str) -> str:
        """
        Parse the given binary file content and return the extracted text.

        Args:
            file_content (bytes): The raw binary content of the file.
            filename (str): The original filename (used for logging or validation).

        Returns:
            str: The extracted text content from the document.

        Raises:
            DocumentParsingError: If the document is malformed or unreadable.
            FileSizeLimitExceeded: If the content is too large.
            SecurityCheckError: If the content appears malicious.
        """
        pass

class PDFParser(AbstractParser):
    """
    Concrete implementation for parsing PDF documents using pypdf.
    
    Includes security validations for file size and basic integrity.
    """

    async def parse(self, file_content: bytes, filename: str) -> str:
        """
        Parses a PDF file from bytes.

        Security Measures:
            - Checks file size against MAX_FILE_SIZE_BYTES.
            - Validates PDF header signature (%PDF).
            - Uses robust pypdf reading to report form values + text.

        Args:
            file_content (bytes): The raw PDF bytes.
            filename (str): Debug info.

        Returns:
            str: Extracted text from all pages, concatenated with newlines.

        Raises:
            FileSizeLimitExceeded: If len(file_content) > 10MB.
            SecurityCheckError: If file not a valid PDF (header check).
            DocumentParsingError: If pypdf fails to read the stream.
        """
        # 1. Size Check
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            msg = f"File {filename} exceeds size limit of {MAX_FILE_SIZE_BYTES} bytes."
            logger.warning(msg)
            raise FileSizeLimitExceeded(msg)

        # 2. Magic Number Check (Basic Security)
        # PDF files must start with %PDF
        if not file_content.startswith(b"%PDF"):
            msg = f"File {filename} does not contain valid PDF signature."
            logger.warning(msg)
            raise SecurityCheckError(msg)

        text_content = []
        try:
            # Create a file-like object
            stream = io.BytesIO(file_content)
            reader = pypdf.PdfReader(stream)
            
            # Check for encryption (optional policy: reject encrypted?)
            if reader.is_encrypted:
                # We could try to decrypt with empty password, but usually it fails.
                # For now, let's log it.
                logger.info(f"PDF {filename} is encrypted. Attempting to read...")

            for i, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
                else:
                    logger.debug(f"Page {i} in {filename} yielded no text.")

        except Exception as e:
            logger.error(f"Failed to parse PDF {filename}: {e}")
            raise DocumentParsingError(f"PDF parsing failed: {str(e)}")

        return "\n".join(text_content)
