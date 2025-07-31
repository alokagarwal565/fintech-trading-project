import streamlit as st
import os
import google.generativeai as genai # Keep this import as it's now correct
from google.generativeai import types
from typing import Dict, List, Any
import json

class ScenarioAnalyzer:
    def __init__(self):
        # Ensure GEMINI_API_KEY is loaded from .env
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
        
        # Configure the generative AI library with the API key
        genai.configure(api_key=api_key)
        
        # We don't need a self.client object anymore for direct model calls
        # The models are accessed directly via genai.GenerativeModel
        
    def analyze_scenario(self, scenario: str, portfolio_holdings: List[Dict], risk_profile: Dict) -> Dict[str, Any]:
        """
        Analyze how a market scenario might affect the portfolio using Gemini AI
        """
        try:
            # Prepare portfolio context
            portfolio_context = self._prepare_portfolio_context(portfolio_holdings)
            risk_context = f"Risk Profile: {risk_profile['category']} - {risk_profile['description']}"
            
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(scenario, portfolio_context, risk_context)
            
            # Get AI analysis
            # Access the model directly using genai.GenerativeModel
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                contents=prompt
            )
            
            if response.text and response.text.strip():
                # Parse the structured response
                analysis_result = self._parse_ai_response(response.text)
                return analysis_result
            else:
                raise Exception(f"Empty or invalid response from AI model. Response: {response}")
                
        except Exception as e:
            st.error(f"❌ Error in AI analysis: {str(e)}")
            # Add debugging info
            st.write(f"Portfolio holdings count: {len(portfolio_holdings)}")
            st.write(f"Risk profile available: {bool(risk_profile)}")
            return self._get_fallback_analysis(scenario)
    
    def _prepare_portfolio_context(self, holdings: List[Dict]) -> str:
        """
        Prepare portfolio information for AI analysis
        """
        if not holdings:
            return "No portfolio holdings provided."
        
        context = "Portfolio Holdings:\n"
        total_value = sum(holding.get('Total Value (₹)', 0) for holding in holdings)
        
        for holding in holdings:
            company = holding.get('Company', 'Unknown')
            sector = holding.get('Sector', 'Unknown')
            value = holding.get('Total Value (₹)', 0)
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            
            context += f"- {company} ({sector}): ₹{value:,.2f} ({percentage:.1f}% of portfolio)\n"
        
        context += f"\nTotal Portfolio Value: ₹{total_value:,.2f}\n"
        
        # Add sector diversification info
        sectors = {}
        for holding in holdings:
            sector = holding.get('Sector', 'Unknown')
            value = holding.get('Total Value (₹)', 0)
            sectors[sector] = sectors.get(sector, 0) + value
        
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
            # Since the AI returns a comprehensive response but not in the exact format we requested,
            # let's split it into logical sections based on content patterns
            
            # Split response into paragraphs
            paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
            
            narrative_parts = []
            insights = []
            recommendations = []
            risk_assessment_parts = []
            
            current_section = 'narrative'  # Start with narrative
            
            for paragraph in paragraphs:
                lines = paragraph.split('\n')
                
                # Check for section indicators in the paragraph
                paragraph_lower = paragraph.lower()
                
                if any(indicator in paragraph_lower for indicator in ['vulnerability', 'sector rotation', 'correlation', 'concentration']):
                    # This looks like insights content
                    current_section = 'insights'
                elif any(indicator in paragraph_lower for indicator in ['reduce', 'increase cash', 'diversify', 'rebalancing', 'review investment']):
                    # This looks like recommendations
                    current_section = 'recommendations'  
                elif any(indicator in paragraph_lower for indicator in ['impact severity', 'probability assessment', 'potential portfolio impact', 'monitoring indicators']):
                    # This looks like risk assessment
                    current_section = 'risk_assessment'
                
                # Process the content based on current section
                if current_section == 'narrative':
                    narrative_parts.append(paragraph)
                elif current_section == 'insights':
                    # Extract numbered or bulleted insights
                    for line in lines:
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                            # Clean up the line by removing bullets/numbers
                            clean_line = line.lstrip('0123456789. •-*').strip()
                            if clean_line:
                                insights.append(clean_line)
                        elif line and len(line) > 20:  # Substantial content
                            insights.append(line)
                elif current_section == 'recommendations':
                    # Extract numbered or bulleted recommendations
                    for line in lines:
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                            # Clean up the line by removing bullets/numbers
                            clean_line = line.lstrip('0123456789. •-*').strip()
                            if clean_line:
                                recommendations.append(clean_line)
                        elif line and len(line) > 20:  # Substantial content
                            recommendations.append(line)
                elif current_section == 'risk_assessment':
                    risk_assessment_parts.append(paragraph)
            
            # Compile final results
            narrative = '\n\n'.join(narrative_parts[:3]) if narrative_parts else response_text[:500] + "..."  # Limit narrative length
            risk_assessment = '\n\n'.join(risk_assessment_parts) if risk_assessment_parts else "Risk assessment completed - see full analysis above"
            
            # Ensure we have some insights and recommendations
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
            
            # Limit the number of insights and recommendations to avoid overwhelming the user
            insights = insights[:6]
            recommendations = recommendations[:6]
            
            return {
                'narrative': narrative,
                'insights': insights,
                'recommendations': recommendations,
                'risk_assessment': risk_assessment
            }
            
        except Exception as e:
            st.warning(f"Could not parse AI response structure: {str(e)}")
            return {
                'narrative': response_text[:1000] + "..." if len(response_text) > 1000 else response_text,
                'insights': ["AI analysis completed - see narrative for details"],
                'recommendations': ["Review analysis and consult financial advisor"],
                'risk_assessment': "Please review the full analysis for risk implications"
            }
    
    def _get_fallback_analysis(self, scenario: str) -> Dict[str, Any]:
        """
        Provide fallback analysis when AI fails
        """
        return {
            'narrative': f"Unable to complete AI analysis for scenario: '{scenario}'. This could be due to API limitations or connectivity issues. Please try again later or consult with a financial advisor for scenario analysis.",
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
    
    def get_predefined_scenarios(self) -> List[str]:
        """
        Get list of predefined market scenarios for Indian markets
        """
        return [
            "RBI increases repo rate by 0.5%",
            "Oil prices surge by 20% due to geopolitical tensions",
            "US Federal Reserve cuts interest rates by 0.25%",
            "Major IT company announces poor quarterly results",
            "Government announces new infrastructure spending of ₹10 lakh crores",
            "Global recession fears increase due to banking crisis",
            "New technology disrupts traditional banking sector",
            "Inflation rises to 7% affecting consumer spending",
            "Monsoon failure affects agricultural output",
            "Foreign institutional investors withdraw ₹50,000 crores",
            "Crude oil prices fall below $60 per barrel",
            "New government policy favors renewable energy sector",
            "Currency volatility: Rupee weakens to ₹85 per USD",
            "Corporate earnings growth slows to 5% across sectors",
            "Trade war escalation affects export-oriented companies"
        ]
    
    def analyze_correlation_impact(self, holdings: List[Dict], scenario_type: str) -> Dict[str, List[str]]:
        """
        Analyze which holdings might be most affected by scenario type
        """
        sector_impact_mapping = {
            'interest_rate': {
                'high_impact': ['Banking', 'Real Estate', 'Auto'],
                'medium_impact': ['Infrastructure', 'Capital Goods'],
                'low_impact': ['IT Services', 'Pharmaceuticals']
            },
            'oil_price': {
                'high_impact': ['Oil & Gas', 'Airlines', 'Auto'],
                'medium_impact': ['Chemicals', 'Paints'],
                'low_impact': ['IT Services', 'Pharmaceuticals']
            },
            'currency': {
                'high_impact': ['IT Services', 'Pharmaceuticals', 'Textiles'],
                'medium_impact': ['Chemicals', 'Auto'],
                'low_impact': ['Banking', 'Real Estate']
            },
            'general': {
                'high_impact': ['Small Cap', 'Mid Cap'],
                'medium_impact': ['Banking', 'Auto'],
                'low_impact': ['FMCG', 'Utilities']
            }
        }
        
        # Default to general impact if scenario type not recognized
        impact_map = sector_impact_mapping.get(scenario_type, sector_impact_mapping['general'])
        
        result = {'high_impact': [], 'medium_impact': [], 'low_impact': []}
        
        for holding in holdings:
            company = holding.get('Company', '')
            sector = holding.get('Sector', '')
            
            for impact_level, sectors in impact_map.items():
                if any(s.lower() in sector.lower() for s in sectors):
                    result[impact_level].append(company)
                    break
            else:
                result['medium_impact'].append(company)  # Default to medium impact
        
        return result
