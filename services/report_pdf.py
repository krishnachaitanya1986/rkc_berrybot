from io import BytesIO
from html import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _format_inline(text):
    """Convert simple Markdown bold into ReportLab paragraph markup."""
    safe = escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)


def build_report_pdf(report_markdown: str) -> bytes:
    """Return a PDF containing the generated interview report."""
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=(595.28, 841.89),  # A4
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48,
        title="Technical Interview Report",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17324D"),
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#17324D"),
            spaceBefore=13,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBullet",
            parent=styles["ReportBody"],
            leftIndent=14,
            firstLineIndent=-10,
        )
    )

    story = []

    for raw_line in report_markdown.splitlines():
        line = raw_line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        if line == "---":
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.6,
                    color=colors.HexColor("#D5DCE3"),
                )
            )
            continue

        if line.startswith("### "):
            heading = line[4:].strip()
            style = (
                styles["ReportTitle"]
                if heading == "Interview Information"
                else styles["ReportHeading"]
            )
            story.append(Paragraph(_format_inline(heading), style))
            continue

        if line.startswith("## "):
            story.append(
                Paragraph(
                    _format_inline(line[3:].strip()),
                    styles["ReportHeading"],
                )
            )
            continue

        if line.startswith("# "):
            story.append(
                Paragraph(
                    _format_inline(line[2:].strip()),
                    styles["ReportTitle"],
                )
            )
            continue

        if line.startswith(("- ", "* ")):
            story.append(
                Paragraph(
                    "• " + _format_inline(line[2:].strip()),
                    styles["ReportBullet"],
                )
            )
            continue

        # Remove Markdown's trailing two spaces used for a line break.
        story.append(
            Paragraph(
                _format_inline(line.rstrip()),
                styles["ReportBody"],
            )
        )

    if not story:
        story.append(
            Paragraph("No report content available.", styles["ReportBody"])
        )

    document.build(story)
    return buffer.getvalue()