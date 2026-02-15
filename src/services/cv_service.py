import io
from typing import Optional

from fpdf import FPDF
from pypdf import PdfReader

from exceptions import FileProcessingError
from logger import logger


class CVService:
    @staticmethod
    def parse_cv_file(file_content: bytes, filename: str) -> str:
        """Parses an uploaded CV file (PDF or TXT) and returns its text content."""
        try:
            logger.info("Parsing CV file: %s", filename)
            if filename.lower().endswith(".pdf"):
                reader = PdfReader(io.BytesIO(file_content))
                content = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
                return content.strip()
            else:
                return file_content.decode("utf-8").strip()
        except Exception as e:
            logger.error(f"Error parsing CV file {filename}: {str(e)}")
            raise FileProcessingError("Failed to read the CV file. Please ensure it is a valid PDF or TXT file.") from e

    @staticmethod
    def generate_pdf(cv_markdown: str) -> Optional[bytes]:
        """Generates a PDF document from Markdown content."""
        try:
            logger.info("Generating PDF from Markdown...")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("helvetica", size=12)

            # Sanitize text for FPDF
            safe_cv = (
                cv_markdown.replace("–", "-")
                .replace("—", "-")
                .replace("‘", "'")
                .replace("’", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("•", "*")
            )
            # Encode to latin-1 for FPDF compatibility
            safe_cv = safe_cv.encode("latin-1", "replace").decode("latin-1")

            effective_width = pdf.w - 2 * pdf.l_margin

            for line in safe_cv.split("\n"):
                if line.startswith("# "):
                    pdf.set_font("helvetica", "B", 16)
                    pdf.multi_cell(effective_width, 10, line[2:])
                elif line.startswith("## "):
                    pdf.set_font("helvetica", "B", 14)
                    pdf.multi_cell(effective_width, 10, line[3:])
                elif line.startswith("### "):
                    pdf.set_font("helvetica", "B", 12)
                    pdf.multi_cell(effective_width, 8, line[4:])
                else:
                    pdf.set_font("helvetica", size=11)
                    pdf.multi_cell(effective_width, 6, line)

            logger.info("PDF generated successfully.")
            return bytes(pdf.output())
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
