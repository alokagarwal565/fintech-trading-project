import google.generativeai as genai
from typing import Dict, List
import os

class ExplanationGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_portfolio_explanation(self, portfolio: List[Dict], metrics: Dict, risk_profile: str) -> str:
        """Generate a plain-English explanation of the portfolio"""
        
        portfolio_summary = self._format_portfolio_for_explanation(portfolio, metrics)
        
        prompt = f"""
        Explain this investment portfolio in simple, conversational language for a retail investor 
        with {risk_profile} risk tolerance:

        {portfolio_summary}

        Cover:
        1. Overall portfolio health and diversification
        2. Risk level assessment
        3. Sector concentration analysis
        4. Suggestions for improvement
        
        Keep it friendly and educational, avoid jargon.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def explain_risk_profile(self, risk_profile: str, risk_score: int) -> str:
        """Explain what the risk profile means"""
        
        prompt = f"""
        Explain in simple terms what it means to be a "{risk_profile}" investor with a risk score of {risk_score}/100.

        Include:
        1. What this risk profile typically means
        2. Suitable investment strategies
        3. What to expect in terms of returns and volatility
        4. Common mistakes to avoid

        Keep it conversational and encouraging.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate risk explanation: {str(e)}"
    
    def _format_portfolio_for_explanation(self, portfolio: List[Dict], metrics: Dict) -> str:
        """Format portfolio data for explanation"""
        total_value = metrics.get('total_value', 0)
        beta = metrics.get('weighted_beta', 1.0)
        sectors = metrics.get('sector_allocation', {})
        
        summary = f"Portfolio Value: ₹{total_value:,.2f}\n"
        summary += f"Portfolio Beta: {beta:.2f}\n"
        summary += f"Number of Holdings: {len(portfolio)}\n\n"
        
        summary += "Holdings:\n"
        for holding in sorted(portfolio, key=lambda x: x['total_value'], reverse=True):
            weight = holding.get('weight', 0) * 100
            summary += f"- {holding['company_name']}: ₹{holding['total_value']:,.2f} ({weight:.1f}%)\n"
        
        summary += f"\nSector Allocation:\n"
        for sector, weight in sectors.items():
            summary += f"- {sector}: {weight*100:.1f}%\n"
        
        return summary
