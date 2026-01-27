"""PDF file reading and image conversion utilities."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PDFReaderError(Exception):
    """Error during PDF reading or conversion."""

    pass


@dataclass
class PDFPage:
    """Represents a single page from a PDF as an image."""

    page_number: int
    image_data: bytes
    width: int
    height: int
    format: str = "PNG"


class PDFReader:
    """Handles PDF file reading and conversion to images for AI vision parsing.

    Supports two backends:
    - pdf2image (requires system poppler) - primary, faster
    - PyMuPDF (fitz) - fallback, pure Python
    """

    def __init__(self, dpi: int = 150, max_pages: int = 3) -> None:
        """Initialize PDFReader.

        Args:
            dpi: Resolution for image conversion. 150 is good balance of quality/size.
            max_pages: Maximum pages to convert (character sheets rarely exceed 2-3).
        """
        self.dpi = dpi
        self.max_pages = max_pages
        self._backend: Optional[str] = None

    def _detect_backend(self) -> str:
        """Detect available PDF backend."""
        if self._backend:
            return self._backend

        # Try pdf2image first (faster, but requires poppler)
        try:
            import pdf2image

            # Test that poppler is actually available
            pdf2image.pdfinfo_from_path
            self._backend = "pdf2image"
            logger.debug("Using pdf2image backend")
            return self._backend
        except (ImportError, Exception):
            pass

        # Try PyMuPDF (pure Python fallback)
        try:
            import fitz  # PyMuPDF

            self._backend = "pymupdf"
            logger.debug("Using PyMuPDF backend")
            return self._backend
        except ImportError:
            pass

        raise PDFReaderError(
            "No PDF backend available. Install with: pip install 'ccvault[import]'\n"
            "This requires either pdf2image (with system poppler) or PyMuPDF."
        )

    def get_page_count(self, pdf_path: Path) -> int:
        """Get the number of pages in a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Number of pages in the PDF.
        """
        if not pdf_path.exists():
            raise PDFReaderError(f"PDF file not found: {pdf_path}")

        backend = self._detect_backend()

        if backend == "pdf2image":
            import pdf2image

            try:
                info = pdf2image.pdfinfo_from_path(str(pdf_path))
                return info.get("Pages", 0)
            except Exception as e:
                raise PDFReaderError(f"Failed to read PDF info: {e}") from e

        elif backend == "pymupdf":
            import fitz

            try:
                doc = fitz.open(str(pdf_path))
                count = len(doc)
                doc.close()
                return count
            except Exception as e:
                raise PDFReaderError(f"Failed to read PDF: {e}") from e

        raise PDFReaderError(f"Unknown backend: {backend}")

    def convert_to_images(
        self, pdf_path: Path, pages: Optional[list[int]] = None
    ) -> list[PDFPage]:
        """Convert PDF pages to images.

        Args:
            pdf_path: Path to the PDF file.
            pages: Specific page numbers to convert (1-indexed). If None, converts
                   up to max_pages from the beginning.

        Returns:
            List of PDFPage objects containing image data.
        """
        if not pdf_path.exists():
            raise PDFReaderError(f"PDF file not found: {pdf_path}")

        backend = self._detect_backend()

        if pages is None:
            total_pages = self.get_page_count(pdf_path)
            pages = list(range(1, min(total_pages + 1, self.max_pages + 1)))

        if backend == "pdf2image":
            return self._convert_with_pdf2image(pdf_path, pages)
        elif backend == "pymupdf":
            return self._convert_with_pymupdf(pdf_path, pages)

        raise PDFReaderError(f"Unknown backend: {backend}")

    def _convert_with_pdf2image(self, pdf_path: Path, pages: list[int]) -> list[PDFPage]:
        """Convert using pdf2image backend."""
        import pdf2image

        result = []
        try:
            # pdf2image uses 1-indexed pages
            images = pdf2image.convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                first_page=min(pages),
                last_page=max(pages),
                fmt="PNG",
            )

            for i, img in enumerate(images):
                page_num = min(pages) + i
                if page_num not in pages:
                    continue

                # Convert PIL Image to bytes
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_data = buffer.getvalue()

                result.append(
                    PDFPage(
                        page_number=page_num,
                        image_data=image_data,
                        width=img.width,
                        height=img.height,
                        format="PNG",
                    )
                )
        except Exception as e:
            raise PDFReaderError(f"Failed to convert PDF with pdf2image: {e}") from e

        return result

    def _convert_with_pymupdf(self, pdf_path: Path, pages: list[int]) -> list[PDFPage]:
        """Convert using PyMuPDF backend."""
        import fitz

        result = []
        try:
            doc = fitz.open(str(pdf_path))

            for page_num in pages:
                if page_num < 1 or page_num > len(doc):
                    logger.warning(f"Page {page_num} out of range, skipping")
                    continue

                # PyMuPDF uses 0-indexed pages
                page = doc[page_num - 1]

                # Calculate zoom factor for desired DPI (PyMuPDF default is 72 DPI)
                zoom = self.dpi / 72
                matrix = fitz.Matrix(zoom, zoom)

                # Render page to pixmap
                pix = page.get_pixmap(matrix=matrix)

                # Convert to PNG bytes
                image_data = pix.tobytes("png")

                result.append(
                    PDFPage(
                        page_number=page_num,
                        image_data=image_data,
                        width=pix.width,
                        height=pix.height,
                        format="PNG",
                    )
                )

            doc.close()
        except Exception as e:
            raise PDFReaderError(f"Failed to convert PDF with PyMuPDF: {e}") from e

        return result

    def convert_to_image_bytes(self, pdf_path: Path) -> list[bytes]:
        """Convenience method to get just the image bytes.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            List of PNG image data as bytes.
        """
        pages = self.convert_to_images(pdf_path)
        return [page.image_data for page in pages]


def is_import_available() -> bool:
    """Check if PDF import dependencies are available."""
    try:
        reader = PDFReader()
        reader._detect_backend()
        return True
    except PDFReaderError:
        return False


def detect_sheet_type(images: list[bytes]) -> str:
    """Attempt to detect the character sheet source type.

    This is a heuristic detection based on visual patterns. The AI parser
    will ultimately determine the best interpretation.

    Args:
        images: List of PNG image data.

    Returns:
        One of: "dndbeyond", "roll20", "generic"
    """
    # For now, return "auto" and let the AI determine the type
    # Future: Could use image analysis or OCR to detect source
    return "auto"
