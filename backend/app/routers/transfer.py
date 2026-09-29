from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Literal

from app.database import get_db
from app.models.user import User
from app.routers.finance import get_current_user
from app.transfer.import_handler.json import JsonImporter
from app.transfer.export_handler.json import JsonExporter

router = APIRouter(prefix="/api/v1/transfer", tags=["Transfer & Backup"])

@router.post("/import")
async def import_data(
    source_type: Literal["json"],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    content = await file.read()
    
    if source_type == "json":
        try:
            importer = JsonImporter()
            parsed_data = importer.parse(content)
            importer.save_to_db(db, user, parsed_data)
            return {"status": "success", "message": "JSON backup successfully imported."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")
            
    raise HTTPException(status_code=400, detail="Unsupported source type")

@router.get("/export")
def export_data(
    export_format: Literal["json"] = "json",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if export_format == "json":
        exporter = JsonExporter()
        data = exporter.export(db, user)
        return JSONResponse(content=data)
        
    raise HTTPException(status_code=400, detail="Unsupported export format") 