from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, FileResponse
from sqlmodel import Session, select
from backend.models.models import User, ExportRequest, Export, ExportType
from backend.models.database import get_session
from backend.auth.auth import get_current_user
from backend.services.export_service import ExportService
from datetime import datetime
import os
import asyncio

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
        
        # Create exports directory if it doesn't exist
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        # Generate filename and save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"investment_analysis_{timestamp}.txt"
        file_path = os.path.join(exports_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Save export record to database
        export_record = Export(
            user_id=current_user.id,
            export_type=ExportType.TEXT,
            filename=filename,
            file_path=file_path,
            include_risk_profile=request.include_risk_profile,
            include_portfolio=request.include_portfolio,
            include_scenarios=request.include_scenarios
        )
        
        session.add(export_record)
        session.commit()
        session.refresh(export_record)
        
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
    Export user's analysis results as PDF with timeout protection
    """
    try:
        print(f"🚀 Starting PDF export for user {current_user.email}")
        
        # Create a task for PDF generation with timeout
        service = ExportService()
        
        # Run PDF generation with timeout protection
        try:
            # Use asyncio.wait_for to add timeout protection
            pdf_content = await asyncio.wait_for(
                asyncio.to_thread(
                    service.export_to_pdf,
                    current_user,
                    session,
                    request.include_risk_profile,
                    request.include_portfolio,
                    request.include_scenarios
                ),
                timeout=15.0  # 15 second timeout since charts are disabled (reduced from 25)
            )
            
            print(f"✅ PDF generation completed for user {current_user.email}")
            
        except asyncio.TimeoutError:
            print(f"⏰ PDF generation timeout for user {current_user.email}")
            raise HTTPException(
                status_code=408, 
                detail="PDF generation timed out. The export may be too complex. Please try again or contact support."
            )
        
        # Create exports directory if it doesn't exist
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        # Generate filename and save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"investment_analysis_{timestamp}.pdf"
        file_path = os.path.join(exports_dir, filename)
        
        # Save the PDF file
        with open(file_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"💾 PDF file saved: {file_path}")
        
        # Save export record to database
        export_record = Export(
            user_id=current_user.id,
            export_type=ExportType.PDF,
            filename=filename,
            file_path=file_path,
            include_risk_profile=request.include_risk_profile,
            include_portfolio=request.include_portfolio,
            include_scenarios=request.include_scenarios
        )
        
        session.add(export_record)
        session.commit()
        session.refresh(export_record)
        
        print(f"📊 Export record saved to database for user {current_user.email}")
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like timeout)
        raise
    except Exception as e:
        print(f"❌ PDF export error for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating PDF export: {str(e)}. Please try again or contact support."
        )

@router.get("/history")
async def get_export_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get export history for the current user
    """
    try:
        statement = select(Export).where(
            Export.user_id == current_user.id
        ).order_by(Export.created_at.desc())
        
        exports = session.exec(statement).all()
        
        exports_data = []
        for export in exports:
            exports_data.append({
                "export_id": export.id,
                "export_type": export.export_type,
                "filename": export.filename,
                "include_risk_profile": export.include_risk_profile,
                "include_portfolio": export.include_portfolio,
                "include_scenarios": export.include_scenarios,
                "created_at": export.created_at.isoformat()
            })
        
        return {
            "exports": exports_data,
            "count": len(exports_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching export history: {str(e)}")

@router.get("/download/{export_id}")
async def download_export(
    export_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Download a specific export file
    """
    try:
        statement = select(Export).where(
            Export.id == export_id,
            Export.user_id == current_user.id
        )
        
        export = session.exec(statement).first()
        
        if not export:
            raise HTTPException(status_code=404, detail="Export not found")
        
        if not os.path.exists(export.file_path):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        media_type = "text/plain" if export.export_type == ExportType.TEXT else "application/pdf"
        
        return FileResponse(
            path=export.file_path,
            filename=export.filename,
            media_type=media_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading export: {str(e)}")

@router.delete("/{export_id}")
async def delete_export(
    export_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific export record and file
    """
    try:
        statement = select(Export).where(
            Export.id == export_id,
            Export.user_id == current_user.id
        )
        
        export = session.exec(statement).first()
        
        if not export:
            raise HTTPException(status_code=404, detail="Export not found")
        
        # Delete file if it exists
        if os.path.exists(export.file_path):
            os.remove(export.file_path)
        
        # Delete database record
        session.delete(export)
        session.commit()
        
        return {"message": "Export deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting export: {str(e)}")