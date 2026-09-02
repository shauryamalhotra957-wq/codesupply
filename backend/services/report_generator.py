import csv
import io
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class ReportGenerator:
    """
    Generates professional PDF security audit reports and CSV component inventories.
    """

    @staticmethod
    def generate_csv(components: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        fieldnames = [
            "name",
            "version",
            "ecosystem",
            "direct",
            "purl",
            "license",
            "source_file",
            "scope",
            "integrity",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for comp in components:
            writer.writerow(comp)
        return output.getvalue()

    @staticmethod
    def generate_pdf(
        project: Dict[str, Any],
        components: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=14,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        finding_title = ParagraphStyle(
            "FindingTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#0f172a"),
        )
        finding_body = ParagraphStyle(
            "FindingBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#334155"),
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("CodeSupply — SBOM & Supply Chain Audit Report", title_style))
        story.append(Spacer(1, 4))
        story.append(
            Paragraph(
                f"Project: <b>{project['name']}</b> | Scanned: {project.get('created_at', 'N/A')[:19]} | "
                f"Ecosystems: {', '.join(project.get('ecosystems', [])) or 'None'}",
                subtitle_style,
            )
        )
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#6366f1"), spaceAfter=15))

        # 2. Executive Metrics Summary Table
        metrics_data = [
            [
                Paragraph("<b>Total Components</b>", body_style),
                Paragraph(str(project.get("total_components", 0)), body_style),
                Paragraph("<b>Direct Dependencies</b>", body_style),
                Paragraph(str(project.get("direct_count", 0)), body_style),
            ],
            [
                Paragraph("<b>Transitive Dependencies</b>", body_style),
                Paragraph(str(project.get("transitive_count", 0)), body_style),
                Paragraph("<b>Pinned Rate</b>", body_style),
                Paragraph(
                    f"{(project.get('pinned_count', 0) / max(project.get('total_components', 1), 1) * 100):.1f}%",
                    body_style,
                ),
            ],
            [
                Paragraph("<b>Critical / High Risks</b>", body_style),
                Paragraph(
                    f"<font color='#dc2626'><b>{project.get('critical_findings', 0) + project.get('high_findings', 0)}</b></font>",
                    body_style,
                ),
                Paragraph("<b>Medium / Low Risks</b>", body_style),
                Paragraph(
                    f"<font color='#d97706'><b>{project.get('medium_findings', 0) + project.get('low_findings', 0)}</b></font>",
                    body_style,
                ),
            ],
        ]

        t_metrics = Table(metrics_data, colWidths=[130, 135, 130, 135])
        t_metrics.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t_metrics)
        story.append(Spacer(1, 15))

        # 3. Supply Chain Findings Section
        story.append(Paragraph(f"Security & Anomaly Findings ({len(findings)})", h2_style))
        if not findings:
            story.append(Paragraph("No anomalies or security risks detected in project manifests.", body_style))
        else:
            for idx, f in enumerate(findings[:20], 1):  # Cap at top 20 for PDF readability
                sev_color = "#dc2626" if f["severity"] in ("CRITICAL", "HIGH") else ("#d97706" if f["severity"] == "MEDIUM" else "#2563eb")
                item_content = [
                    Paragraph(
                        f"<b>#{idx} [{f['severity']}] {f['title']}</b> (<font color='{sev_color}'>{f['category']}</font>)",
                        finding_title,
                    ),
                    Spacer(1, 2),
                    Paragraph(f"<b>Evidence:</b> {f.get('evidence', '')}", finding_body),
                    Spacer(1, 2),
                    Paragraph(f"<b>Explanation:</b> {f.get('explanation', '')}", finding_body),
                    Spacer(1, 2),
                    Paragraph(f"<b>Recommendation:</b> <font color='#15803d'>{f.get('recommendation', '')}</font>", finding_body),
                    Spacer(1, 6),
                ]
                story.append(KeepTogether(item_content))

        story.append(Spacer(1, 15))

        # 4. Software Bill of Materials (SBOM) Component Inventory Table
        story.append(Paragraph(f"Bill of Materials Component Inventory ({len(components)})", h2_style))

        table_header = [
            Paragraph("<b>Component Name</b>", body_style),
            Paragraph("<b>Version</b>", body_style),
            Paragraph("<b>Ecosystem</b>", body_style),
            Paragraph("<b>Type</b>", body_style),
            Paragraph("<b>Source File</b>", body_style),
        ]
        table_rows = [table_header]

        for c in components:
            table_rows.append(
                [
                    Paragraph(c["name"], body_style),
                    Paragraph(c.get("version") or "<font color='#dc2626'>unpinned</font>", body_style),
                    Paragraph(c.get("ecosystem", "").upper(), body_style),
                    Paragraph("Direct" if c.get("direct") else "Transitive", body_style),
                    Paragraph(c.get("source_file", "")[:25], body_style),
                ]
            )

        t_components = Table(table_rows, colWidths=[150, 90, 80, 80, 130])
        t_components.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(t_components)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
