import os
import google.generativeai as genai
from typing import Dict, List, Any
from backend.models.models import User, Portfolio, Holding
from sqlmodel import Session, select

class ScenarioService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
    
    def analyze_scenario(self, scenario: str, user: User, session: Session, portfolio_id: int = None) -> Dict[str, Any]:
        """
        Analyze how a market scenario might affect the user's portfolio using Gemini AI
        """
        try:
            # Get user's latest portfolio if portfolio_id not specified
            if portfolio_id:
                portfolio_stmt = select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
                portfolio = session.exec(portfolio_stmt).first()
            else:
                portfolio_stmt = select(Portfolio).where(Portfolio.user_id == user.id).order_by(Portfolio.created_at.desc())
                portfolio = session.exec(portfolio_stmt).first()
            
            if not portfolio:
                raise Exception("No portfolio found for analysis")
            
            # Get portfolio holdings
            holdings_stmt = select(Holding).where(Holding.portfolio_id == portfolio.id)
            holdings = session.exec(holdings_stmt).all()
            
            # Get user's risk profile
            risk_profile = None
            if user.risk_assessments:
                latest_assessment = sorted(user.risk_assessments, key=lambda x: x.created_at, reverse=True)[0]
                risk_profile = {
                    'category': latest_assessment.category,
                    'description': latest_assessment.description
                }
            
            # Prepare portfolio context
            portfolio_context = self._prepare_portfolio_context(holdings)
            risk_context = f"Risk Profile: {risk_profile['category']} - {risk_profile['description']}" if risk_profile else "No risk profile available"
            
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(scenario, portfolio_context, risk_context)
            
            # Get AI analysis
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(contents=prompt)
            
            if response.text and response.text.strip():
                # Parse the structured response
                analysis_result = self._parse_ai_response(response.text)
                return analysis_result
            else:
                raise Exception(f"Empty or invalid response from AI model")
                
        except Exception as e:
            return self._get_fallback_analysis(scenario, str(e))
    
    def _prepare_portfolio_context(self, holdings: List[Holding]) -> str:
        """
        Prepare portfolio information for AI analysis
        """
        if not holdings:
            return "No portfolio holdings provided."
        
        context = "Portfolio Holdings:\n"
        total_value = sum(holding.total_value for holding in holdings)
        
        for holding in holdings:
            percentage = (holding.total_value / total_value) * 100 if total_value > 0 else 0
            context += f"- {holding.company_name} ({holding.sector}): ₹{holding.total_value:,.2f} ({percentage:.1f}% of portfolio)\n"
        
        context += f"\nTotal Portfolio Value: ₹{total_value:,.2f}\n"
        
        # Add sector diversification info
        sectors = {}
        for holding in holdings:
            sector = holding.sector or 'Unknown'
            sectors[sector] = sectors.get(sector, 0) + holding.total_value
        
        context += "\nSector Allocation:\n"
        for sector, value in sectors.items():
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            context += f"- {sector}: ₹{value:,.2f} ({percentage:.1f}%)\n"
        
        return context
    
    def _create_analysis_prompt(self, scenario: str, portfolio_context: str, risk_context: str) -> str:
        """
        Create a comprehensive prompt for AI analysis
        """
        prompt = f"""
You are an expert financial advisor specializing in Indian stock markets. Analyze the following market scenario and its potential impact on the provided portfolio.

SCENARIO TO ANALYZE:
{scenario}

INVESTOR'S PORTFOLIO:
{portfolio_context}

INVESTOR'S RISK PROFILE:
{risk_context}

Please provide a comprehensive analysis in the following structured format:

NARRATIVE ANALYSIS:
Provide a detailed explanation (3-4 paragraphs) of how this scenario would likely affect the portfolio, considering:
- Direct impact on individual holdings and sectors
- Broader market implications
- Timeline considerations (short-term vs long-term effects)
- Indian market-specific factors

KEY INSIGHTS:
List 4-5 specific insights about:
- Which holdings are most/least vulnerable
- Sector rotation possibilities
- Market correlation effects
- Liquidity considerations

ACTIONABLE RECOMMENDATIONS:
Provide 4-5 specific, actionable recommendations such as:
- Portfolio adjustments to consider
- Hedging strategies if appropriate
- Timing considerations
- Risk management measures

RISK ASSESSMENT:
Evaluate the overall risk level of this scenario for the portfolio:
- Rate the impact severity (Low/Medium/High)
- Probability assessment
- Potential portfolio impact percentage
- Recommended monitoring indicators

Keep the analysis practical, specific to Indian markets, and tailored to the investor's risk profile. Use clear, professional language appropriate for retail investors.
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the AI response into structured components
        """
        try:
            # Split response into paragraphs
            paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
            
            narrative_parts = []
            insights = []
            recommendations = []
            risk_assessment_parts = []
            
            current_section = 'narrative'
            
            for paragraph in paragraphs:
                lines = paragraph.split('\n')
                paragraph_lower = paragraph.lower()
                
                if any(indicator in paragraph_lower for indicator in ['vulnerability', 'sector rotation', 'correlation', 'concentration']):
                    current_section = 'insights'
                elif any(indicator in paragraph_lower for indicator in ['reduce', 'increase cash', 'diversify', 'rebalancing', 'review investment']):
                    current_section = 'recommendations'  
                elif any(indicator in paragraph_lower for indicator in ['impact severity', 'probability assessment', 'potential portfolio impact', 'monitoring indicators']):
                    current_section = 'risk_assessment'
                
                if current_section == 'narrative':
                    narrative_parts.append(paragraph)
                elif current_section == 'insights':
                    for line in lines:
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                            clean_line = line.lstrip('0123456789. •-*').strip()
                            if clean_line:
                                insights.append(clean_line)
                        elif line and len(line) > 20:
                            insights.append(line)
                elif current_section == 'recommendations':
                    for line in lines:
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                            clean_line = line.lstrip('0123456789. •-*').strip()
                            if clean_line:
                                recommendations.append(clean_line)
                        elif line and len(line) > 20:
                            recommendations.append(line)
                elif current_section == 'risk_assessment':
                    risk_assessment_parts.append(paragraph)
            
            narrative = '\n\n'.join(narrative_parts[:3]) if narrative_parts else response_text[:500] + "..."
            risk_assessment = '\n\n'.join(risk_assessment_parts) if risk_assessment_parts else "Risk assessment completed - see full analysis above"
            
            if not insights:
                insights = [
                    "Portfolio concentration risk identified",
                    "Interest rate sensitivity affects holdings",
                    "Market correlation effects noted",
                    "Sector diversification recommended"
                ]
            
            if not recommendations:
                recommendations = [
                    "Consider portfolio diversification",
                    "Review asset allocation strategy", 
                    "Monitor key economic indicators",
                    "Consult with financial advisor for personalized guidance"
                ]
            
            insights = insights[:6]
            recommendations = recommendations[:6]
            
            return {
                'narrative': narrative,
                'insights': insights,
                'recommendations': recommendations,
                'risk_assessment': risk_assessment
            }
            
        except Exception as e:
            return {
                'narrative': response_text[:1000] + "..." if len(response_text) > 1000 else response_text,
                'insights': ["AI analysis completed - see narrative for details"],
                'recommendations': ["Review analysis and consult financial advisor"],
                'risk_assessment': "Please review the full analysis for risk implications"
            }
    
    def _get_fallback_analysis(self, scenario: str, error: str) -> Dict[str, Any]:
        """
        Provide fallback analysis when AI fails
        """
        return {
            'narrative': f"Unable to complete AI analysis for scenario: '{scenario}'. Error: {error}. Please try again later or consult with a financial advisor for scenario analysis.",
            'insights': [
                "AI analysis temporarily unavailable",
                "Consider general market volatility factors",
                "Review portfolio diversification",
                "Monitor relevant economic indicators"
            ],
            'recommendations': [
                "Retry analysis when AI service is available",
                "Consult financial news for scenario-related updates",
                "Review portfolio risk management strategies",
                "Consider professional financial advice"
            ],
            'risk_assessment': "Cannot assess risk without AI analysis. Please retry or seek professional advice."
        }