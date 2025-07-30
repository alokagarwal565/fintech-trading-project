import google.generativeai as genai
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class ScenarioAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_scenario(self, scenario: str, portfolio: List[Dict], risk_profile: str, portfolio_metrics: Dict) -> Dict:
        """Analyze how a scenario might impact the portfolio"""
        
        # Prepare portfolio summary for the prompt
        portfolio_summary = self._prepare_portfolio_summary(portfolio, portfolio_metrics)
        
        prompt = f"""
        You are an expert financial advisor analyzing investment scenarios. 

        INVESTOR PROFILE:
        - Risk Tolerance: {risk_profile}
        - Portfolio Value: ₹{portfolio_metrics.get('total_value', 0):,.2f}
        - Portfolio Beta: {portfolio_metrics.get('weighted_beta', 1.0):.2f}
        - Number of Holdings: {portfolio_metrics.get('num_holdings', 0)}

        CURRENT PORTFOLIO:
        {portfolio_summary}

        SCENARIO TO ANALYZE:
        {scenario}

        Please provide a comprehensive analysis covering:

        1. IMMEDIATE IMPACT ASSESSMENT:
        - Which specific holdings would be most affected and why?
        - Estimated percentage impact on overall portfolio value
        - Timeline for potential effects (immediate, short-term, long-term)

        2. RISK ANALYSIS:
        - How does this scenario align with the investor's {risk_profile} risk profile?
        - What are the key risks and opportunities?
        - Probability assessment of the scenario occurring

        3. SECTOR/HOLDING SPECIFIC IMPACTS:
        - Detailed impact on each major holding
        - Sector rotation implications
        - Correlation effects across holdings

        4. ACTIONABLE RECOMMENDATIONS:
        - Immediate actions the investor should consider
        - Portfolio rebalancing suggestions
        - Risk mitigation strategies
        - Opportunities to capitalize on

        5. MONITORING STRATEGY:
        - Key indicators to watch
        - Early warning signals
        - Exit/entry criteria

        Please provide clear, actionable insights in simple language suitable for a retail investor.
        Use specific numbers and percentages where possible.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                'analysis': response.text,
                'scenario': scenario,
                'portfolio_value': portfolio_metrics.get('total_value', 0),
                'risk_profile': risk_profile
            }
        except Exception as e:
            return {
                'analysis': f"Error generating analysis: {str(e)}",
                'scenario': scenario,
                'portfolio_value': portfolio_metrics.get('total_value', 0),
                'risk_profile': risk_profile
            }
    
    def _prepare_portfolio_summary(self, portfolio: List[Dict], metrics: Dict) -> str:
        """Prepare a formatted portfolio summary for the AI prompt"""
        summary = ""
        
        for holding in portfolio:
            weight = holding.get('weight', 0) * 100
            summary += f"- {holding['company_name']} ({holding['ticker']}): {holding['quantity']} shares, "
            summary += f"₹{holding['total_value']:,.2f} ({weight:.1f}% of portfolio), "
            summary += f"Sector: {holding['sector']}, Beta: {holding.get('beta', 'N/A')}\n"
        
        # Add sector allocation
        sector_allocation = metrics.get('sector_allocation', {})
        if sector_allocation:
            summary += f"\nSECTOR ALLOCATION:\n"
            for sector, weight in sector_allocation.items():
                summary += f"- {sector}: {weight*100:.1f}%\n"
        
        return summary

    def generate_quick_suggestions(self, scenario: str, risk_profile: str) -> List[str]:
        """Generate quick actionable suggestions"""
        prompt = f"""
        As a financial advisor, provide 3-5 quick, actionable suggestions for a {risk_profile} risk investor 
        dealing with this scenario: {scenario}

        Format as bullet points, keep each suggestion under 25 words, focus on immediate actions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = response.text.strip().split('\n')
            return [s.strip('- ').strip() for s in suggestions if s.strip()]
        except:
            return ["Monitor your portfolio closely", "Consider consulting a financial advisor", "Review your risk tolerance"]
