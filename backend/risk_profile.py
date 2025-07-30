import streamlit as st
from typing import Dict, Tuple

class RiskProfiler:
    def __init__(self):
        self.questions = [
            {
                "id": "age",
                "question": "What is your age range?",
                "options": ["18-25", "26-35", "36-45", "46-55", "55+"],
                "weights": [5, 4, 3, 2, 1]
            },
            {
                "id": "income",
                "question": "What percentage of your income do you invest?",
                "options": ["Less than 10%", "10-20%", "20-30%", "30-50%", "More than 50%"],
                "weights": [1, 2, 3, 4, 5]
            },
            {
                "id": "horizon",
                "question": "What is your investment time horizon?",
                "options": ["Less than 1 year", "1-3 years", "3-5 years", "5-10 years", "More than 10 years"],
                "weights": [1, 2, 3, 4, 5]
            },
            {
                "id": "volatility",
                "question": "How comfortable are you with portfolio volatility?",
                "options": ["Very uncomfortable", "Somewhat uncomfortable", "Neutral", "Somewhat comfortable", "Very comfortable"],
                "weights": [1, 2, 3, 4, 5]
            },
            {
                "id": "loss_reaction",
                "question": "If your portfolio dropped 20% in a month, what would you do?",
                "options": ["Sell everything immediately", "Sell some holdings", "Hold and wait", "Buy more at lower prices", "Significantly increase investment"],
                "weights": [1, 2, 3, 4, 5]
            },
            {
                "id": "experience",
                "question": "How would you describe your investment experience?",
                "options": ["Complete beginner", "Some experience", "Moderate experience", "Experienced", "Very experienced"],
                "weights": [1, 2, 3, 4, 5]
            }
        ]
    
    def calculate_risk_score(self, answers: Dict[str, str]) -> Tuple[int, str]:
        """Calculate risk score based on answers"""
        total_score = 0
        max_score = len(self.questions) * 5
        
        for question in self.questions:
            answer = answers.get(question["id"])
            if answer:
                option_index = question["options"].index(answer)
                total_score += question["weights"][option_index]
        
        # Normalize to percentage
        risk_percentage = (total_score / max_score) * 100
        
        # Classify risk profile
        if risk_percentage <= 40:
            risk_profile = "Conservative"
        elif risk_percentage <= 70:
            risk_profile = "Balanced"
        else:
            risk_profile = "Aggressive"
        
        return risk_percentage, risk_profile
    
    def get_risk_description(self, risk_profile: str) -> str:
        """Get description of risk profile"""
        descriptions = {
            "Conservative": "You prefer stable, low-risk investments with predictable returns. Capital preservation is your priority.",
            "Balanced": "You're comfortable with moderate risk for potentially higher returns. You seek a balance between growth and stability.",
            "Aggressive": "You're willing to take high risks for potentially high returns. You have a long investment horizon and can tolerate volatility."
        }
        return descriptions.get(risk_profile, "Unknown risk profile")
