from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.models.models import User, PortfolioAnalysisRequest
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/v1", tags=["portfolio"])

@router.post("/analyze-portfolio")
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Analyze user's portfolio from natural language input
    """
    try:
        service = PortfolioService()
        result = service.analyze_portfolio(request.portfolio_input, current_user, session)
        
        return {
            "portfolio_id": result['portfolio_id'],
            "total_value": result['total_value'],
            "valid_holdings": result['valid_holdings'],
            "invalid_holdings": result['invalid_holdings'],
            "holdings_count": len(result['valid_holdings'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")