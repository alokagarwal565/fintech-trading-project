import streamlit as st
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def validate_environment() -> bool:
    """
    Validate that required environment variables are set
    """
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        st.write("Please set the following environment variables:")
        for var in missing_vars:
            st.code(f"{var}=your_{var.lower()}_here")
        return False
    
    return True

def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format currency amounts with proper symbols
    """
    if currency == "INR":
        return f"₹{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def export_to_text(risk_profile: Optional[Dict], portfolio_data: Optional[Dict], scenario_results: List[Dict]) -> str:
    """
    Export analysis results to text format
    """
    content = []
    content.append("=" * 60)
    content.append("AI-POWERED RISK & SCENARIO ADVISOR REPORT")
    content.append("=" * 60)
    content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    
    # Risk Profile Section
    if risk_profile:
        content.append("RISK TOLERANCE ASSESSMENT")
        content.append("-" * 30)
        content.append(f"Risk Category: {risk_profile['category']}")
        content.append(f"Risk Score: {risk_profile['score']}/24")
        content.append(f"Description: {risk_profile['description']}")
        content.append("")
        content.append("Recommendations:")
        for rec in risk_profile['recommendations']:
            content.append(f"• {rec}")
        content.append("")
    
    # Portfolio Analysis Section
    if portfolio_data and portfolio_data.get('valid_holdings'):
        content.append("PORTFOLIO ANALYSIS")
        content.append("-" * 20)
        content.append(f"Total Portfolio Value: ₹{portfolio_data['total_value']:,.2f}")
        content.append(f"Number of Holdings: {len(portfolio_data['valid_holdings'])}")
        content.append("")
        content.append("Holdings Detail:")
        
        for holding in portfolio_data['valid_holdings']:
            content.append(f"• {holding['Company']} ({holding['Symbol']})")
            content.append(f"  Quantity: {holding['Quantity']}")
            content.append(f"  Current Price: ₹{holding['Current Price (₹)']}")
            content.append(f"  Total Value: ₹{holding['Total Value (₹)']:,.2f}")
            content.append(f"  Sector: {holding.get('Sector', 'Unknown')}")
            content.append("")
        
        if portfolio_data.get('invalid_holdings'):
            content.append("Invalid Holdings:")
            for invalid in portfolio_data['invalid_holdings']:
                content.append(f"• {invalid}")
            content.append("")
    
    # Scenario Analysis Section
    if scenario_results:
        content.append("SCENARIO ANALYSIS RESULTS")
        content.append("-" * 30)
        
        for i, result in enumerate(scenario_results, 1):
            content.append(f"Analysis {i}:")
            content.append(f"Date: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            content.append(f"Scenario: {result['scenario']}")
            content.append("")
            content.append("AI Analysis:")
            content.append(result['analysis']['narrative'])
            content.append("")
            
            if result['analysis'].get('insights'):
                content.append("Key Insights:")
                for insight in result['analysis']['insights']:
                    content.append(f"• {insight}")
                content.append("")
            
            if result['analysis'].get('recommendations'):
                content.append("Recommendations:")
                for rec in result['analysis']['recommendations']:
                    content.append(f"• {rec}")
                content.append("")
            
            if result['analysis'].get('risk_assessment'):
                content.append("Risk Assessment:")
                content.append(result['analysis']['risk_assessment'])
                content.append("")
            
            content.append("-" * 50)
            content.append("")
    
    content.append("END OF REPORT")
    content.append("=" * 60)
    
    return "\n".join(content)

def export_to_pdf(risk_profile: Optional[Dict], portfolio_data: Optional[Dict], scenario_results: List[Dict]) -> bytes:
    """
    Export analysis results to PDF format
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
        story.append(Spacer(1, 20))
        
        # Risk Profile Section
        if risk_profile:
            story.append(Paragraph("Risk Tolerance Assessment", heading_style))
            
            risk_data = [
                ['Risk Category', risk_profile['category']],
                ['Risk Score', f"{risk_profile['score']}/24"],
                ['Description', risk_profile['description']]
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
            for rec in risk_profile['recommendations']:
                story.append(Paragraph(f"• {rec}", normal_style))
            
            story.append(Spacer(1, 20))
        
        # Portfolio Analysis Section
        if portfolio_data and portfolio_data.get('valid_holdings'):
            story.append(Paragraph("Portfolio Analysis", heading_style))
            story.append(Paragraph(f"Total Portfolio Value: ₹{portfolio_data['total_value']:,.2f}", normal_style))
            story.append(Spacer(1, 12))
            
            # Holdings table
            holdings_data = [['Company', 'Symbol', 'Quantity', 'Price (₹)', 'Value (₹)', 'Sector']]
            
            for holding in portfolio_data['valid_holdings']:
                holdings_data.append([
                    holding['Company'],
                    holding['Symbol'],
                    str(holding['Quantity']),
                    f"{holding['Current Price (₹)']}",
                    f"{holding['Total Value (₹)']:,.0f}",
                    holding.get('Sector', 'Unknown')
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
        
        # Scenario Analysis Section
        if scenario_results:
            story.append(Paragraph("Scenario Analysis Results", heading_style))
            
            for i, result in enumerate(scenario_results, 1):
                story.append(Paragraph(f"Analysis {i}: {result['scenario']}", normal_style))
                story.append(Paragraph(f"Date: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                story.append(Spacer(1, 8))
                
                story.append(Paragraph("AI Analysis:", normal_style))
                story.append(Paragraph(result['analysis']['narrative'], normal_style))
                story.append(Spacer(1, 8))
                
                if result['analysis'].get('insights'):
                    story.append(Paragraph("Key Insights:", normal_style))
                    for insight in result['analysis']['insights']:
                        story.append(Paragraph(f"• {insight}", normal_style))
                    story.append(Spacer(1, 8))
                
                if result['analysis'].get('recommendations'):
                    story.append(Paragraph("Recommendations:", normal_style))
                    for rec in result['analysis']['recommendations']:
                        story.append(Paragraph(f"• {rec}", normal_style))
                    story.append(Spacer(1, 8))
                
                if i < len(scenario_results):
                    story.append(PageBreak())
        
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        # Fallback to text export if PDF generation fails
        st.warning(f"PDF generation failed: {str(e)}. Generating text export instead.")
        text_content = export_to_text(risk_profile, portfolio_data, scenario_results)
        return text_content.encode('utf-8')

def display_error_message(error_type: str, message: str) -> None:
    """
    Display standardized error messages
    """
    error_icons = {
        'api': '🔌',
        'data': '📊',
        'input': '⚠️',
        'network': '🌐',
        'general': '❌'
    }
    
    icon = error_icons.get(error_type, '❌')
    st.error(f"{icon} {message}")

def display_info_message(message: str) -> None:
    """
    Display standardized info messages
    """
    st.info(f"ℹ️ {message}")

def display_success_message(message: str) -> None:
    """
    Display standardized success messages
    """
    st.success(f"✅ {message}")

def format_percentage(value: float) -> str:
    """
    Format percentage values
    """
    return f"{value:.1f}%"

def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    """
    if not text:
        return ""
    
    # Remove potentially harmful characters
    sanitized = text.strip()
    
    # Remove excessive whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized

def calculate_portfolio_concentration(holdings: List[Dict]) -> Dict[str, float]:
    """
    Calculate portfolio concentration metrics
    """
    if not holdings:
        return {}
    
    total_value = sum(holding.get('Total Value (₹)', 0) for holding in holdings)
    if total_value == 0:
        return {}
    
    # Calculate individual holdings percentages
    percentages = []
    for holding in holdings:
        value = holding.get('Total Value (₹)', 0)
        percentage = (value / total_value) * 100
        percentages.append(percentage)
    
    percentages.sort(reverse=True)
    
    return {
        'largest_holding': percentages[0] if percentages else 0,
        'top_3_holdings': sum(percentages[:3]) if len(percentages) >= 3 else sum(percentages),
        'top_5_holdings': sum(percentages[:5]) if len(percentages) >= 5 else sum(percentages),
        'herfindahl_index': sum(p**2 for p in percentages) / 100  # Normalized HHI
    }
