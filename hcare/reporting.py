from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def pdf_report(report):
    out = BytesIO()
    doc = SimpleDocTemplate(out)
    styles = getSampleStyleSheet()
    result = report["result"]
    safe = lambda value: escape(str(value))
    story = [Paragraph("H-CARE Assessment Report", styles["Title"]), Spacer(1, 12), Paragraph(safe(report["assessment"]), styles["Heading2"]), Paragraph("Generated (UTC): " + safe(report["generated_at_utc"]), styles["Normal"]), Spacer(1, 12)]
    for label, key in [("Base H-CARE index", "base_index"), ("Evidence-adjusted index", "evidence_adjusted_index"), ("Evidence gap", "evidence_gap"), ("Assessment status", "status")]:
        story.append(Paragraph(safe(label) + ": " + safe(result[key]), styles["Normal"]))
    story.append(Spacer(1, 12))
    rows = [["Dimension", "Score", "Confidence", "Weight"]]
    for name, score in result["dimension_scores"].items():
        rows.append([Paragraph(safe(name), styles["BodyText"]), f"{score:.2f}", f"{result['dimension_confidence'][name]:.2f}", f"{result['weights'][name]:.2f}"])
    table = Table(rows, colWidths=[240, 75, 85, 75], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0), colors.lightgrey), ("GRID", (0,0),(-1,-1), 0.3, colors.grey), ("VALIGN", (0,0),(-1,-1), "TOP"), ("BOTTOMPADDING", (0,0),(-1,-1), 7)]))
    story.extend([table, Spacer(1, 12), Paragraph("Failed critical gates: " + safe(", ".join(result["failed_gates"]) or "None"), styles["Normal"]), Spacer(1, 12), Paragraph("Evidence references", styles["Heading2"])])
    for name, ref in report.get("evidence_references", {}).items():
        story.append(Paragraph(safe(name) + ": " + safe(ref or "Not supplied"), styles["Normal"]))
    story.extend([Spacer(1, 15), Paragraph("Research prototype. Scores and references are assessor-supplied or synthetic, not independently verified. Not a compliance certification.", styles["Italic"])])
    doc.build(story)
    return out.getvalue()
