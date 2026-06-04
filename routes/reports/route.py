from fastapi import APIRouter, Depends, HTTPException
from core.response import APIResponse, success_response
from core.security import get_current_user_id
from database import get_db_connection
from .service import ReportsService

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/daily", response_model=APIResponse)
def get_daily_report(
    date: str,
    current_user_id: int = Depends(get_current_user_id)
):
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = ReportsService.get_daily_report(date)
    return success_response(result, "Daily report fetched successfully")

@router.get("/monthly", response_model=APIResponse)
def get_monthly_report(
    start_date: str,
    end_date: str,
    current_user_id: int = Depends(get_current_user_id)
):
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")     

    result = ReportsService.get_monthly_report(start_date, end_date)
    return success_response(result, "Monthly report fetched successfully")
