from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session
from backend.models.models import User, ExportRequest
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.export_service import ExportService
from datetime import datetime

router = APIRouter(prefix="/api/v1/export", tags=["export"])

@router.post("/text")
async def export_text(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Export user's analysis results as text
    """
    try:
        service = ExportService()
        text_content = service.export_to_text(
            current_user, 
            session,
            request.include_risk_profile,
            request.include_portfolio,
            request.include_scenarios
        )
        
        filename = f"investment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        return Response(
            content=text_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text export: {str(e)}")

@router.post("/pdf")
async def export_pdf(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Export user's analysis results as PDF
    """
    try:
        service = ExportService()
        pdf_content = service.export_to_pdf(
            current_user,
            session,
            request.include_risk_profile,
            request.include_portfolio,
            request.include_scenarios
        )
        
        filename = f"investment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF export: {str(e)}")