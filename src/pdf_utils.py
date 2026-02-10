"""Utility functions for generating PDF documents from Markdown content."""

import streamlit as st
from fpdf import FPDF


def generate_pdf(cv_markdown):
    """Generate a PDF document from the provided Markdown content.

    Args:
        cv_markdown: The CV content in Markdown format.

    Returns:
        The generated PDF as bytes, or None if an error occurs.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)

        # Sanitize text
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

        # Available width for text
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

        return bytes(pdf.output())
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None
