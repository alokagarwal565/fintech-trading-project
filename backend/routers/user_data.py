from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.models.models import User, RiskAssessment, Portfolio, Holding, Scenario, Export
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.portfolio_service import PortfolioService
import json

router = APIRouter(prefix="/api/v1/user", tags=["user-data"])
portfolio_service = PortfolioService()

@router.get("/data")
async def get_user_data(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all user data including risk profile, portfolio, scenarios, and exports
    """
    try:
        user_data = {
            "risk_profile": None,
            "portfolio": None,
            "scenarios": [],
            "exports": []
        }
        
        # Get latest risk assessment
        try:
            risk_statement = select(RiskAssessment).where(
                RiskAssessment.user_id == current_user.id
            ).order_by(RiskAssessment.created_at.desc()).limit(1)
            
            risk_assessment = session.exec(risk_statement).first()
            if risk_assessment:
                # Handle missing answers column gracefully
                try:
                    answers = json.loads(risk_assessment.answers) if hasattr(risk_assessment, 'answers') else []
                except (AttributeError, json.JSONDecodeError):
                    answers = []
                
                user_data["risk_profile"] = {
                    "assessment_id": risk_assessment.id,
                    "score": risk_assessment.score,
                    "category": risk_assessment.category,
                    "description": risk_assessment.description,
                    "recommendations": json.loads(risk_assessment.recommendations),
                    "answers": answers,
                    "created_at": risk_assessment.created_at.isoformat()
                }
        except Exception as e:
            print(f"Warning: Could not fetch risk assessment: {e}")
        
        # Get latest portfolio
        try:
            portfolio_statement = select(Portfolio).where(
                Portfolio.user_id == current_user.id
            ).order_by(Portfolio.updated_at.desc()).limit(1)
            
            portfolio = session.exec(portfolio_statement).first()
            if portfolio:
                # Get holdings for this portfolio
                holdings_statement = select(Holding).where(Holding.portfolio_id == portfolio.id)
                holdings = session.exec(holdings_statement).all()
                
                holdings_data = []
                for holding in holdings:
                    holdings_data.append({
                        "id": holding.id,
                        "company_name": holding.company_name,
                        "symbol": holding.symbol,
                        "quantity": holding.quantity,
                        "current_price": holding.current_price,
                        "total_value": holding.total_value,
                        "sector": holding.sector,
                        "pe_ratio": holding.pe_ratio,
                        "dividend_yield": holding.dividend_yield
                    })
                
                user_data["portfolio"] = {
                    "portfolio_id": portfolio.id,
                    "total_value": portfolio.total_value,
                    "holdings": holdings_data,
                    "holdings_count": len(holdings_data),
                    "visualizations": portfolio_service.visualize_portfolio(holdings_data),
                    "created_at": portfolio.created_at.isoformat(),
                    "updated_at": portfolio.updated_at.isoformat()
                }
        except Exception as e:
            print(f"Warning: Could not fetch portfolio: {e}")
        
        # Get all scenarios
        try:
            scenarios_statement = select(Scenario).where(
                Scenario.user_id == current_user.id
            ).order_by(Scenario.created_at.desc())
            
            scenarios = session.exec(scenarios_statement).all()
            for scenario in scenarios:
                user_data["scenarios"].append({
                    "scenario_id": scenario.id,
                    "scenario_text": scenario.scenario_text,
                    "narrative": scenario.analysis_narrative,
                    "insights": json.loads(scenario.insights),
                    "recommendations": json.loads(scenario.recommendations),
                    "risk_assessment": scenario.risk_assessment,
                    "created_at": scenario.created_at.isoformat()
                })
        except Exception as e:
            print(f"Warning: Could not fetch scenarios: {e}")
        
        # Get all exports
        try:
            exports_statement = select(Export).where(
                Export.user_id == current_user.id
            ).order_by(Export.created_at.desc())
            
            exports = session.exec(exports_statement).all()
            for export in exports:
                user_data["exports"].append({
                    "export_id": export.id,
                    "export_type": export.export_type,
                    "filename": export.filename,
                    "include_risk_profile": export.include_risk_profile,
                    "include_portfolio": export.include_portfolio,
                    "include_scenarios": export.include_scenarios,
                    "created_at": export.created_at.isoformat()
                })
        except Exception as e:
            print(f"Warning: Could not fetch exports: {e}")
        
        return user_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user data: {str(e)}")
