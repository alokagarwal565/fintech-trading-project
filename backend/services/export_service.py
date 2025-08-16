from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from backend.models.models import User, Portfolio, Holding, RiskAssessment, Scenario
import json
import io
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import math

class ExportService:
    def __init__(self):
        self.chart_timeout = 3   # 3 seconds timeout for chart generation (much faster)
        self.pdf_timeout = 20    # 20 seconds timeout for PDF generation (reduced)
    
    def export_to_text(self, user: User, session: Session, include_risk_profile: bool = True, 
                      include_portfolio: bool = True, include_scenarios: bool = True) -> str:
        """
        Export user's analysis results to text format
        """
        content = []
        content.append("=" * 60)
        content.append("AI-POWERED RISK & SCENARIO ADVISOR REPORT")
        content.append("=" * 60)
        content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"User: {user.full_name or user.email}")
        content.append("")
        
        # Risk Profile Section
        if include_risk_profile and user.risk_assessments:
            latest_risk = sorted(user.risk_assessments, key=lambda x: x.created_at, reverse=True)[0]
            content.append("RISK TOLERANCE ASSESSMENT")
            content.append("-" * 30)
            content.append(f"Risk Category: {latest_risk.category}")
            content.append(f"Risk Score: {latest_risk.score}/24")
            content.append(f"Description: {latest_risk.description}")
            content.append("")
            content.append("Recommendations:")
            recommendations = json.loads(latest_risk.recommendations)
            for rec in recommendations:
                content.append(f"• {rec}")
            content.append("")
        
        # Portfolio Analysis Section
        if include_portfolio and user.portfolios:
            latest_portfolio = sorted(user.portfolios, key=lambda x: x.created_at, reverse=True)[0]
            holdings_stmt = select(Holding).where(Holding.portfolio_id == latest_portfolio.id)
            holdings = session.exec(holdings_stmt).all()
            
            content.append("PORTFOLIO ANALYSIS")
            content.append("-" * 20)
            content.append(f"Total Portfolio Value: ₹{latest_portfolio.total_value:,.2f}")
            content.append(f"Number of Holdings: {len(holdings)}")
            content.append("")
            content.append("Holdings Detail:")
            
            for holding in holdings:
                content.append(f"• {holding.company_name} ({holding.symbol})")
                content.append(f"  Quantity: {holding.quantity}")
                content.append(f"  Current Price: ₹{holding.current_price}")
                content.append(f"  Total Value: ₹{holding.total_value:,.2f}")
                content.append(f"  Sector: {holding.sector or 'Unknown'}")
                content.append("")
        
        # Scenario Analysis Section
        if include_scenarios and user.scenarios:
            content.append("SCENARIO ANALYSIS RESULTS")
            content.append("-" * 30)
            
            for i, scenario in enumerate(sorted(user.scenarios, key=lambda x: x.created_at, reverse=True)[:5], 1):
                content.append(f"Analysis {i}:")
                content.append(f"Date: {scenario.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                content.append(f"Scenario: {scenario.scenario_text}")
                content.append("")
                content.append("AI Analysis:")
                content.append(scenario.analysis_narrative)
                content.append("")
                
                insights = json.loads(scenario.insights)
                if insights:
                    content.append("Key Insights:")
                    for insight in insights:
                        content.append(f"• {insight}")
                    content.append("")
                
                recommendations = json.loads(scenario.recommendations)
                if recommendations:
                    content.append("Recommendations:")
                    for rec in recommendations:
                        content.append(f"• {rec}")
                    content.append("")
                
                if scenario.risk_assessment:
                    content.append("Risk Assessment:")
                    content.append(scenario.risk_assessment)
                    content.append("")
                
                # Add enhanced fields if they exist
                if scenario.risk_details:
                    try:
                        risk_details = json.loads(scenario.risk_details)
                        if risk_details:
                            content.append("Detailed Risk Analysis:")
                            for key, value in risk_details.items():
                                if isinstance(value, (int, float)):
                                    content.append(f"  {key.replace('_', ' ').title()}: {value}")
                                else:
                                    content.append(f"  {key.replace('_', ' ').title()}: {value}")
                            content.append("")
                    except:
                        pass
                
                if scenario.portfolio_impact:
                    try:
                        portfolio_impact = json.loads(scenario.portfolio_impact)
                        if portfolio_impact:
                            content.append("Portfolio Impact Analysis:")
                            for key, value in portfolio_impact.items():
                                if isinstance(value, (int, float)):
                                    content.append(f"  {key.replace('_', ' ').title()}: {value}")
                                else:
                                    content.append(f"  {key.replace('_', ' ').title()}: {value}")
                            content.append("")
                    except:
                        pass
                
                content.append("-" * 50)
                content.append("")
        
        content.append("END OF REPORT")
        content.append("=" * 60)
        
        return "\n".join(content)
    
    def create_sector_pie_chart(self, holdings: List[Holding]) -> Optional[Drawing]:
        """Create a pie chart for sector allocation with fast timeout protection"""
        if not holdings:
            return None
        
        start_time = time.time()
        
        try:
            # Group holdings by sector
            sector_data = {}
            for holding in holdings:
                sector = holding.sector or 'Unknown'
                if sector not in sector_data:
                    sector_data[sector] = 0
                sector_data[sector] += holding.total_value
            
            if not sector_data:
                return None
            
            # Check timeout immediately
            if time.time() - start_time > self.chart_timeout:
                print("⚠️ Chart generation timeout, skipping pie chart")
                return None
            
            # Create pie chart with minimal styling for speed
            drawing = Drawing(250, 150)  # Smaller size for speed
            pie = Pie()
            pie.x = 125
            pie.y = 75
            pie.width = 100
            pie.height = 100
            
            # Prepare data
            sectors = list(sector_data.keys())
            values = list(sector_data.values())
            
            pie.data = values
            pie.labels = sectors
            pie.slices.strokeWidth = 0.5
            
            # Add basic colors
            colors_list = [colors.blue, colors.green, colors.red, colors.orange, colors.purple]
            for i, slice in enumerate(pie.slices):
                slice.fillColor = colors_list[i % len(colors_list)]
            
            drawing.add(pie)
            
            # Simple legend for speed
            legend = Legend()
            legend.x = 200
            legend.y = 25
            legend.alignment = 'right'
            legend.fontName = 'Helvetica'
            legend.fontSize = 7
            legend.colorNamePairs = [(colors_list[i % len(colors_list)], sectors[i]) for i in range(len(sectors))]
            drawing.add(legend)
            
            return drawing
            
        except Exception as e:
            print(f"⚠️ Error creating pie chart: {e}")
            return None
    
    def create_holdings_bar_chart(self, holdings: List[Holding]) -> Optional[Drawing]:
        """Create a bar chart for holdings values with fast timeout protection"""
        if not holdings:
            return None
        
        start_time = time.time()
        
        try:
            # Sort holdings by value (top 6 for speed)
            sorted_holdings = sorted(holdings, key=lambda x: x.total_value, reverse=True)[:6]
            
            # Check timeout immediately
            if time.time() - start_time > self.chart_timeout:
                print("⚠️ Chart generation timeout, skipping bar chart")
                return None
            
            drawing = Drawing(300, 150)  # Smaller size for speed
            chart = VerticalBarChart()
            chart.x = 50
            chart.y = 25
            chart.width = 200
            chart.height = 100
            
            # Prepare data
            symbols = [h.symbol for h in sorted_holdings]
            values = [h.total_value for h in sorted_holdings]
            
            chart.data = [values]
            chart.categoryAxis.categoryNames = symbols
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = max(values) * 1.1
            
            # Basic styling for speed
            chart.bars[0].fillColor = colors.blue
            chart.bars[0].strokeColor = colors.black
            chart.bars[0].strokeWidth = 0.5
            
            drawing.add(chart)
            return drawing
            
        except Exception as e:
            print(f"⚠️ Error creating bar chart: {e}")
            return None
    
    def export_to_pdf_simple(self, user: User, session: Session, include_risk_profile: bool = True,
                     include_portfolio: bool = True, include_scenarios: bool = True) -> bytes:
        """
        Fallback PDF export method - creates a simple PDF without charts for reliability
        """
        try:
            print("🔄 Using fallback PDF generation method")
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                 leftMargin=0.5*inch, rightMargin=0.5*inch,
                                 topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            
            # Basic styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'SimpleTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'SimpleHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            normal_style = styles['Normal']
            
            # Title
            story.append(Paragraph("AI-Powered Risk & Scenario Advisor Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Paragraph(f"User: {user.full_name or user.email}", normal_style))
            story.append(Spacer(1, 20))
            
            # Risk Profile Section
            if include_risk_profile and user.risk_assessments:
                story.append(Paragraph("Risk Tolerance Assessment", heading_style))
                latest_risk = sorted(user.risk_assessments, key=lambda x: x.created_at, reverse=True)[0]
                
                risk_data = [
                    ['Risk Category', latest_risk.category],
                    ['Risk Score', f"{latest_risk.score}/24"],
                    ['Description', latest_risk.description]
                ]
                
                risk_table = Table(risk_data, colWidths=[1.5*inch, 4.5*inch])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                ]))
                
                story.append(risk_table)
                story.append(Spacer(1, 15))
                
                story.append(Paragraph("Recommendations:", heading_style))
                recommendations = json.loads(latest_risk.recommendations)
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", normal_style))
                
                story.append(Spacer(1, 20))
            
            # Portfolio Analysis Section
            if include_portfolio and user.portfolios:
                story.append(Paragraph("Portfolio Analysis", heading_style))
                
                latest_portfolio = sorted(user.portfolios, key=lambda x: x.created_at, reverse=True)[0]
                holdings_stmt = select(Holding).where(Holding.portfolio_id == latest_portfolio.id)
                holdings = session.exec(holdings_stmt).all()
                
                story.append(Paragraph(f"Total Portfolio Value: ₹{latest_portfolio.total_value:,.2f}", normal_style))
                story.append(Paragraph(f"Number of Holdings: {len(holdings)}", normal_style))
                story.append(Spacer(1, 15))
                
                # Simple holdings table
                holdings_data = [['Company', 'Symbol', 'Quantity', 'Value (₹)', 'Sector']]
                
                for holding in holdings:
                    company_name = holding.company_name
                    if len(company_name) > 20:
                        company_name = company_name[:17] + "..."
                    
                    holdings_data.append([
                        company_name,
                        holding.symbol,
                        str(holding.quantity),
                        f"₹{holding.total_value:,.0f}",
                        holding.sector or 'Unknown'
                    ])
                
                holdings_table = Table(holdings_data, colWidths=[2.5*inch, 0.8*inch, 0.7*inch, 1.2*inch, 1.0*inch])
                holdings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                
                story.append(holdings_table)
                story.append(Spacer(1, 20))
            
            # Scenario Analysis Section
            if include_scenarios and user.scenarios:
                story.append(Paragraph("Scenario Analysis Results", heading_style))
                
                latest_scenarios = sorted(user.scenarios, key=lambda x: x.created_at, reverse=True)[:2]  # Limit to 2 for simplicity
                
                for i, scenario in enumerate(latest_scenarios, 1):
                    story.append(Paragraph(f"Scenario {i}:", heading_style))
                    story.append(Paragraph(f"Date: {scenario.created_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                    story.append(Paragraph(f"Scenario: {scenario.scenario_text}", normal_style))
                    story.append(Spacer(1, 10))
                    
                    story.append(Paragraph("AI Analysis:", normal_style))
                    story.append(Paragraph(scenario.analysis_narrative, normal_style))
                    story.append(Spacer(1, 10))
                    
                    if scenario.risk_assessment:
                        story.append(Paragraph("Risk Assessment:", normal_style))
                        story.append(Paragraph(scenario.risk_assessment, normal_style))
                        story.append(Spacer(1, 10))
                    
                    if i < len(latest_scenarios):
                        story.append(PageBreak())
                        story.append(Spacer(1, 20))
            
            # Footer
            story.append(Spacer(1, 20))
            story.append(Paragraph("End of Report", normal_style))
            
            # Build PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            print("✅ Fallback PDF generated successfully")
            return pdf_data
            
        except Exception as e:
            print(f"❌ Fallback PDF generation also failed: {e}")
            buffer.close()
            # Final fallback to text
            text_content = self.export_to_text(user, session, include_risk_profile, include_portfolio, include_scenarios)
            return text_content.encode('utf-8')
    
    def export_to_pdf_fast(self, user: User, session: Session, include_risk_profile: bool = True,
                          include_portfolio: bool = True, include_scenarios: bool = True) -> bytes:
        """
        Ultra-fast PDF export method - no charts, minimal styling for maximum speed
        """
        try:
            print("⚡ Using ultra-fast PDF generation method")
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                 leftMargin=0.5*inch, rightMargin=0.5*inch,
                                 topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            
            # Basic styles for speed
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'FastTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=15,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'FastHeading',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            normal_style = styles['Normal']
            
            # Title
            story.append(Paragraph("AI-Powered Risk & Scenario Advisor Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Paragraph(f"User: {user.full_name or user.email}", normal_style))
            story.append(Spacer(1, 15))
            
            # Risk Profile Section
            if include_risk_profile and user.risk_assessments:
                story.append(Paragraph("Risk Tolerance Assessment", heading_style))
                latest_risk = sorted(user.risk_assessments, key=lambda x: x.created_at, reverse=True)[0]
                
                story.append(Paragraph(f"Risk Category: {latest_risk.category}", normal_style))
                story.append(Paragraph(f"Risk Score: {latest_risk.score}/24", normal_style))
                story.append(Paragraph(f"Description: {latest_risk.description}", normal_style))
                story.append(Spacer(1, 10))
                
                story.append(Paragraph("Recommendations:", heading_style))
                recommendations = json.loads(latest_risk.recommendations)
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", normal_style))
                
                story.append(Spacer(1, 15))
            
            # Portfolio Analysis Section
            if include_portfolio and user.portfolios:
                story.append(Paragraph("Portfolio Analysis", heading_style))
                
                latest_portfolio = sorted(user.portfolios, key=lambda x: x.created_at, reverse=True)[0]
                holdings_stmt = select(Holding).where(Holding.portfolio_id == latest_portfolio.id)
                holdings = session.exec(holdings_stmt).all()
                
                story.append(Paragraph(f"Total Portfolio Value: ₹{latest_portfolio.total_value:,.2f}", normal_style))
                story.append(Paragraph(f"Number of Holdings: {len(holdings)}", normal_style))
                story.append(Spacer(1, 10))
                
                # Simple holdings list for speed
                story.append(Paragraph("Holdings:", heading_style))
                for holding in holdings:
                    story.append(Paragraph(f"• {holding.company_name} ({holding.symbol}): {holding.quantity} shares @ ₹{holding.current_price:,.2f} = ₹{holding.total_value:,.0f}", normal_style))
                
                story.append(Spacer(1, 15))
            
            # Scenario Analysis Section
            if include_scenarios and user.scenarios:
                story.append(Paragraph("Scenario Analysis Results", heading_style))
                
                # Limit to 1 scenario for maximum speed
                latest_scenarios = sorted(user.scenarios, key=lambda x: x.created_at, reverse=True)[:1]
                
                for i, scenario in enumerate(latest_scenarios, 1):
                    story.append(Paragraph(f"Scenario {i}:", heading_style))
                    story.append(Paragraph(f"Date: {scenario.created_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                    story.append(Paragraph(f"Scenario: {scenario.scenario_text}", normal_style))
                    story.append(Spacer(1, 8))
                    
                    story.append(Paragraph("AI Analysis:", normal_style))
                    story.append(Paragraph(scenario.analysis_narrative, normal_style))
                    story.append(Spacer(1, 8))
                    
                    if scenario.risk_assessment:
                        story.append(Paragraph("Risk Assessment:", normal_style))
                        story.append(Paragraph(scenario.risk_assessment, normal_style))
                        story.append(Spacer(1, 8))
            
            # Footer
            story.append(Spacer(1, 15))
            story.append(Paragraph("End of Report", normal_style))
            
            # Build PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            print("✅ Ultra-fast PDF generated successfully")
            return pdf_data
            
        except Exception as e:
            print(f"❌ Ultra-fast PDF generation failed: {e}")
            buffer.close()
            # Final fallback to text
            text_content = self.export_to_text(user, session, include_risk_profile, include_portfolio, include_scenarios)
            return text_content.encode('utf-8')
    
    def export_to_pdf(self, user: User, session: Session, include_risk_profile: bool = True,
                     include_portfolio: bool = True, include_scenarios: bool = True) -> bytes:
        """
        Export user's analysis results to PDF format with improved formatting (NO CHARTS) for maximum speed
        """
        start_time = time.time()
        enable_charts = False  # Charts completely disabled for maximum speed
        
        try:
            print(f"📄 Starting PDF export for user {user.email} (charts disabled for speed)")
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                 leftMargin=0.5*inch, rightMargin=0.5*inch,
                                 topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            
            # Enhanced Styles
            styles = getSampleStyleSheet()
            
            # Title style with better formatting
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                textColor=colors.darkblue
            )
            
            # Section heading style
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=15,
                spaceBefore=20,
                fontName='Helvetica-Bold',
                textColor=colors.darkblue,
                borderWidth=1,
                borderColor=colors.lightgrey,
                borderPadding=5,
                backColor=colors.lightgrey
            )
            
            # Subheading style
            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold',
                textColor=colors.darkblue
            )
            
            # Normal text style with better spacing
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                fontName='Helvetica',
                alignment=TA_LEFT,
                leading=14
            )
            
            # Title and metadata
            story.append(Paragraph("AI-Powered Risk & Scenario Advisor Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Paragraph(f"User: {user.full_name or user.email}", normal_style))
            story.append(Spacer(1, 25))
            
            # Add page header and footer styles
            header_footer_style = ParagraphStyle(
                'HeaderFooter',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=0,
                spaceBefore=0
            )
            
            # Add page header
            story.append(Paragraph("─" * 80, header_footer_style))
            story.append(Paragraph("AI-Powered Risk & Scenario Advisor – Export Report", header_footer_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | User: {user.full_name or user.email}", header_footer_style))
            story.append(Paragraph("─" * 80, header_footer_style))
            story.append(Spacer(1, 20))
            
            # Risk Profile Section
            if include_risk_profile and user.risk_assessments:
                print("📊 Adding risk profile section")
                story.append(Paragraph("Risk Tolerance Assessment", heading_style))
                
                latest_risk = sorted(user.risk_assessments, key=lambda x: x.created_at, reverse=True)[0]
                
                # Risk summary table with better formatting
                risk_data = [
                    ['Risk Category', latest_risk.category],
                    ['Risk Score', f"{latest_risk.score}/24"]
                ]
                
                # Calculate column widths based on content - give more space to Description
                risk_table = Table(risk_data, colWidths=[1.2*inch, 4.8*inch])  # Reduced first column, increased second
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Add left padding for better text spacing
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),  # Add right padding for better text spacing
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.white]),  # Better row highlighting
                ]))
                
                story.append(risk_table)
                story.append(Spacer(1, 15))
                
                # Show description separately for better readability
                story.append(Paragraph("Description:", subheading_style))
                story.append(Paragraph(latest_risk.description, normal_style))
                story.append(Spacer(1, 15))
                
                # Recommendations with better formatting
                story.append(Paragraph("Recommendations:", subheading_style))
                recommendations = json.loads(latest_risk.recommendations)
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", normal_style))
                
                story.append(Spacer(1, 25))
            
            # Portfolio Analysis Section
            if include_portfolio and user.portfolios:
                print("📈 Adding portfolio analysis section")
                story.append(Paragraph("Portfolio Analysis", heading_style))
                
                latest_portfolio = sorted(user.portfolios, key=lambda x: x.created_at, reverse=True)[0]
                holdings_stmt = select(Holding).where(Holding.portfolio_id == latest_portfolio.id)
                holdings = session.exec(holdings_stmt).all()
                
                # Portfolio summary
                story.append(Paragraph(f"Total Portfolio Value: ₹{latest_portfolio.total_value:,.2f}", subheading_style))
                story.append(Paragraph(f"Number of Holdings: {len(holdings)}", normal_style))
                story.append(Spacer(1, 15))
                
                # Charts completely disabled for speed
                print("📊 Charts disabled for maximum speed")
                
                # Add sector summary text instead of charts
                if holdings:
                    sector_summary = {}
                    for holding in holdings:
                        sector = holding.sector or 'Unknown'
                        if sector not in sector_summary:
                            sector_summary[sector] = {'count': 0, 'value': 0}
                        sector_summary[sector]['count'] += 1
                        sector_summary[sector]['value'] += holding.total_value
                    
                    if sector_summary:
                        story.append(Paragraph("Sector Allocation Summary:", subheading_style))
                        for sector, data in sector_summary.items():
                            percentage = (data['value'] / latest_portfolio.total_value) * 100
                            story.append(Paragraph(f"• {sector}: {data['count']} holdings, ₹{data['value']:,.0f} ({percentage:.1f}%)", normal_style))
                        story.append(Spacer(1, 15))
                
                # Holdings table with improved formatting
                print("📋 Creating holdings table")
                holdings_data = [['Company', 'Symbol', 'Quantity', 'Price (₹)', 'Value (₹)', 'Sector']]
                
                for holding in holdings:
                    # Truncate long company names for better table display
                    company_name = holding.company_name
                    if len(company_name) > 25:
                        company_name = company_name[:22] + "..."
                    
                    holdings_data.append([
                        company_name,
                        holding.symbol,
                        str(holding.quantity),
                        f"₹{holding.current_price:,.2f}",
                        f"₹{holding.total_value:,.0f}",
                        holding.sector or 'Unknown'
                    ])
                
                # Calculate optimal column widths
                col_widths = [2.2*inch, 0.8*inch, 0.7*inch, 1.0*inch, 1.2*inch, 1.1*inch]
                holdings_table = Table(holdings_data, colWidths=col_widths)
                
                holdings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(holdings_table)
                story.append(Spacer(1, 25))
            
            # Scenario Analysis Section - COMPLETELY REWRITTEN
            if include_scenarios and user.scenarios:
                print("🔮 Adding scenario analysis section")
                story.append(Paragraph("Scenario Analysis Results", heading_style))
                
                # Get latest scenarios (limit to 2 for PDF readability and speed)
                latest_scenarios = sorted(user.scenarios, key=lambda x: x.created_at, reverse=True)[:2]
                
                for i, scenario in enumerate(latest_scenarios, 1):
                    print(f"📝 Processing scenario {i}/{len(latest_scenarios)}")
                    
                    # Add page break for scenarios after the first one
                    if i > 1:
                        story.append(PageBreak())
                        story.append(Spacer(1, 20))
                    
                    # Scenario Header with clear structure
                    story.append(Paragraph(f"Scenario Analysis {i}", subheading_style))
                    story.append(Paragraph(f"Date: {scenario.created_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                    story.append(Paragraph(f"Scenario: {scenario.scenario_text}", normal_style))
                    story.append(Spacer(1, 15))
                    
                    # AI Analysis narrative with proper formatting
                    if scenario.analysis_narrative:
                        story.append(Paragraph("AI Analysis:", subheading_style))
                        # Clean up any markdown-like syntax and ensure proper text wrapping
                        clean_narrative = scenario.analysis_narrative.replace('###', '').replace('**', '').replace('*', '')
                        story.append(Paragraph(clean_narrative, normal_style))
                        story.append(Spacer(1, 15))
                    
                    # Key Insights with proper bullet formatting
                    try:
                        insights = json.loads(scenario.insights) if scenario.insights else []
                        if insights:
                            story.append(Paragraph("Key Insights:", subheading_style))
                            for insight in insights:
                                # Clean up any markdown-like syntax
                                clean_insight = insight.replace('###', '').replace('**', '').replace('*', '')
                                story.append(Paragraph(f"• {clean_insight}", normal_style))
                            story.append(Spacer(1, 15))
                    except:
                        pass
                    
                    # Recommendations with proper bullet formatting
                    try:
                        recommendations = json.loads(scenario.recommendations) if scenario.recommendations else []
                        if recommendations:
                            story.append(Paragraph("Recommendations:", subheading_style))
                            for rec in recommendations:
                                # Clean up any markdown-like syntax
                                clean_rec = rec.replace('###', '').replace('**', '').replace('*', '')
                                story.append(Paragraph(f"• {clean_rec}", normal_style))
                            story.append(Spacer(1, 15))
                    except:
                        pass
                    
                    # Risk Assessment with structured display
                    if scenario.risk_assessment:
                        story.append(Paragraph("Risk Assessment:", subheading_style))
                        # Clean up any markdown-like syntax
                        clean_risk = scenario.risk_assessment.replace('###', '').replace('**', '').replace('*', '')
                        story.append(Paragraph(clean_risk, normal_style))
                        story.append(Spacer(1, 15))
                    
                    # Enhanced Risk Details with structured table
                    if scenario.risk_details:
                        try:
                            risk_details = json.loads(scenario.risk_details)
                            if risk_details:
                                story.append(Paragraph("Detailed Risk Analysis:", subheading_style))
                                
                                # Create structured table for risk details
                                risk_table_data = [['Risk Metric', 'Value']]
                                for key, value in risk_details.items():
                                    if isinstance(value, (int, float)):
                                        risk_table_data.append([key.replace('_', ' ').title(), f"{value:.2f}"])
                                    else:
                                        risk_table_data.append([key.replace('_', ' ').title(), str(value)])
                                
                                if len(risk_table_data) > 1:  # Only create table if we have data
                                    risk_details_table = Table(risk_table_data, colWidths=[2.5*inch, 2.5*inch])
                                    risk_details_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                                        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                                    ]))
                                    story.append(risk_details_table)
                                    story.append(Spacer(1, 15))
                        except:
                            pass
                    
                    # Portfolio Impact Analysis with structured tables
                    if scenario.portfolio_impact:
                        try:
                            portfolio_impact = json.loads(scenario.portfolio_impact)
                            if portfolio_impact:
                                story.append(Paragraph("Portfolio Impact Analysis:", subheading_style))
                                
                                # Create structured table for portfolio impact metrics
                                impact_table_data = [['Impact Metric', 'Value']]
                                for key, value in portfolio_impact.items():
                                    if key != 'affected_sectors':  # Handle sectors separately
                                        if isinstance(value, (int, float)):
                                            impact_table_data.append([key.replace('_', ' ').title(), f"{value:.4f}"])
                                        else:
                                            impact_table_data.append([key.replace('_', ' ').title(), str(value)])
                                
                                if len(impact_table_data) > 1:  # Only create table if we have data
                                    impact_table = Table(impact_table_data, colWidths=[2.5*inch, 2.5*inch])
                                    impact_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                                        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                                    ]))
                                    story.append(impact_table)
                                    story.append(Spacer(1, 15))
                                
                                # Handle affected sectors if they exist
                                if 'affected_sectors' in portfolio_impact and portfolio_impact['affected_sectors']:
                                    try:
                                        affected_sectors = portfolio_impact['affected_sectors']
                                        if isinstance(affected_sectors, list) and affected_sectors:
                                            story.append(Paragraph("Affected Sectors:", subheading_style))
                                            
                                            # Create structured table for affected sectors
                                            sectors_table_data = [['Sector', 'Weight %', 'Impact', 'Risk Level']]
                                            for sector_data in affected_sectors:
                                                if isinstance(sector_data, dict):
                                                    sector = sector_data.get('sector', 'Unknown')
                                                    weight = sector_data.get('weight', 0)
                                                    impact = sector_data.get('impact', 'Unknown')
                                                    risk_level = sector_data.get('risk_level', 'Unknown')
                                                    
                                                    sectors_table_data.append([
                                                        str(sector),
                                                        f"{weight:.1f}%" if isinstance(weight, (int, float)) else str(weight),
                                                        str(impact),
                                                        str(risk_level)
                                                    ])
                                            
                                            if len(sectors_table_data) > 1:  # Only create table if we have data
                                                sectors_table = Table(sectors_table_data, colWidths=[1.5*inch, 1.0*inch, 1.5*inch, 1.0*inch])
                                                sectors_table.setStyle(TableStyle([
                                                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                                                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                                                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                                                ]))
                                                story.append(sectors_table)
                                                story.append(Spacer(1, 15))
                                    except:
                                        pass
                        except:
                            pass
                    
                    # Portfolio Composition if available
                    if scenario.portfolio_composition:
                        try:
                            portfolio_composition = json.loads(scenario.portfolio_composition)
                            if portfolio_composition:
                                story.append(Paragraph("Portfolio Composition:", subheading_style))
                                
                                # Create structured table for portfolio composition
                                comp_table_data = [['Component', 'Details']]
                                for key, value in portfolio_composition.items():
                                    if isinstance(value, (int, float)):
                                        comp_table_data.append([key.replace('_', ' ').title(), f"{value:.2f}"])
                                    else:
                                        comp_table_data.append([key.replace('_', ' ').title(), str(value)])
                                
                                if len(comp_table_data) > 1:  # Only create table if we have data
                                    comp_table = Table(comp_table_data, colWidths=[2.0*inch, 3.0*inch])
                                    comp_table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                                        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                                    ]))
                                    story.append(comp_table)
                                    story.append(Spacer(1, 15))
                        except:
                            pass
                    
                    # Add separator between scenarios
                    if i < len(latest_scenarios):
                        story.append(Spacer(1, 20))
                        story.append(Paragraph("─" * 80, normal_style))  # Visual separator
                        story.append(Spacer(1, 20))
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph("─" * 80, header_footer_style))
            story.append(Paragraph("End of Report", normal_style))
            story.append(Paragraph("Generated by AI-Powered Risk & Scenario Advisor", header_footer_style))
            story.append(Paragraph("─" * 80, header_footer_style))
            
            # Build PDF
            print("🔨 Building PDF document")
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            generation_time = time.time() - start_time
            print(f"✅ PDF generated successfully in {generation_time:.2f} seconds")
            
            return pdf_data
            
        except Exception as e:
            print(f"❌ PDF generation error: {e}")
            buffer.close()
            print("🔄 Attempting fallback PDF generation...")
            # Try fallback PDF generation
            try:
                return self.export_to_pdf_simple(user, session, include_risk_profile, include_portfolio, include_scenarios)
            except:
                print("🔄 Fallback PDF failed, trying ultra-fast method...")
                # Try ultra-fast method
                try:
                    return self.export_to_pdf_fast(user, session, include_risk_profile, include_portfolio, include_scenarios)
                except:
                    # Final fallback to text
                    text_content = self.export_to_text(user, session, include_risk_profile, include_portfolio, include_scenarios)
                    return text_content.encode('utf-8')