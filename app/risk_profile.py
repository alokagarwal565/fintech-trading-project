import streamlit as st

class RiskProfiler:
    def __init__(self):
        self.risk_categories = {
            'Conservative': {
                'range': (6, 12),
                'description': "You prefer stable, low-risk investments with predictable returns. Capital preservation is more important than growth.",
                'recommendations': [
                    "Focus on large-cap, dividend-paying stocks",
                    "Consider government bonds and fixed deposits",
                    "Limit equity exposure to 30-40% of portfolio",
                    "Diversify across defensive sectors like FMCG and utilities"
                ]
            },
            'Moderate': {
                'range': (13, 19),
                'description': "You're comfortable with moderate risk for potentially higher returns. You can tolerate some volatility in pursuit of growth.",
                'recommendations': [
                    "Balance between large-cap and mid-cap stocks",
                    "Equity exposure can be 50-70% of portfolio",
                    "Include some growth sectors like technology and healthcare",
                    "Consider systematic investment plans (SIPs) for rupee cost averaging"
                ]
            },
            'Aggressive': {
                'range': (20, 24),
                'description': "You're willing to take high risks for potentially high returns. You can handle significant portfolio volatility.",
                'recommendations': [
                    "Focus on growth stocks and emerging sectors",
                    "Equity exposure can be 70-90% of portfolio",
                    "Include small-cap and mid-cap stocks",
                    "Consider thematic investments in new technologies"
                ]
            }
        }
    
    def assess_risk_tolerance(self, answers):
        """
        Assess risk tolerance based on questionnaire answers
        """
        # Scoring matrix for each question
        scoring = {
            # Question 1: Investment experience
            0: {"Less than 1 year": 1, "1-3 years": 2, "3-5 years": 3, "More than 5 years": 4},
            
            # Question 2: Risk comfort (portfolio loss scenario)
            1: {"Sell immediately": 1, "Sell some holdings": 2, "Hold and wait": 3, "Buy more": 4},
            
            # Question 3: Investment goals
            2: {"Capital preservation": 1, "Steady income": 2, "Moderate growth": 3, "Aggressive growth": 4},
            
            # Question 4: Time horizon
            3: {"Within 1 year": 1, "1-3 years": 2, "3-7 years": 3, "More than 7 years": 4},
            
            # Question 5: Income stability
            4: {"Very unstable": 1, "Somewhat unstable": 2, "Stable": 3, "Very stable": 4},
            
            # Question 6: Emergency fund
            5: {"No emergency fund": 1, "Less than 3 months": 2, "3-6 months": 3, "More than 6 months": 4}
        }
        
        # Calculate total score
        total_score = 0
        for i, answer in enumerate(answers):
            if answer in scoring[i]:
                total_score += scoring[i][answer]
        
        # Determine risk category
        category = "Conservative"
        for cat_name, cat_info in self.risk_categories.items():
            if cat_info['range'][0] <= total_score <= cat_info['range'][1]:
                category = cat_name
                break
        
        return {
            'score': total_score,
            'category': category,
            'description': self.risk_categories[category]['description'],
            'recommendations': self.risk_categories[category]['recommendations']
        }
    
    def get_risk_adjusted_advice(self, risk_category, portfolio_data):
        """
        Get personalized advice based on risk profile and portfolio
        """
        advice = []
        
        if risk_category == 'Conservative':
            advice.extend([
                "Your portfolio seems suitable for conservative investing",
                "Consider increasing allocation to dividend-paying stocks",
                "Look for companies with consistent earnings growth",
                "Avoid highly volatile small-cap stocks"
            ])
        
        elif risk_category == 'Moderate':
            advice.extend([
                "Your portfolio allows for balanced growth and stability",
                "Consider a mix of large-cap and selected mid-cap stocks",
                "Regular portfolio rebalancing is recommended",
                "Monitor sector concentration to avoid overexposure"
            ])
        
        else:  # Aggressive
            advice.extend([
                "Your risk tolerance allows for growth-oriented investments",
                "Consider adding small-cap and emerging sector stocks",
                "You can handle higher portfolio volatility",
                "Focus on companies with high growth potential"
            ])
        
        return advice
