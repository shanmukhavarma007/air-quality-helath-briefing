import io
from datetime import datetime, timedelta
from loguru import logger
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.config import settings

class PDFReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        self.normal_style = self.styles['Normal']

    async def generate_weekly_exposure_report(
        self,
        user_email: str,
        user_name: str,
        location_label: str,
        weekly_data: list[dict]
    ) -> bytes:
        """
        Generate a weekly air quality exposure report in PDF format
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []

            # Title
            title = Paragraph("Weekly Air Quality Exposure Report", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))

            # User info
            user_info = f"""
            <b>User:</b> {user_name}<br/>
            <b>Email:</b> {user_email}<br/>
            <b>Location:</b> {location_label}<br/>
            <b>Report Period:</b> {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            story.append(Paragraph(user_info, self.normal_style))
            story.append(Spacer(1, 20))

            # Summary statistics
            if weekly_data:
                aqi_values = [day.get('aqi_value', 0) for day in weekly_data if day.get('aqi_value') is not None]
                if aqi_values:
                    avg_aqi = sum(aqi_values) / len(aqi_values)
                    max_aqi = max(aqi_values)
                    min_aqi = min(aqi_values)
                    
                    # AQI category function
                    def get_aqi_category(aqi):
                        if aqi <= 50: return "Good"
                        elif aqi <= 100: return "Moderate"
                        elif aqi <= 150: return "Unhealthy for Sensitive"
                        elif aqi <= 200: return "Unhealthy"
                        elif aqi <= 300: return "Very Unhealthy"
                        else: return "Hazardous"
                    
                    avg_category = get_aqi_category(int(avg_aqi))
                    max_category = get_aqi_category(int(max_aqi))

                    summary_data = [
                        ["Metric", "Value"],
                        ["Average AQI", f"{avg_aqi:.1f} ({avg_category})"],
                        ["Maximum AQI", f"{max_aqi} ({max_category})"],
                        ["Minimum AQI", f"{min_aqi} ({get_aqi_category(int(min_aqi))})"],
                        ["Days with AQI > 100", str(len([v for v in aqi_values if v > 100]))],
                        ["Days with AQI > 150", str(len([v for v in aqi_values if v > 150]))]
                    ]
                    
                    story.append(Paragraph("Weekly Summary", self.heading_style))
                    summary_table = Table(summary_data)
                    summary_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(summary_table)
                    story.append(Spacer(1, 20))

            # Daily breakdown
            story.append(Paragraph("Daily Breakdown", self.heading_style))
            
            if weekly_data:
                # Prepare table data
                table_data = [["Date", "AQI", "Category", "PM2.5 (µg/m³)", "Notes"]]
                
                for day in weekly_data:
                    date_str = day.get('date', 'Unknown')
                    aqi_val = day.get('aqi_value', 'N/A')
                    category = day.get('category', 'Unknown')
                    pm25 = day.get('pm25', 'N/A')
                    notes = day.get('notes', '')
                    
                    # Format AQI with color indication
                    if isinstance(aqi_val, (int, float)):
                        aqi_display = f"{aqi_val}"
                    else:
                        aqi_display = str(aqi_val)
                    
                    table_data.append([date_str, aqi_display, category, str(pm25), notes])
                
                daily_table = Table(table_data)
                daily_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(daily_table)
            else:
                story.append(Paragraph("No data available for the selected period.", self.normal_style))

            # Health recommendations
            story.append(Spacer(1, 20))
            story.append(Paragraph("Health Recommendations", self.heading_style))
            
            recommendations = [
                "• Limit outdoor activities when AQI exceeds 100",
                "• Consider wearing a mask (N95 or equivalent) when AQI exceeds 150",
                "• Keep windows closed and use air purifiers during poor air quality days",
                "• Schedule outdoor exercise for early morning when air quality is typically better",
                "• Stay hydrated and monitor for respiratory symptoms",
                "• Consult with healthcare provider if you have pre-existing conditions"
            ]
            
            for rec in recommendations:
                story.append(Paragraph(rec, self.normal_style))
                story.append(Spacer(1, 6))

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Generated weekly PDF report for {user_email}")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            # Return a simple error PDF or raise exception
            raise

    async def close(self):
        # Nothing to close for this service
        pass