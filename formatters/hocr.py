"""
HOCR (HTML-based OCR) formatter for OCR output.

HOCR is an open standard for representing OCR results in HTML format,
preserving layout and coordinate information.
"""
import html
from typing import List, Tuple
from .base import BaseFormatter


class HOCRFormatter(BaseFormatter):
    """
    Formats OCR output as HOCR (HTML-based OCR) format.

    HOCR uses HTML with specific class names to represent OCR data:
    - ocr_page: The entire page
    - ocr_carea: Column or text area
    - ocr_par: Paragraph
    - ocr_line: Text line
    - ocrx_word: Individual word

    Each element includes a 'title' attribute with bounding box coordinates:
    bbox x0 y0 x1 y1

    Note: Since PaddleOCR-VL model outputs text without coordinate information,
    this formatter creates estimated positions based on text flow.
    """

    def __init__(self):
        self.line_height = 30  # Estimated line height in pixels
        self.word_spacing = 10  # Estimated spacing between words
        self.avg_char_width = 10  # Estimated character width

    def format(self, text: str, image_width: int = None, image_height: int = None, **kwargs) -> str:
        """
        Format OCR text as HOCR.

        Args:
            text: The raw OCR text output
            image_width: Width of the source image (default: estimated from text)
            image_height: Height of the source image (default: estimated from text)
            **kwargs: Additional parameters (e.g., title, lang)

        Returns:
            HOCR-formatted HTML string
        """
        if not text or not text.strip():
            text = ""

        # Parse text into lines and words
        lines = text.split('\n')

        # Estimate image dimensions if not provided
        if image_width is None:
            max_line_length = max((len(line) for line in lines), default=0)
            image_width = max(800, max_line_length * self.avg_char_width)

        if image_height is None:
            image_height = max(600, len(lines) * self.line_height + 40)

        # Extract optional parameters
        title = kwargs.get('title', 'OCR Result')
        lang = kwargs.get('lang', 'en')

        # Build HOCR document
        hocr_parts = []
        hocr_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        hocr_parts.append('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"')
        hocr_parts.append('    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
        hocr_parts.append(f'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">')
        hocr_parts.append('<head>')
        hocr_parts.append(f'  <title>{html.escape(title)}</title>')
        hocr_parts.append('  <meta http-equiv="content-type" content="text/html; charset=utf-8" />')
        hocr_parts.append('  <meta name="ocr-system" content="PaddleOCR-VL" />')
        hocr_parts.append('  <meta name="ocr-capabilities" content="ocr_page ocr_carea ocr_par ocr_line ocrx_word" />')
        hocr_parts.append('</head>')
        hocr_parts.append('<body>')

        # Page element
        page_bbox = f"bbox 0 0 {image_width} {image_height}"
        hocr_parts.append(f'  <div class="ocr_page" id="page_1" title="{page_bbox}">')

        # Content area
        carea_bbox = f"bbox 10 10 {image_width - 10} {image_height - 10}"
        hocr_parts.append(f'    <div class="ocr_carea" id="carea_1_1" title="{carea_bbox}">')

        # Process each paragraph (treat each non-empty text block as a paragraph)
        y_offset = 20
        par_id = 1
        line_id = 1
        word_id = 1

        current_par_lines = []

        for line_text in lines:
            line_text = line_text.strip()

            # Empty line indicates paragraph break
            if not line_text:
                if current_par_lines:
                    # Output current paragraph
                    par_html, line_id, word_id = self._format_paragraph(
                        current_par_lines, par_id, line_id, word_id,
                        y_offset, image_width
                    )
                    hocr_parts.append(par_html)
                    par_id += 1
                    y_offset += len(current_par_lines) * self.line_height + 10
                    current_par_lines = []
                continue

            current_par_lines.append(line_text)

        # Output final paragraph if any
        if current_par_lines:
            par_html, line_id, word_id = self._format_paragraph(
                current_par_lines, par_id, line_id, word_id,
                y_offset, image_width
            )
            hocr_parts.append(par_html)

        # Close tags
        hocr_parts.append('    </div>')  # Close carea
        hocr_parts.append('  </div>')    # Close page
        hocr_parts.append('</body>')
        hocr_parts.append('</html>')

        return '\n'.join(hocr_parts)

    def _format_paragraph(
        self,
        lines: List[str],
        par_id: int,
        start_line_id: int,
        start_word_id: int,
        y_offset: int,
        image_width: int
    ) -> Tuple[str, int, int]:
        """
        Format a paragraph with its lines and words.

        Args:
            lines: List of line strings in the paragraph
            par_id: Paragraph ID
            start_line_id: Starting line ID
            start_word_id: Starting word ID
            y_offset: Vertical offset for the paragraph
            image_width: Width of the image

        Returns:
            Tuple of (paragraph HTML, next line_id, next word_id)
        """
        line_id = start_line_id
        word_id = start_word_id

        # Calculate paragraph bounding box
        par_height = len(lines) * self.line_height
        par_bbox = f"bbox 20 {y_offset} {image_width - 20} {y_offset + par_height}"

        par_parts = []
        par_parts.append(f'      <p class="ocr_par" id="par_1_{par_id}" title="{par_bbox}">')

        # Process each line
        for i, line_text in enumerate(lines):
            line_y = y_offset + i * self.line_height
            line_html, word_id = self._format_line(
                line_text, par_id, line_id, word_id,
                line_y, image_width
            )
            par_parts.append(line_html)
            line_id += 1

        par_parts.append('      </p>')

        return '\n'.join(par_parts), line_id, word_id

    def _format_line(
        self,
        line_text: str,
        par_id: int,
        line_id: int,
        start_word_id: int,
        y: int,
        image_width: int
    ) -> Tuple[str, int]:
        """
        Format a text line with its words.

        Args:
            line_text: The line text
            par_id: Parent paragraph ID
            line_id: Line ID
            start_word_id: Starting word ID
            y: Vertical position
            image_width: Width of the image

        Returns:
            Tuple of (line HTML, next word_id)
        """
        word_id = start_word_id
        words = line_text.split()

        # Estimate line dimensions
        line_width = sum(len(w) * self.avg_char_width for w in words) + \
                     (len(words) - 1) * self.word_spacing if words else 0
        line_bbox = f"bbox 30 {y} {min(30 + line_width, image_width - 30)} {y + self.line_height}"

        line_parts = []
        line_parts.append(f'        <span class="ocr_line" id="line_1_{line_id}" title="{line_bbox}">')

        # Process each word
        x_offset = 30
        for word_text in words:
            word_width = len(word_text) * self.avg_char_width
            word_bbox = f"bbox {x_offset} {y} {x_offset + word_width} {y + self.line_height}"

            escaped_word = html.escape(word_text)
            line_parts.append(
                f'          <span class="ocrx_word" id="word_1_{word_id}" '
                f'title="{word_bbox}">{escaped_word}</span>'
            )

            word_id += 1
            x_offset += word_width + self.word_spacing

        line_parts.append('        </span>')

        return '\n'.join(line_parts), word_id

    def get_content_type(self) -> str:
        """Get the MIME content type for HOCR format."""
        return 'text/html; charset=utf-8'
