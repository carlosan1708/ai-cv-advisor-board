import io
from typing import Optional

from fpdf import FPDF
from pypdf import PdfReader

from exceptions import FileProcessingError
from logger import logger

# PDF Layout Constants
A4_WIDTH_MM = 210
MARGIN_MM = 20
EFFECTIVE_WIDTH = A4_WIDTH_MM - (2 * MARGIN_MM) - 5  # 5mm safety buffer


class CVService:
    @staticmethod
    def parse_cv_file(file_content: bytes, filename: str) -> str:
        """Parses an uploaded CV file (PDF or TXT) and returns its text content."""
        try:
            logger.info("Parsing CV file: %s", filename)
            lower_filename = filename.lower()
            if lower_filename.endswith(".pdf"):
                reader = PdfReader(io.BytesIO(file_content))
                content = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
                return content.strip()
            elif lower_filename.endswith(".txt"):
                return file_content.decode("utf-8").strip()
            else:
                raise FileProcessingError(f"Unsupported file format: {filename}. Please upload a PDF or TXT file.")
        except Exception as e:
            logger.error(f"Error parsing CV file {filename}: {str(e)}")
            raise FileProcessingError("Failed to read the CV file. Please ensure it is a valid PDF or TXT file.") from e

    @staticmethod
    def _sanitize_text_for_pdf(text: str) -> str:
        """Sanitizes text to be compatible with FPDF Latin-1 encoding."""
        replacements = {
            "–": "-",
            "—": "-",
            "‘": "'",
            "’": "'",
            "“": '"',
            "”": '"',
            "•": "-",
            "…": "...",
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text.encode("latin-1", "replace").decode("latin-1")

    @staticmethod
    def clean_markdown_code_blocks(text: str) -> str:
        """Removes markdown code block syntax if present."""
        cleaned = text.strip()
        if cleaned.startswith("```markdown"):
            cleaned = cleaned[11:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    @staticmethod
    def generate_pdf(cv_markdown: str) -> Optional[bytes]:
        """Generates a professional PDF document from Markdown content (A4, Arial)."""
        try:
            logger.info("Generating PDF from Markdown...")

            cleaned_cv = CVService.clean_markdown_code_blocks(cv_markdown)
            safe_cv = CVService._sanitize_text_for_pdf(cleaned_cv)

            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_margins(MARGIN_MM, MARGIN_MM, MARGIN_MM)

            lines = safe_cv.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(2)
                    continue

                if line.startswith("# "):
                    # H1 - Name or Main Title
                    pdf.ln(4)
                    pdf.set_x(MARGIN_MM)
                    pdf.set_font("helvetica", "B", 24)
                    pdf.multi_cell(EFFECTIVE_WIDTH, 10, line[2:].upper(), align="C", markdown=True)
                    pdf.ln(6)

                elif line.startswith("## "):
                    # H2 - Section Headers
                    pdf.ln(6)
                    pdf.set_x(MARGIN_MM)
                    pdf.set_font("helvetica", "B", 16)
                    pdf.multi_cell(EFFECTIVE_WIDTH, 8, line[3:].upper(), align="L", markdown=True)

                    # Horizontal Line
                    current_y = pdf.get_y()
                    pdf.set_line_width(0.5)
                    pdf.line(MARGIN_MM, current_y, MARGIN_MM + EFFECTIVE_WIDTH, current_y)
                    pdf.set_line_width(0.2)
                    pdf.ln(4)

                elif line.startswith("### "):
                    # H3 - Subsections
                    pdf.ln(3)
                    pdf.set_x(MARGIN_MM)
                    pdf.set_font("helvetica", "B", 14)
                    pdf.multi_cell(EFFECTIVE_WIDTH, 6, line[3:].strip(), align="L", markdown=True)

                elif line.startswith("- ") or line.startswith("* "):
                    # List Items
                    pdf.set_font("helvetica", size=10)
                    pdf.set_x(MARGIN_MM)
                    current_x = pdf.get_x()
                    pdf.set_x(current_x + 5)
                    pdf.multi_cell(EFFECTIVE_WIDTH - 5, 5, "- " + line[2:], align="L", markdown=True)

                else:
                    # Body Text
                    pdf.set_font("helvetica", size=10)
                    pdf.set_x(MARGIN_MM)
                    pdf.multi_cell(EFFECTIVE_WIDTH, 5, line, align="L", markdown=True)

            logger.info("PDF generated successfully.")
            return bytes(pdf.output())
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
