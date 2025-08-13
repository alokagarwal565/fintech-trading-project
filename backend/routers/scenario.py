from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.models.models import User, ScenarioAnalysisRequest, Scenario
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.scenario_service import ScenarioService
import json

router = APIRouter(prefix="/api/v1", tags=["scenario"])

@router.post("/analyze-scenario")
async def analyze_scenario(
    request: ScenarioAnalysisRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Analyze market scenario impact on user's portfolio
    """
    try:
        service = ScenarioService()
        result = service.analyze_scenario(
            request.scenario_text, 
            current_user, 
            session, 
            request.portfolio_id
        )
        
        # Save to database
        scenario = Scenario(
            user_id=current_user.id,
            scenario_text=request.scenario_text,
            analysis_narrative=result['narrative'],
            insights=json.dumps(result['insights']),
            recommendations=json.dumps(result['recommendations']),
            risk_assessment=result['risk_assessment']
        )
        
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
        
        return {
            "scenario_id": scenario.id,
            "narrative": result['narrative'],
            "insights": result['insights'],
            "recommendations": result['recommendations'],
            "risk_assessment": result['risk_assessment']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing scenario: {str(e)}")