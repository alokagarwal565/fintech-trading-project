from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from backend.models.models import User, Portfolio, Holding, RiskAssessment, Scenario
import json
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ExportService:
    def __init__(self):
        pass
    
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
                
                content.append("-" * 50)
                content.append("")
        
        content.append("END OF REPORT")
        content.append("=" * 60)
        
        return "\n".join(content)
    
    def export_to_pdf(self, user: User, session: Session, include_risk_profile: bool = True,
                     include_portfolio: bool = True, include_scenarios: bool = True) -> bytes:
        """
        Export user's analysis results to PDF format
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            normal_style = styles['Normal']
            
            # Title
            story.append(Paragraph("AI-Powered Risk & Scenario Advisor Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Paragraph(f"User: {user.full_name or user.email}", normal_style))
            story.append(Spacer(1, 20))
            
            # Risk Profile Section
            if include_risk_profile and user.risk_assessments:
                latest_risk = sorted(user.risk_assessments, key=lambda x: x.created_at, reverse=True)[0]
                story.append(Paragraph("Risk Tolerance Assessment", heading_style))
                
                risk_data = [
                    ['Risk Category', latest_risk.category],
                    ['Risk Score', f"{latest_risk.score}/24"],
                    ['Description', latest_risk.description]
                ]
                
                risk_table = Table(risk_data, colWidths=[2*inch, 4*inch])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(risk_table)
                story.append(Spacer(1, 12))
                
                story.append(Paragraph("Recommendations:", normal_style))
                recommendations = json.loads(latest_risk.recommendations)
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", normal_style))
                
                story.append(Spacer(1, 20))
            
            # Portfolio Analysis Section
            if include_portfolio and user.portfolios:
                latest_portfolio = sorted(user.portfolios, key=lambda x: x.created_at, reverse=True)[0]
                holdings_stmt = select(Holding).where(Holding.portfolio_id == latest_portfolio.id)
                holdings = session.exec(holdings_stmt).all()
                
                story.append(Paragraph("Portfolio Analysis", heading_style))
                story.append(Paragraph(f"Total Portfolio Value: ₹{latest_portfolio.total_value:,.2f}", normal_style))
                story.append(Spacer(1, 12))
                
                # Holdings table
                holdings_data = [['Company', 'Symbol', 'Quantity', 'Price (₹)', 'Value (₹)', 'Sector']]
                
                for holding in holdings:
                    holdings_data.append([
                        holding.company_name,
                        holding.symbol,
                        str(holding.quantity),
                        f"{holding.current_price}",
                        f"{holding.total_value:,.0f}",
                        holding.sector or 'Unknown'
                    ])
                
                holdings_table = Table(holdings_data, colWidths=[1.2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 1*inch, 1*inch])
                holdings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(holdings_table)
                story.append(Spacer(1, 20))
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            # Fallback to text export if PDF generation fails
            text_content = self.export_to_text(user, session, include_risk_profile, include_portfolio, include_scenarios)
            return text_content.encode('utf-8')