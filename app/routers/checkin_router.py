from fastapi import APIRouter, HTTPException
from app.models.user import CheckinRequest
from app.services.logic import process_user_checkin

router = APIRouter(prefix="/checkin", tags=["Check-in"])

@router.post("/", status_code=201)
async def create_checkin(request: CheckinRequest):
    try:
        result = await process_user_checkin(request.username)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
