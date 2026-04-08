from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

PURPLE = HexColor("#A100FF")
WHITE = white


def generate_pdf(assessment: dict, results: dict) -> bytes:
    """Return PDF bytes for the executive summary report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=PURPLE,
        fontSize=20,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=PURPLE,
        fontSize=13,
        spaceBefore=12,
        spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=HexColor("#666666"),
    )

    client = assessment.get("client", {})
    scores = results.get("scores", {})
    interest = results.get("total_interest", 0)
    tco = results.get("total_tco", 0)

    story = []

    # Header
    story.append(Paragraph("▲ Accenture Tech Debt Assessment", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE))
    story.append(Spacer(1, 0.3 * cm))

    # Client info
    story.append(Paragraph("Executive Summary", heading_style))
    client_data = [
        ["Client", client.get("name", "—"), "Industry", client.get("industry", "—")],
        ["Market", client.get("market", "—"), "Size", client.get("size", "—")],
    ]
    client_table = Table(client_data, colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm])
    client_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), PURPLE),
        ("TEXTCOLOR", (2, 0), (2, -1), PURPLE),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.4 * cm))

    # KPI summary
    story.append(Paragraph("Financial Summary", heading_style))
    kpi_data = [
        ["Metric", "Value"],
        ["Total Annual Tech Debt Interest", f"{interest:.1f} kUSD"],
        ["Total Application TCO", f"{tco:.1f} kUSD/year"],
        ["Applications assessed", str(len(assessment.get("applications", [])))],
        ["Infrastructure components assessed", str(len(assessment.get("infrastructure", [])))],
    ]
    kpi_table = Table(kpi_data, colWidths=[10 * cm, 7 * cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F5F5F5"), WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.4 * cm))

    # Scores by dimension
    story.append(Paragraph("Tech Debt Scores by Dimension (1 = best, 5 = worst)", heading_style))
    score_data = [["Dimension", "Score", "Status"]]
    for dim, label in [("application", "Application"), ("infrastructure", "Infrastructure"),
                       ("architecture", "Architecture"), ("people", "People")]:
        sc = scores.get(dim, 0)
        status = "High Risk" if sc >= 3 else ("Medium Risk" if sc >= 2 else "Low Risk")
        score_data.append([label, f"{sc:.2f}", status])

    score_table = Table(score_data, colWidths=[6 * cm, 4 * cm, 7 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#F5F5F5"), WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.4 * cm))

    # Interest by dimension
    story.append(Paragraph("Annual Interest Cost by Dimension (kUSD)", heading_style))
    interest_dim = results.get("interest_by_dimension", {})
    interest_data = [["Dimension", "Annual Interest (kUSD)"]]
    for dim, label in [("application", "Application"), ("infrastructure", "Infrastructure"),
                       ("architecture", "Architecture"), ("people", "People")]:
        interest_data.append([label, f"{interest_dim.get(dim, 0):.1f}"])
    interest_data.append(["TOTAL", f"{interest:.1f}"])

    int_table = Table(interest_data, colWidths=[10 * cm, 7 * cm])
    int_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [HexColor("#F5F5F5"), WHITE]),
        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#F0E0FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(int_table)

    # Footer
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE))
    story.append(Paragraph("Generated by Accenture Tech Debt Calculator", label_style))

    doc.build(story)
    return buffer.getvalue()
