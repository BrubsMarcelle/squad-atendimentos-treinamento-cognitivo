from fastapi import APIRouter, HTTPException, Depends, status
from app.services.logic import process_user_checkin
from app.auth import get_current_user

router = APIRouter(prefix="/checkin", tags=["Check-in"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_checkin(current_user: dict = Depends(get_current_user)):
    """
    Registra o check-in do usuário autenticado.
    O usuário é identificado pelo token JWT, não por um payload.
    """
    try:
        # A função de lógica agora recebe o objeto do usuário do token
        result = await process_user_checkin(current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))