"""
Export questions and answers as PDF files.
"""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _create_pdf_doc() -> tuple[BytesIO, SimpleDocTemplate, list]:
    """Create a PDF document with standard styles."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    return buffer, doc, styles


def _esc(s: str) -> str:
    """Escape HTML special chars for ReportLab Paragraph."""
    return escape(str(s) if s else "")


def generate_question_paper_pdf(questions: list[dict], question_type: str) -> bytes:
    """Generate PDF with questions only (no answers)."""
    buffer, doc, styles = _create_pdf_doc()
    story = []

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=20,
    )
    story.append(Paragraph("Question Paper", title_style))
    story.append(Spacer(1, 12))

    body_style = styles["Normal"]
    for i, q in enumerate(questions, 1):
        if question_type == "mcq":
            text = f"<b>{i}. {_esc(q.get('question', ''))}</b><br/><br/>"
            for opt in q.get("options", []):
                text += f"&nbsp;&nbsp;&nbsp;{_esc(opt)}<br/>"
        elif question_type == "fill_blank":
            text = f"<b>{i}. {_esc(q.get('sentence', ''))}</b>"
        else:
            text = f"<b>{i}. {_esc(q.get('question', ''))}</b>"
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 16))

    doc.build(story)
    return buffer.getvalue()


def generate_answers_pdf(questions: list[dict], question_type: str) -> bytes:
    """Generate PDF with answers only."""
    buffer, doc, styles = _create_pdf_doc()
    story = []

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=20,
    )
    story.append(Paragraph("Answer Key", title_style))
    story.append(Spacer(1, 12))

    body_style = styles["Normal"]
    for i, q in enumerate(questions, 1):
        if question_type == "mcq":
            ans = q.get("correct", "")
        elif question_type == "fill_blank":
            ans = q.get("answer", "")
        else:
            ans = q.get("expected_answer", "")
        text = f"<b>{i}.</b> {_esc(ans)}"
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 10))

    doc.build(story)
    return buffer.getvalue()
