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
        """Generates a professional PDF document from Markdown content (A4, Arial 10/11/12/16)."""
        try:
            logger.info("Generating PDF from Markdown...")
            
            # Clean up markdown code blocks if present
            cleaned_cv = cv_markdown.strip()
            if cleaned_cv.startswith("```markdown"):
                cleaned_cv = cleaned_cv[11:]
            elif cleaned_cv.startswith("```"):
                cleaned_cv = cleaned_cv[3:]
            if cleaned_cv.endswith("```"):
                cleaned_cv = cleaned_cv[:-3]
            
            cleaned_cv = cleaned_cv.strip()

            # Use A4 format explicitly
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Set wider margins (20mm) to ensure content never touches edges
            pdf.set_margins(20, 20, 20)

            # Sanitize text for FPDF (Latin-1 limitations)
            safe_cv = (
                cleaned_cv.replace("–", "-")
                .replace("—", "-")
                .replace("‘", "'")
                .replace("’", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("•", "-")
            )
            
            # Encode to latin-1 to avoid FPDF Unicode errors
            safe_cv = safe_cv.encode("latin-1", "replace").decode("latin-1")

            # Calculate effective width for text
            # A4 is 210mm wide. With 20mm margins: 210 - 40 = 170mm.
            # Reducing to 165mm ensures extra safety buffer on the right.
            effective_width = 165
            left_margin = 20

            lines = safe_cv.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(2)
                    continue

                if line.startswith("# "):
                    # H1 - Name or Main Title (Centered, Extra Large)
                    pdf.ln(4)
                    pdf.set_x(left_margin)  # Force alignment
                    pdf.set_font("helvetica", "B", 24)
                    pdf.multi_cell(effective_width, 10, line[2:].upper(), align="C", markdown=True)
                    pdf.ln(6)
                elif line.startswith("## "):
                    # H2 - Section Headers (Experience, Education) (Large, Bold)
                    pdf.ln(6)
                    pdf.set_x(left_margin)  # Force alignment
                    pdf.set_font("helvetica", "B", 16)
                    # Use multi_cell to ensure wrapping even for headers
                    pdf.multi_cell(effective_width, 8, line[3:].upper(), align="L", markdown=True)
                    # Draw a line under the header for separation using absolute coordinates
                    current_y = pdf.get_y()
                    pdf.set_line_width(0.5)
                    pdf.line(left_margin, current_y, left_margin + effective_width, current_y)
                    pdf.set_line_width(0.2)
                    pdf.ln(4)
                elif line.startswith("### "):
                    # H3 - Job Titles / Subsections (Bold, Medium-Large)
                    pdf.ln(3)
                    pdf.set_x(left_margin)  # Force alignment
                    pdf.set_font("helvetica", "B", 14)
                    pdf.multi_cell(effective_width, 6, line[3:].strip(), align="L", markdown=True)
                elif line.startswith("- ") or line.startswith("* "):
                    # List items (Standard Body Font)
                    pdf.set_font("helvetica", size=10)
                    pdf.set_x(left_margin)  # Force alignment
                    # Indent slightly for bullets
                    current_x = pdf.get_x()
                    pdf.set_x(current_x + 5)
                    # Use a simple hyphen for maximum compatibility (bullet char can cause encoding issues)
                    pdf.multi_cell(effective_width - 5, 5, "- " + line[2:], align="L", markdown=True)
                    # No need to reset X manually as next loop iteration resets it or uses default margin
                else:
                    # Body Text (Standard Font)
                    pdf.set_font("helvetica", size=10)
                    pdf.set_x(left_margin)  # Force alignment
                    pdf.multi_cell(effective_width, 5, line, align="L", markdown=True)

            logger.info("PDF generated successfully.")
            return bytes(pdf.output())
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
