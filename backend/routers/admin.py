from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from collections import Counter

from backend.models.database import get_session
from backend.models.models import (
    User, Portfolio, Holding, RiskAssessment, Scenario, Export, 
    UserRole, AdminUserSummary, AdminPortfolioSummary, AdminRiskAssessmentSummary,
    AdminScenarioSummary, AdminExportSummary, AdminDashboardStats, AdminSystemLog
)
from backend.auth.auth import get_current_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Get comprehensive dashboard statistics"""
    
    # User statistics
    total_users = session.exec(select(func.count(User.id))).first()
    active_users = session.exec(select(func.count(User.id)).where(User.is_active == True)).first()
    
    # Time-based user statistics
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    new_users_this_week = session.exec(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    ).first()
    
    new_users_this_month = session.exec(
        select(func.count(User.id)).where(User.created_at >= month_ago)
    ).first()
    
    # Portfolio statistics
    total_portfolios = session.exec(select(func.count(Portfolio.id))).first()
    total_holdings = session.exec(select(func.count(Holding.id))).first()
    
    # Calculate average holdings per portfolio
    portfolio_counts = session.exec(
        select(Portfolio.id, func.count(Holding.id).label('holdings_count'))
        .outerjoin(Holding)
        .group_by(Portfolio.id)
    ).all()
    
    if portfolio_counts:
        total_holdings_for_avg = sum(count.holdings_count for count in portfolio_counts)
        average_holdings_per_portfolio = total_holdings_for_avg / len(portfolio_counts)
    else:
        average_holdings_per_portfolio = 0.0
    
    # Risk assessment statistics
    total_risk_assessments = session.exec(select(func.count(RiskAssessment.id))).first()
    
    # Risk score distribution
    risk_scores = session.exec(select(RiskAssessment.score)).all()
    risk_score_distribution = {}
    for score_tuple in risk_scores:
        score_val = score_tuple[0] if isinstance(score_tuple, tuple) else score_tuple
        if score_val in risk_score_distribution:
            risk_score_distribution[score_val] += 1
        else:
            risk_score_distribution[score_val] = 1
    
    # Scenario and export statistics
    total_scenarios = session.exec(select(func.count(Scenario.id))).first()
    total_exports = session.exec(select(func.count(Export.id))).first()
    
    # Most common stocks and sectors
    holdings = session.exec(select(Holding.symbol, Holding.sector)).all()
    
    stock_counter = Counter(holding.symbol for holding in holdings)
    sector_counter = Counter(holding.sector for holding in holdings if holding.sector)
    
    most_common_stocks = [{"symbol": symbol, "count": count} for symbol, count in stock_counter.most_common(10)]
    most_common_sectors = [{"sector": sector, "count": count} for sector, count in sector_counter.most_common(10)]
    
    return AdminDashboardStats(
        total_users=total_users or 0,
        active_users=active_users or 0,
        new_users_this_week=new_users_this_week or 0,
        new_users_this_month=new_users_this_month or 0,
        total_portfolios=total_portfolios or 0,
        total_holdings=total_holdings or 0,
        average_holdings_per_portfolio=average_holdings_per_portfolio,
        total_risk_assessments=total_risk_assessments or 0,
        risk_score_distribution=risk_score_distribution,
        total_scenarios=total_scenarios or 0,
        total_exports=total_exports or 0,
        most_common_stocks=most_common_stocks,
        most_common_sectors=most_common_sectors
    )

@router.get("/users", response_model=List[AdminUserSummary])
async def get_all_users(
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
):
    """Get all users with their activity counts"""
    
    query = select(User)
    if active_only:
        query = query.where(User.is_active == True)
    
    users = session.exec(query.offset(skip).limit(limit)).all()
    
    user_summaries = []
    for user in users:
        # Count related records
        risk_assessments_count = session.exec(
            select(func.count(RiskAssessment.id)).where(RiskAssessment.user_id == user.id)
        ).first() or 0
        
        portfolios_count = session.exec(
            select(func.count(Portfolio.id)).where(Portfolio.user_id == user.id)
        ).first() or 0
        
        scenarios_count = session.exec(
            select(func.count(Scenario.id)).where(Scenario.user_id == user.id)
        ).first() or 0
        
        exports_count = session.exec(
            select(func.count(Export.id)).where(Export.user_id == user.id)
        ).first() or 0
        
        user_summaries.append(AdminUserSummary(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            risk_assessments_count=risk_assessments_count,
            portfolios_count=portfolios_count,
            scenarios_count=scenarios_count,
            exports_count=exports_count
        ))
    
    return user_summaries

@router.get("/portfolios", response_model=List[AdminPortfolioSummary])
async def get_all_portfolios(
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """Get all portfolios with user information"""
    
    portfolios = session.exec(
        select(Portfolio)
        .join(User)
        .offset(skip)
        .limit(limit)
    ).all()
    
    portfolio_summaries = []
    for portfolio in portfolios:
        # Get user info
        user = session.exec(select(User).where(User.id == portfolio.user_id)).first()
        
        # Count holdings
        holdings_count = session.exec(
            select(func.count(Holding.id)).where(Holding.portfolio_id == portfolio.id)
        ).first() or 0
        
        portfolio_summaries.append(AdminPortfolioSummary(
            id=portfolio.id,
            user_email=user.email if user else "Unknown",
            user_full_name=user.full_name if user else None,
            name=portfolio.name,
            total_value=portfolio.total_value,
            holdings_count=holdings_count,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at
        ))
    
    return portfolio_summaries

@router.get("/risk-assessments", response_model=List[AdminRiskAssessmentSummary])
async def get_all_risk_assessments(
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """Get all risk assessments with user information"""
    
    risk_assessments = session.exec(
        select(RiskAssessment)
        .join(User)
        .offset(skip)
        .limit(limit)
    ).all()
    
    risk_summaries = []
    for assessment in risk_assessments:
        user = session.exec(select(User).where(User.id == assessment.user_id)).first()
        
        risk_summaries.append(AdminRiskAssessmentSummary(
            id=assessment.id,
            user_email=user.email if user else "Unknown",
            user_full_name=user.full_name if user else None,
            score=assessment.score,
            category=assessment.category,
            created_at=assessment.created_at
        ))
    
    return risk_summaries

@router.get("/scenarios", response_model=List[AdminScenarioSummary])
async def get_all_scenarios(
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """Get all scenarios with user information"""
    
    scenarios = session.exec(
        select(Scenario)
        .join(User)
        .offset(skip)
        .limit(limit)
    ).all()
    
    scenario_summaries = []
    for scenario in scenarios:
        user = session.exec(select(User).where(User.id == scenario.user_id)).first()
        
        scenario_summaries.append(AdminScenarioSummary(
            id=scenario.id,
            user_email=user.email if user else "Unknown",
            user_full_name=user.full_name if user else None,
            scenario_text=scenario.scenario_text,
            risk_assessment=scenario.risk_assessment,
            created_at=scenario.created_at
        ))
    
    return scenario_summaries

@router.get("/exports", response_model=List[AdminExportSummary])
async def get_all_exports(
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """Get all exports with user information"""
    
    exports = session.exec(
        select(Export)
        .join(User)
        .offset(skip)
        .limit(limit)
    ).all()
    
    export_summaries = []
    for export in exports:
        user = session.exec(select(User).where(User.id == export.user_id)).first()
        
        export_summaries.append(AdminExportSummary(
            id=export.id,
            user_email=user.email if user else "Unknown",
            user_full_name=user.full_name if user else None,
            export_type=export.export_type,
            filename=export.filename,
            include_risk_profile=export.include_risk_profile,
            include_portfolio=export.include_portfolio,
            include_scenarios=export.include_scenarios,
            created_at=export.created_at
        ))
    
    return export_summaries

@router.get("/system-logs", response_model=List[AdminSystemLog])
async def get_system_logs(
    current_admin: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    search: Optional[str] = None
):
    """Get system logs from app.log file"""
    
    log_file = os.getenv("LOG_FILE", "app.log")
    logs = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
        
        # Parse log lines and filter
        for line in log_lines:
            try:
                # Parse log line format: timestamp - module - level - function:line - message
                parts = line.strip().split(' - ')
                if len(parts) >= 4:
                    timestamp = parts[0]
                    module = parts[1]
                    level_info = parts[2]
                    message = ' - '.join(parts[3:])
                    
                    # Extract level and function:line
                    level_parts = level_info.split(' ')
                    log_level = level_parts[0]
                    function_line = level_parts[1] if len(level_parts) > 1 else ""
                    
                    # Parse function:line
                    if ':' in function_line:
                        function, line_str = function_line.rsplit(':', 1)
                        line_num = int(line_str) if line_str.isdigit() else 0
                    else:
                        function = function_line
                        line_num = 0
                    
                    # Apply filters
                    if level and log_level.lower() != level.lower():
                        continue
                    
                    if search and search.lower() not in message.lower():
                        continue
                    
                    logs.append(AdminSystemLog(
                        timestamp=timestamp,
                        level=log_level,
                        message=message,
                        module=module,
                        function=function,
                        line=line_num
                    ))
            except Exception:
                # Skip malformed log lines
                continue
        
        # Sort by timestamp (newest first) and apply pagination
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[skip:skip + limit]
        
    except FileNotFoundError:
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading log file: {str(e)}"
        )

@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Toggle user active/inactive status"""
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify admin user status"
        )
    
    user.is_active = not user.is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": f"User {user.email} status changed to {'active' if user.is_active else 'inactive'}"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Delete a user and all associated data"""
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    
    # Delete associated data (cascade delete should handle this)
    session.delete(user)
    session.commit()
    
    return {"message": f"User {user.email} and all associated data deleted successfully"}
