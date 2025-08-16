import os
import google.generativeai as genai
from typing import Dict, List, Any, Tuple
from backend.models.models import User, Portfolio, Holding
from sqlmodel import Session, select
from backend.utils.retry import retry_with_backoff
from backend.utils.logger import app_logger
import time
import re
from collections import defaultdict

class ScenarioService:
    """
    A service class to analyze market scenarios and their impact on a user's
    investment portfolio using the Gemini API with dynamic portfolio-aware analysis.
    """

    def __init__(self):
        """
        Initializes the ScenarioService and configures the Gemini API.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

    @retry_with_backoff(max_retries=2, base_delay=2.0, exceptions=(Exception,))
    def analyze_scenario(self, scenario: str, user: User, session: Session, portfolio_id: int = None) -> Dict[str, Any]:
        """
        Analyzes how a market scenario might affect the user's portfolio using dynamic analysis.

        Args:
            scenario (str): A description of the market scenario to analyze.
            user (User): The user object associated with the portfolio.
            session (Session): The SQLModel session for database access.
            portfolio_id (int, optional): The ID of a specific portfolio to analyze.
                                          If None, the user's latest portfolio is used.

        Returns:
            Dict[str, Any]: A dictionary containing the structured analysis with dynamic risk assessment.
        """
        try:
            app_logger.info(f"Starting scenario analysis for user {user.id}: {scenario[:50]}...")
            start_time = time.time()
            
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

            if not holdings:
                raise Exception("No holdings found in portfolio")

            # Get user's risk profile
            risk_profile = self._get_user_risk_profile(user, session)

            # Perform dynamic portfolio analysis
            portfolio_analysis = self._analyze_portfolio_composition(holdings)
            
            # Analyze scenario impact on portfolio
            impact_analysis = self._analyze_scenario_impact(scenario, portfolio_analysis)
            
            # Calculate dynamic risk assessment
            risk_assessment = self._calculate_dynamic_risk(portfolio_analysis, impact_analysis, risk_profile)
            
            # Generate AI-powered insights and recommendations
            ai_analysis = self._get_ai_analysis(scenario, portfolio_analysis, impact_analysis, risk_assessment)

            analysis_time = time.time() - start_time
            app_logger.info(f"Scenario analysis completed for user {user.id} in {analysis_time:.2f}s")
            
            return {
                'narrative': ai_analysis['narrative'],
                'insights': ai_analysis['insights'],
                'recommendations': ai_analysis['recommendations'],
                'risk_assessment': risk_assessment['level'],
                'risk_details': risk_assessment,
                'portfolio_impact': impact_analysis,
                'portfolio_composition': portfolio_analysis
            }

        except Exception as e:
            app_logger.error(f"Scenario analysis failed for user {user.id}: {str(e)}")
            return self._get_fallback_analysis(scenario, str(e))

    def _get_user_risk_profile(self, user: User, session: Session) -> Dict[str, Any]:
        """Get user's latest risk profile"""
        try:
            from backend.models.models import RiskAssessment
            risk_stmt = select(RiskAssessment).where(RiskAssessment.user_id == user.id).order_by(RiskAssessment.created_at.desc())
            latest_risk = session.exec(risk_stmt).first()
            
            if latest_risk:
                return {
                    'category': latest_risk.category,
                    'score': latest_risk.score,
                    'description': latest_risk.description
                }
        except Exception as e:
            app_logger.warning(f"Could not retrieve risk profile: {e}")
        
        return {'category': 'MODERATE', 'score': 5, 'description': 'No risk profile available'}

    def _analyze_portfolio_composition(self, holdings: List[Holding]) -> Dict[str, Any]:
        """
        Analyze portfolio composition for concentration, diversification, and sector exposure.
        """
        total_value = sum(holding.total_value for holding in holdings)
        
        # Sector analysis
        sector_allocation = defaultdict(float)
        sector_holdings = defaultdict(list)
        
        for holding in holdings:
            sector = holding.sector or 'Unknown'
            sector_allocation[sector] += holding.total_value
            sector_holdings[sector].append(holding)
        
        # Calculate sector percentages
        sector_percentages = {sector: (value / total_value) * 100 for sector, value in sector_allocation.items()}
        
        # Concentration analysis
        max_sector_exposure = max(sector_percentages.values()) if sector_percentages else 0
        top_3_sectors = sorted(sector_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
        concentration_score = sum(percentage for _, percentage in top_3_sectors)
        
        # Diversification metrics
        num_sectors = len(sector_allocation)
        num_holdings = len(holdings)
        avg_holding_size = total_value / num_holdings if num_holdings > 0 else 0
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        hhi = sum((percentage / 100) ** 2 for percentage in sector_percentages.values())
        
        return {
            'total_value': total_value,
            'num_holdings': num_holdings,
            'num_sectors': num_sectors,
            'sector_allocation': dict(sector_allocation),
            'sector_percentages': sector_percentages,
            'sector_holdings': {
                sector: [
                    {
                        'company_name': holding.company_name,
                        'symbol': holding.symbol,
                        'quantity': holding.quantity,
                        'current_price': holding.current_price,
                        'total_value': holding.total_value,
                        'sector': holding.sector
                    } for holding in holdings_list
                ] for sector, holdings_list in sector_holdings.items()
            },
            'max_sector_exposure': max_sector_exposure,
            'concentration_score': concentration_score,
            'hhi': hhi,
            'avg_holding_size': avg_holding_size,
            'diversification_level': self._calculate_diversification_level(hhi, num_sectors, max_sector_exposure)
        }

    def _calculate_diversification_level(self, hhi: float, num_sectors: int, max_exposure: float) -> str:
        """Calculate portfolio diversification level"""
        if hhi > 0.25 or max_exposure > 50:
            return "HIGH_CONCENTRATION"
        elif hhi > 0.15 or max_exposure > 30:
            return "MODERATE_CONCENTRATION"
        elif hhi > 0.08 or max_exposure > 20:
            return "MODERATE_DIVERSIFICATION"
        else:
            return "WELL_DIVERSIFIED"

    def _analyze_scenario_impact(self, scenario: str, portfolio_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how the scenario impacts the specific portfolio composition.
        """
        # Define sector impact mappings for common scenarios
        sector_impacts = self._get_sector_impact_mapping(scenario)
        
        # Calculate weighted impact on portfolio
        total_impact = 0
        sector_impacts_detailed = {}
        affected_sectors = []
        
        for sector, percentage in portfolio_analysis['sector_percentages'].items():
            impact_multiplier = sector_impacts.get(sector, 0)
            sector_impact = (percentage / 100) * impact_multiplier
            total_impact += sector_impact
            
            sector_impacts_detailed[sector] = {
                'portfolio_weight': percentage,
                'impact_multiplier': impact_multiplier,
                'weighted_impact': sector_impact
            }
            
            if impact_multiplier != 0:
                affected_sectors.append({
                    'sector': sector,
                    'weight': percentage,
                    'impact': impact_multiplier,
                    'risk_level': self._get_impact_risk_level(impact_multiplier)
                })
        
        # Sort affected sectors by impact
        affected_sectors.sort(key=lambda x: x['weight'] * abs(x['impact']), reverse=True)
        
        return {
            'total_impact_score': total_impact,
            'sector_impacts': sector_impacts_detailed,
            'affected_sectors': affected_sectors,
            'primary_risk_sectors': [s for s in affected_sectors if s['weight'] > 10 and abs(s['impact']) > 0.5],
            'impact_severity': self._get_impact_severity(total_impact),
            'scenario_type': self._classify_scenario_type(scenario)
        }

    def _get_sector_impact_mapping(self, scenario: str) -> Dict[str, float]:
        """
        Map scenario to sector impact multipliers.
        Returns impact multipliers: positive for positive impact, negative for negative impact.
        """
        scenario_lower = scenario.lower()
        
        # IT/Tech sector scenarios
        if any(keyword in scenario_lower for keyword in ['it', 'tech', 'software', 'technology', 'quarterly results']):
            return {
                'Technology': -0.8,
                'Financial Services': -0.2,
                'Healthcare': -0.1,
                'Consumer Goods': -0.1,
                'Industrials': -0.1
            }
        
        # Banking/Financial sector scenarios
        elif any(keyword in scenario_lower for keyword in ['bank', 'financial', 'rbi', 'repo rate', 'interest rate']):
            return {
                'Financial Services': -0.9,
                'Real Estate': -0.7,
                'Technology': -0.3,
                'Consumer Goods': -0.2,
                'Industrials': -0.2
            }
        
        # Oil/Energy scenarios
        elif any(keyword in scenario_lower for keyword in ['oil', 'energy', 'fuel', 'petroleum']):
            return {
                'Energy': 0.8,
                'Transportation': -0.6,
                'Consumer Goods': -0.3,
                'Industrials': -0.2,
                'Technology': -0.1
            }
        
        # Real Estate scenarios
        elif any(keyword in scenario_lower for keyword in ['real estate', 'property', 'housing', 'construction']):
            return {
                'Real Estate': -0.9,
                'Financial Services': -0.6,
                'Construction': -0.8,
                'Consumer Goods': -0.2,
                'Industrials': -0.3
            }
        
        # Pharmaceutical/Healthcare scenarios
        elif any(keyword in scenario_lower for keyword in ['pharma', 'healthcare', 'drug', 'medical']):
            return {
                'Healthcare': -0.8,
                'Technology': -0.1,
                'Consumer Goods': -0.1
            }
        
        # Regulatory scenarios
        elif any(keyword in scenario_lower for keyword in ['regulation', 'policy', 'government', 'regulatory']):
            return {
                'Financial Services': -0.5,
                'Technology': -0.4,
                'Healthcare': -0.3,
                'Consumer Goods': -0.2,
                'Industrials': -0.2
            }
        
        # Global economic scenarios
        elif any(keyword in scenario_lower for keyword in ['global', 'economic', 'recession', 'slowdown']):
            return {
                'Financial Services': -0.6,
                'Consumer Goods': -0.5,
                'Technology': -0.4,
                'Industrials': -0.4,
                'Real Estate': -0.5
            }
        
        # Default neutral impact
        return {}

    def _get_impact_risk_level(self, impact_multiplier: float) -> str:
        """Convert impact multiplier to risk level"""
        if abs(impact_multiplier) > 0.7:
            return "HIGH"
        elif abs(impact_multiplier) > 0.4:
            return "MEDIUM"
        elif abs(impact_multiplier) > 0.2:
            return "LOW"
        else:
            return "MINIMAL"

    def _get_impact_severity(self, total_impact: float) -> str:
        """Determine overall impact severity"""
        if abs(total_impact) > 0.5:
            return "HIGH"
        elif abs(total_impact) > 0.3:
            return "MEDIUM"
        elif abs(total_impact) > 0.1:
            return "LOW"
        else:
            return "MINIMAL"

    def _classify_scenario_type(self, scenario: str) -> str:
        """Classify the type of scenario"""
        scenario_lower = scenario.lower()
        
        if any(keyword in scenario_lower for keyword in ['quarterly', 'earnings', 'results']):
            return "COMPANY_SPECIFIC"
        elif any(keyword in scenario_lower for keyword in ['sector', 'industry']):
            return "SECTOR_WIDE"
        elif any(keyword in scenario_lower for keyword in ['policy', 'regulation', 'government']):
            return "REGULATORY"
        elif any(keyword in scenario_lower for keyword in ['global', 'economic', 'recession']):
            return "MACRO_ECONOMIC"
        else:
            return "CUSTOM"

    def _calculate_dynamic_risk(self, portfolio_analysis: Dict[str, Any], 
                               impact_analysis: Dict[str, Any], 
                               risk_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate dynamic risk assessment based on portfolio composition and scenario impact.
        """
        # Base risk factors
        concentration_risk = self._calculate_concentration_risk(portfolio_analysis)
        impact_risk = self._calculate_impact_risk(impact_analysis)
        diversification_risk = self._calculate_diversification_risk(portfolio_analysis)
        
        # Combined risk score (0-100)
        risk_score = (concentration_risk * 0.4 + impact_risk * 0.4 + diversification_risk * 0.2)
        
        # Determine risk level
        if risk_score > 75:
            risk_level = "CRITICAL"
        elif risk_score > 60:
            risk_level = "HIGH"
        elif risk_score > 40:
            risk_level = "MEDIUM"
        elif risk_score > 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            'level': risk_level,
            'score': risk_score,
            'concentration_risk': concentration_risk,
            'impact_risk': impact_risk,
            'diversification_risk': diversification_risk,
            'primary_factors': self._identify_primary_risk_factors(portfolio_analysis, impact_analysis),
            'confidence': self._calculate_confidence_level(portfolio_analysis, impact_analysis)
        }

    def _calculate_concentration_risk(self, portfolio_analysis: Dict[str, Any]) -> float:
        """Calculate risk from portfolio concentration"""
        max_exposure = portfolio_analysis['max_sector_exposure']
        hhi = portfolio_analysis['hhi']
        
        # High concentration risk if single sector > 50% or HHI > 0.25
        if max_exposure > 50 or hhi > 0.25:
            return 90
        elif max_exposure > 30 or hhi > 0.15:
            return 70
        elif max_exposure > 20 or hhi > 0.08:
            return 50
        else:
            return 20

    def _calculate_impact_risk(self, impact_analysis: Dict[str, Any]) -> float:
        """Calculate risk from scenario impact"""
        total_impact = abs(impact_analysis['total_impact_score'])
        primary_risks = len(impact_analysis['primary_risk_sectors'])
        
        if total_impact > 0.5 or primary_risks > 2:
            return 85
        elif total_impact > 0.3 or primary_risks > 1:
            return 65
        elif total_impact > 0.1:
            return 45
        else:
            return 20

    def _calculate_diversification_risk(self, portfolio_analysis: Dict[str, Any]) -> float:
        """Calculate risk from lack of diversification"""
        num_sectors = portfolio_analysis['num_sectors']
        num_holdings = portfolio_analysis['num_holdings']
        
        if num_sectors < 3 or num_holdings < 5:
            return 80
        elif num_sectors < 5 or num_holdings < 8:
            return 60
        elif num_sectors < 7 or num_holdings < 10:
            return 40
        else:
            return 20

    def _identify_primary_risk_factors(self, portfolio_analysis: Dict[str, Any], 
                                     impact_analysis: Dict[str, Any]) -> List[str]:
        """Identify primary risk factors"""
        factors = []
        
        if portfolio_analysis['max_sector_exposure'] > 30:
            factors.append(f"High concentration in {max(portfolio_analysis['sector_percentages'].items(), key=lambda x: x[1])[0]} sector")
        
        if portfolio_analysis['num_sectors'] < 5:
            factors.append("Limited sector diversification")
        
        if impact_analysis['total_impact_score'] > 0.3:
            factors.append("Significant scenario impact on portfolio")
        
        if len(impact_analysis['primary_risk_sectors']) > 1:
            factors.append("Multiple sectors at risk")
        
        return factors

    def _calculate_confidence_level(self, portfolio_analysis: Dict[str, Any], 
                                  impact_analysis: Dict[str, Any]) -> str:
        """Calculate confidence level in the analysis"""
        if (portfolio_analysis['num_holdings'] > 10 and 
            portfolio_analysis['num_sectors'] > 5 and 
            impact_analysis['scenario_type'] != 'CUSTOM'):
            return "HIGH"
        elif (portfolio_analysis['num_holdings'] > 5 and 
              portfolio_analysis['num_sectors'] > 3):
            return "MEDIUM"
        else:
            return "LOW"

    def _get_ai_analysis(self, scenario: str, portfolio_analysis: Dict[str, Any], 
                        impact_analysis: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-powered analysis with portfolio-specific insights.
        """
        try:
            # Create comprehensive prompt with portfolio data
            prompt = self._create_dynamic_prompt(scenario, portfolio_analysis, impact_analysis, risk_assessment)

            # Get AI analysis
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(contents=prompt)

            if response.text and response.text.strip():
                return self._parse_ai_response(response.text, portfolio_analysis, impact_analysis, risk_assessment)
            else:
                raise Exception("Empty response from AI model")

        except Exception as e:
            app_logger.error(f"AI analysis failed: {e}")
            return self._get_fallback_analysis(scenario, str(e))

    def _create_dynamic_prompt(self, scenario: str, portfolio_analysis: Dict[str, Any], 
                             impact_analysis: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
        """
        Create a dynamic prompt that includes portfolio-specific data.
        """
        # Format portfolio data
        portfolio_summary = f"""
PORTFOLIO COMPOSITION:
Total Value: ₹{portfolio_analysis['total_value']:,.2f}
Holdings: {portfolio_analysis['num_holdings']} stocks across {portfolio_analysis['num_sectors']} sectors
Diversification Level: {portfolio_analysis['diversification_level']}

SECTOR ALLOCATION:
"""
        for sector, percentage in portfolio_analysis['sector_percentages'].items():
            portfolio_summary += f"- {sector}: {percentage:.1f}%\n"

        # Format impact analysis
        impact_summary = f"""
SCENARIO IMPACT ANALYSIS:
Impact Severity: {impact_analysis['impact_severity']}
Total Impact Score: {impact_analysis['total_impact_score']:.2f}
Scenario Type: {impact_analysis['scenario_type']}

PRIMARY RISK SECTORS:
"""
        for sector_risk in impact_analysis['primary_risk_sectors']:
            impact_summary += f"- {sector_risk['sector']}: {sector_risk['weight']:.1f}% weight, {sector_risk['risk_level']} risk\n"

        # Format risk assessment
        risk_summary = f"""
RISK ASSESSMENT:
Risk Level: {risk_assessment['level']}
Risk Score: {risk_assessment['score']:.1f}/100
Confidence: {risk_assessment['confidence']}

PRIMARY RISK FACTORS:
"""
        for factor in risk_assessment['primary_factors']:
            risk_summary += f"- {factor}\n"

        prompt = f"""
You are an expert financial advisor analyzing the impact of a market scenario on a specific portfolio. 

SCENARIO: {scenario}

{portfolio_summary}

{impact_summary}

{risk_summary}

Provide a comprehensive analysis in the following structured format:

[OVERVIEW]
- 2-3 paragraphs explaining the specific impact on this portfolio
- Focus on the portfolio's unique characteristics and vulnerabilities
- Quantify potential impacts where possible

[KEY INSIGHTS]
- 4-5 specific insights about how this scenario affects the portfolio
- Include sector-specific implications and concentration risks
- Highlight any mitigating factors or opportunities

[ACTIONABLE RECOMMENDATIONS]
- 4-5 specific, prioritized recommendations for this portfolio
- Include immediate actions, monitoring points, and long-term strategies
- Consider the portfolio's current composition and risk profile

IMPORTANT: Base your analysis on the actual portfolio composition and scenario impact data provided. Be specific about how this particular portfolio is affected, not generic advice.
"""
        return prompt

    def _parse_ai_response(self, response_text: str, portfolio_analysis: Dict[str, Any], 
                          impact_analysis: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse AI response with portfolio-specific context.
        """
        try:
            # Split response into sections
            sections = self._extract_sections(response_text)
            
            narrative = sections.get('overview', response_text[:800] + "...")
            insights = sections.get('insights', [])
            recommendations = sections.get('recommendations', [])
            
            # Add portfolio-specific insights if AI didn't provide enough
            if len(insights) < 3:
                insights.extend(self._generate_portfolio_specific_insights(portfolio_analysis, impact_analysis))
            
            if len(recommendations) < 3:
                recommendations.extend(self._generate_portfolio_specific_recommendations(portfolio_analysis, risk_assessment))

            return {
                'narrative': narrative,
                'insights': insights[:6],
                'recommendations': recommendations[:6]
            }

        except Exception as e:
            app_logger.error(f"Error parsing AI response: {e}")
            return self._get_fallback_analysis("", str(e))

    def _extract_sections(self, text: str) -> Dict[str, Any]:
        """Extract sections from AI response"""
        sections = {'overview': '', 'insights': [], 'recommendations': []}
        
        lines = text.split('\n')
        current_section = 'overview'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '[OVERVIEW]' in line.upper():
                current_section = 'overview'
            elif '[KEY INSIGHTS]' in line.upper() or '[INSIGHTS]' in line.upper():
                current_section = 'insights'
            elif '[ACTIONABLE RECOMMENDATIONS]' in line.upper() or '[RECOMMENDATIONS]' in line.upper():
                current_section = 'recommendations'
            elif line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                if current_section == 'insights':
                    sections['insights'].append(line.lstrip('•-*123456789. '))
                elif current_section == 'recommendations':
                    sections['recommendations'].append(line.lstrip('•-*123456789. '))
            elif current_section == 'overview':
                sections['overview'] += line + '\n'
        
        return sections

    def _generate_portfolio_specific_insights(self, portfolio_analysis: Dict[str, Any], 
                                            impact_analysis: Dict[str, Any]) -> List[str]:
        """Generate portfolio-specific insights"""
        insights = []
        
        # Concentration insights
        if portfolio_analysis['max_sector_exposure'] > 30:
            max_sector = max(portfolio_analysis['sector_percentages'].items(), key=lambda x: x[1])
            insights.append(f"Portfolio is heavily concentrated in {max_sector[0]} sector ({max_sector[1]:.1f}%), increasing vulnerability to sector-specific shocks")
        
        # Diversification insights
        if portfolio_analysis['num_sectors'] < 5:
            insights.append(f"Limited diversification across only {portfolio_analysis['num_sectors']} sectors reduces portfolio resilience to sector-specific risks")
        
        # Impact insights
        if impact_analysis['primary_risk_sectors']:
            risk_sectors = [s['sector'] for s in impact_analysis['primary_risk_sectors']]
            insights.append(f"Scenario directly impacts {len(risk_sectors)} key sectors: {', '.join(risk_sectors)}")
        
        return insights

    def _generate_portfolio_specific_recommendations(self, portfolio_analysis: Dict[str, Any], 
                                                   risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate portfolio-specific recommendations"""
        recommendations = []
        
        # Concentration recommendations
        if portfolio_analysis['max_sector_exposure'] > 30:
            recommendations.append("Consider reducing exposure to the largest sector to improve diversification")
        
        # Diversification recommendations
        if portfolio_analysis['num_sectors'] < 5:
            recommendations.append("Explore opportunities to add exposure to additional sectors for better risk distribution")
        
        # Risk-based recommendations
        if risk_assessment['level'] in ['HIGH', 'CRITICAL']:
            recommendations.append("Implement defensive positioning and consider increasing cash allocation")
        
        return recommendations

    def _get_fallback_analysis(self, scenario: str, error: str) -> Dict[str, Any]:
        """
        Provides fallback analysis when the AI fails.
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
