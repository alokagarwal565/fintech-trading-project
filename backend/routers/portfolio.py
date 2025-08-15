from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.models.models import User, Portfolio, Holding, PortfolioAnalysisRequest
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.portfolio_service import PortfolioService
from pydantic import BaseModel
from typing import List, Dict, Any
import json

router = APIRouter(prefix="/api/v1", tags=["portfolio"])
portfolio_service = PortfolioService()

@router.post("/analyze-portfolio", response_model=Dict[str, Any])
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Analyze user's portfolio from natural language input
    """
    try:
        service = PortfolioService()
        result = service.analyze_portfolio(request.portfolio_input, current_user, session)
        
        return {
            "portfolio_id": result['portfolio_id'],
            "portfolio_input": request.portfolio_input,
            "total_value": result['total_value'],
            "holdings": result['valid_holdings'],  # Use 'holdings' for consistency
            "invalid_holdings": result['invalid_holdings'],
            "holdings_count": len(result['valid_holdings']),
            "metrics": result['metrics'],
            "visualizations": result['visualizations'],
            "created_at": result.get('created_at', '')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")

@router.get("/portfolio/latest")
async def get_latest_portfolio(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the latest portfolio analysis for the current user
    """
    try:
        # Get the most recent portfolio for the user
        statement = select(Portfolio).where(
            Portfolio.user_id == current_user.id
        ).order_by(Portfolio.updated_at.desc()).limit(1)
        
        portfolio = session.exec(statement).first()
        
        if not portfolio:
            return {"message": "No portfolio found"}
        
        # Get holdings for this portfolio
        holdings_statement = select(Holding).where(Holding.portfolio_id == portfolio.id)
        holdings = session.exec(holdings_statement).all()
        
        # Convert holdings to list of dicts
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
        
        # Regenerate visualizations from saved holdings data
        visualizations = portfolio_service.visualize_portfolio(holdings_data)
        
        return {
            "portfolio_id": portfolio.id,
            "total_value": portfolio.total_value,
            "holdings": holdings_data,
            "holdings_count": len(holdings_data),
            "visualizations": visualizations,
            "created_at": portfolio.created_at.isoformat(),
            "updated_at": portfolio.updated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio: {str(e)}")

@router.delete("/portfolio/latest")
async def delete_latest_portfolio(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete the latest portfolio and its holdings for the current user
    """
    try:
        # Get the most recent portfolio for the user
        statement = select(Portfolio).where(
            Portfolio.user_id == current_user.id
        ).order_by(Portfolio.updated_at.desc()).limit(1)
        
        portfolio = session.exec(statement).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="No portfolio found")
        
        # Delete holdings first (due to foreign key constraint)
        holdings_statement = select(Holding).where(Holding.portfolio_id == portfolio.id)
        holdings = session.exec(holdings_statement).all()
        for holding in holdings:
            session.delete(holding)
        
        # Delete portfolio
        session.delete(portfolio)
        session.commit()
        
        return {"message": "Portfolio deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting portfolio: {str(e)}")
