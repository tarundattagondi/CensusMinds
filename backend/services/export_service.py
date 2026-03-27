"""Export services — generates PDF reports and CSV files from simulation results."""

import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)


def generate_csv(results: dict) -> str:
    """Generate a CSV string of all persona responses."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Name", "Age", "Ethnicity", "Income", "Housing", "Commute",
        "Education", "Stance", "Impact Level", "Reasoning",
        "Would Attend", "Suggested Modification",
    ])

    for r in results.get("all_responses", []):
        writer.writerow([
            r.get("persona_name", ""),
            r.get("age", ""),
            r.get("ethnicity", ""),
            r.get("income_range", ""),
            r.get("housing_type", ""),
            r.get("commute_mode", ""),
            r.get("education", ""),
            r.get("stance", ""),
            r.get("impact_level", ""),
            r.get("reasoning", ""),
            r.get("would_attend", ""),
            r.get("suggested_modification", ""),
        ])

    return output.getvalue()


def generate_pdf(results: dict) -> bytes:
    """Generate a PDF report from simulation results. Returns PDF bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, textColor=colors.grey, spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceBefore=16, spaceAfter=8)
    body_style = styles['Normal']
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.grey)

    elements = []

    # Title
    elements.append(Paragraph("CensusMinds Simulation Report", title_style))

    policy = results.get("policy", "N/A")
    zip_code = results.get("zip_code", "N/A")
    census = results.get("census_snapshot", {})
    pop = census.get("total_population", "N/A")
    income = census.get("median_household_income", 0)
    pop_str = f"{pop:,}" if isinstance(pop, int) else str(pop)
    income_str = f"${income:,}" if isinstance(income, int) else str(income)
    elements.append(Paragraph(f"ZIP Code: {zip_code} | Population: {pop_str} | Median Income: {income_str}", subtitle_style))
    elements.append(Paragraph(f"<b>Policy:</b> {policy}", body_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", color=colors.lightgrey))
    elements.append(Spacer(1, 12))

    # Summary
    summary = results.get("summary", {})
    elements.append(Paragraph("Overall Results", heading_style))

    summary_data = [
        ["Metric", "Value"],
        ["Support", f"{summary.get('support_pct', 0)}% ({summary.get('support_count', 0)} personas)"],
        ["Oppose", f"{summary.get('oppose_pct', 0)}% ({summary.get('oppose_count', 0)} personas)"],
        ["Total Personas", str(summary.get('total_personas', 0))],
        ["Would Attend Meeting", f"{results.get('attendance', {}).get('would_attend_pct', 0)}%"],
    ]

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5ff')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])
    t = Table(summary_data, colWidths=[2.5 * inch, 4 * inch])
    t.setStyle(table_style)
    elements.append(t)
    elements.append(Spacer(1, 16))

    # Breakdown tables
    breakdown_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5ff')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ])

    def add_breakdown(title, data):
        if not data:
            return
        elements.append(Paragraph(title, heading_style))
        rows = [["Group", "Support %", "Oppose %", "Count"]]
        for group, vals in data.items():
            rows.append([group, f"{vals['support_pct']}%", f"{vals['oppose_pct']}%", str(vals['total'])])
        t = Table(rows, colWidths=[2.5 * inch, 1.25 * inch, 1.25 * inch, 1 * inch])
        t.setStyle(breakdown_table_style)
        elements.append(t)
        elements.append(Spacer(1, 8))

    add_breakdown("Breakdown by Income", results.get("breakdown_by_income"))
    add_breakdown("Breakdown by Age Group", results.get("breakdown_by_age_group"))
    add_breakdown("Breakdown by Commute Mode", results.get("breakdown_by_commute"))
    add_breakdown("Breakdown by Housing", results.get("breakdown_by_housing"))

    # Hidden Impacts
    hidden = results.get("hidden_impacts", [])
    if hidden:
        elements.append(Paragraph("Hidden Impacts", heading_style))
        elements.append(Paragraph(
            "<i>Groups with HIGH/CRITICAL impact but low public meeting attendance:</i>",
            small_style,
        ))
        elements.append(Spacer(1, 6))
        for h in hidden:
            elements.append(Paragraph(
                f"<b>{h['group']}</b> — {h['high_impact_count']} highly impacted, "
                f"{h['would_not_attend_count']} wouldn't attend (out of {h['total_in_group']})",
                body_style,
            ))
            elements.append(Spacer(1, 4))

    # Top Concerns & Benefits
    for section, key in [("Top Concerns", "top_concerns"), ("Top Benefits", "top_benefits")]:
        items = results.get(key, [])
        if items:
            elements.append(Paragraph(section, heading_style))
            for i, item in enumerate(items, 1):
                elements.append(Paragraph(f"{i}. {item}", body_style))
            elements.append(Spacer(1, 8))

    # Suggested Modifications
    mods = results.get("suggested_modifications", [])
    if mods:
        elements.append(Paragraph("Suggested Modifications", heading_style))
        for m in mods[:10]:
            elements.append(Paragraph(f"<b>{m['persona']}:</b> {m['suggestion']}", body_style))
            elements.append(Spacer(1, 4))

    # All Persona Responses
    all_responses = results.get("all_responses", [])
    if all_responses:
        elements.append(Paragraph("Individual Persona Responses", heading_style))
        resp_rows = [["Name", "Age", "Stance", "Impact", "Attend", "Reasoning"]]
        for r in all_responses:
            reasoning = r.get("reasoning", "")
            if len(reasoning) > 80:
                reasoning = reasoning[:77] + "..."
            resp_rows.append([
                r.get("persona_name", ""),
                str(r.get("age", "")),
                r.get("stance", ""),
                r.get("impact_level", ""),
                r.get("would_attend", ""),
                reasoning,
            ])
        resp_table = Table(resp_rows, colWidths=[1.1 * inch, 0.4 * inch, 0.65 * inch, 0.6 * inch, 0.5 * inch, 3.25 * inch])
        resp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5ff')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(resp_table)

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", color=colors.lightgrey))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Generated by CensusMinds — census-grounded local policy impact simulator", small_style))

    doc.build(elements)
    return buffer.getvalue()
