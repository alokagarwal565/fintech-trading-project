from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.models.models import User, RiskProfileRequest, RiskAssessment
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.risk_profile_service import RiskProfileService
import json

router = APIRouter(prefix="/api/v1", tags=["risk-profile"])

@router.post("/risk-profile")
async def assess_risk_profile(
    request: RiskProfileRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Assess user's risk tolerance based on questionnaire answers
    """
    try:
        service = RiskProfileService()
        result = service.assess_risk_tolerance(request.answers)
        
        # Save to database
        risk_assessment = RiskAssessment(
            user_id=current_user.id,
            score=result['score'],
            category=result['category'],
            description=result['description'],
            recommendations=json.dumps(result['recommendations']),
            answers=json.dumps(request.answers)
        )
        
        session.add(risk_assessment)
        session.commit()
        session.refresh(risk_assessment)
        
        return {
            "assessment_id": risk_assessment.id,
            "score": result['score'],
            "category": result['category'],
            "description": result['description'],
            "recommendations": result['recommendations'],
            "answers": request.answers,
            "created_at": risk_assessment.created_at.isoformat()
        }
        
    except Exception as e:
        # Check if it's a database schema error
        if "no such column" in str(e).lower() or "answers" in str(e).lower():
            raise HTTPException(
                status_code=500, 
                detail="Database schema needs to be updated. Please run 'python reset_database.py' and restart the server."
            )
        raise HTTPException(status_code=500, detail=f"Error assessing risk profile: {str(e)}")

@router.get("/risk-profile/latest")
async def get_latest_risk_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the latest risk assessment for the current user
    """
    try:
        # Get the most recent risk assessment for the user
        statement = select(RiskAssessment).where(
            RiskAssessment.user_id == current_user.id
        ).order_by(RiskAssessment.created_at.desc()).limit(1)
        
        result = session.exec(statement).first()
        
        if not result:
            return {"message": "No risk assessment found"}
        
        return {
            "assessment_id": result.id,
            "score": result.score,
            "category": result.category,
            "description": result.description,
            "recommendations": json.loads(result.recommendations),
            "answers": json.loads(result.answers),
            "created_at": result.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching risk profile: {str(e)}")

@router.delete("/risk-profile/latest")
async def delete_latest_risk_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete the latest risk assessment for the current user
    """
    try:
        # Get the most recent risk assessment for the user
        statement = select(RiskAssessment).where(
            RiskAssessment.user_id == current_user.id
        ).order_by(RiskAssessment.created_at.desc()).limit(1)
        
        result = session.exec(statement).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="No risk assessment found")
        
        session.delete(result)
        session.commit()
        
        return {"message": "Risk assessment deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting risk profile: {str(e)}")