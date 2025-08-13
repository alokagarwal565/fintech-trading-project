from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
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
            recommendations=json.dumps(result['recommendations'])
        )
        
        session.add(risk_assessment)
        session.commit()
        session.refresh(risk_assessment)
        
        return {
            "assessment_id": risk_assessment.id,
            "score": result['score'],
            "category": result['category'],
            "description": result['description'],
            "recommendations": result['recommendations']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing risk profile: {str(e)}")