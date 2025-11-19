"""Quota validation endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import validate_api_key
from app.models.schemas import QuotaValidationRequest, QuotaValidationResult
from app.services.quota_service import QuotaService

router = APIRouter()


@router.post("/validate", response_model=QuotaValidationResult)
async def validate_quota(
    request: QuotaValidationRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """Validate if action is allowed within quota."""
    service = QuotaService(db)
    result = await service.validate_quota(request)
    return result

