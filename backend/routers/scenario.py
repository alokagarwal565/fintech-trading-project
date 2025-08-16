from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
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
    Analyze market scenario impact on user's portfolio with dynamic portfolio-aware analysis
    """
    try:
        service = ScenarioService()
        result = service.analyze_scenario(
            request.scenario_text, 
            current_user, 
            session, 
            request.portfolio_id
        )
        
        # Save to database with enhanced data
        scenario = Scenario(
            user_id=current_user.id,
            scenario_text=request.scenario_text,
            analysis_narrative=result['narrative'],
            insights=json.dumps(result['insights']),
            recommendations=json.dumps(result['recommendations']),
            risk_assessment=result['risk_assessment'],
            risk_details=json.dumps(result.get('risk_details', {})),
            portfolio_impact=json.dumps(result.get('portfolio_impact', {})),
            portfolio_composition=json.dumps(result.get('portfolio_composition', {}))
        )
        
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
        
        # Return enhanced response with portfolio analysis data
        return {
            "scenario_id": scenario.id,
            "scenario_text": request.scenario_text,
            "narrative": result['narrative'],
            "insights": result['insights'],
            "recommendations": result['recommendations'],
            "risk_assessment": result['risk_assessment'],
            "risk_details": result.get('risk_details', {}),
            "portfolio_impact": result.get('portfolio_impact', {}),
            "portfolio_composition": result.get('portfolio_composition', {}),
            "created_at": scenario.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing scenario: {str(e)}")

@router.get("/scenarios")
async def get_user_scenarios(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all scenarios for the current user
    """
    try:
        statement = select(Scenario).where(
            Scenario.user_id == current_user.id
        ).order_by(Scenario.created_at.desc())
        
        scenarios = session.exec(statement).all()
        
        scenarios_data = []
        for scenario in scenarios:
            scenario_data = {
                "scenario_id": scenario.id,
                "scenario_text": scenario.scenario_text,
                "narrative": scenario.analysis_narrative,
                "insights": json.loads(scenario.insights),
                "recommendations": json.loads(scenario.recommendations),
                "risk_assessment": scenario.risk_assessment,
                "created_at": scenario.created_at.isoformat()
            }
            
            # Add new fields if they exist
            if scenario.risk_details:
                scenario_data["risk_details"] = json.loads(scenario.risk_details)
            if scenario.portfolio_impact:
                scenario_data["portfolio_impact"] = json.loads(scenario.portfolio_impact)
            if scenario.portfolio_composition:
                scenario_data["portfolio_composition"] = json.loads(scenario.portfolio_composition)
            
            scenarios_data.append(scenario_data)
        
        return {
            "scenarios": scenarios_data,
            "count": len(scenarios_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scenarios: {str(e)}")

@router.get("/scenarios/{scenario_id}")
async def get_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific scenario by ID
    """
    try:
        statement = select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.user_id == current_user.id
        )
        
        scenario = session.exec(statement).first()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        scenario_data = {
            "scenario_id": scenario.id,
            "scenario_text": scenario.scenario_text,
            "narrative": scenario.analysis_narrative,
            "insights": json.loads(scenario.insights),
            "recommendations": json.loads(scenario.recommendations),
            "risk_assessment": scenario.risk_assessment,
            "created_at": scenario.created_at.isoformat()
        }
        
        # Add new fields if they exist
        if scenario.risk_details:
            scenario_data["risk_details"] = json.loads(scenario.risk_details)
        if scenario.portfolio_impact:
            scenario_data["portfolio_impact"] = json.loads(scenario.portfolio_impact)
        if scenario.portfolio_composition:
            scenario_data["portfolio_composition"] = json.loads(scenario.portfolio_composition)
        
        return scenario_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scenario: {str(e)}")

@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific scenario by ID
    """
    try:
        statement = select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.user_id == current_user.id
        )
        
        scenario = session.exec(statement).first()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        session.delete(scenario)
        session.commit()
        
        return {"message": "Scenario deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting scenario: {str(e)}")