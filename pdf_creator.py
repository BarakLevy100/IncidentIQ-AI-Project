from fpdf import FPDF


class PostmortemPDF(FPDF):
    def header(self):
        # Document Header
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "IncidentIQ - Post-Incident Report (PIR)", border=0, ln=1)
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, "Generated via AI Multi-Agent Audit Pipeline", border=0, ln=1)
        self.line(10, 25, 200, 25)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def sanitize_for_latin1(text: str) -> str:
    """
    Replaces common unicode characters with latin-1 safe ASCII equivalents.
    Forces the final string to be latin-1 compatible to prevent FPDF crashes.
    """
    replacements = {
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2022': '*',  # bullet
        '\u2026': '...',  # ellipsis
        '\u00A0': ' ',  # non-breaking space
    }

    # Replace known offenders
    for search, replace in replacements.items():
        text = text.replace(search, replace)

    # Catch-all: forcefully encode to latin-1, replacing any unknown characters with '?'
    # Then decode back to a string so FPDF can process it normally.
    return text.encode('latin-1', 'replace').decode('latin-1')


def create_pdf(report_md: str) -> bytes:
    """Parses AI markdown text and converts it into a formatted PDF byte stream."""
    pdf = PostmortemPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    lines = report_md.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue

        # Sanitize the line before FPDF touches it
        line = sanitize_for_latin1(line)

        # Parse H2 Headings (## Heading)
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 12)
            clean_title = line.replace("## ", "").strip()
            pdf.cell(0, 8, clean_title, ln=1)
            pdf.ln(2)

        # Parse H1 or H3 Headings
        elif line.startswith("# ") or line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            clean_title = line.replace("### ", "").replace("# ", "").strip()
            pdf.cell(0, 6, clean_title, ln=1)

        # Parse Bullet Points
        elif line.startswith("* ") or line.startswith("- "):
            pdf.set_font("Helvetica", size=10)
            clean_bullet = line[2:].replace("**", "").strip()
            pdf.multi_cell(0, 6, f"  *  {clean_bullet}")

        # Standard Text
        else:
            pdf.set_font("Helvetica", size=10)
            clean_text = line.replace("**", "").strip()
            pdf.multi_cell(0, 6, clean_text)

    # Output to byte string safely
    try:
        pdf_string = pdf.output(dest='S')
        if isinstance(pdf_string, str):
            return pdf_string.encode("latin-1", "ignore")
        return bytes(pdf_string)
    except Exception:
        out = pdf.output()
        if isinstance(out, str):
            return out.encode("latin-1", "ignore")
        return bytes(out)