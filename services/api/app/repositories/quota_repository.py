"""Repository for quota database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.database import MeteringQuota


class QuotaRepository:
    """Repository for quota operations."""
    
    @staticmethod
    def get_by_tenant_feature(
        db: Session,
        tenant_id: str,
        feature: str,
        resource: Optional[str] = None
    ) -> Optional[MeteringQuota]:
        """Get quota for a tenant and feature."""
        query = db.query(MeteringQuota).filter(
            MeteringQuota.tenant_id == tenant_id,
            MeteringQuota.feature == feature,
            MeteringQuota.is_active == True
        )
        
        if resource:
            query = query.filter(MeteringQuota.resource == resource)
        
        return query.first()
    
    @staticmethod
    def create(db: Session, quota_data: dict) -> MeteringQuota:
        """Create a new quota."""
        quota = MeteringQuota(**quota_data)
        db.add(quota)
        db.commit()
        db.refresh(quota)
        return quota
    
    @staticmethod
    def get_all_by_tenant(db: Session, tenant_id: str) -> List[MeteringQuota]:
        """Get all quotas for a tenant."""
        return db.query(MeteringQuota).filter(
            MeteringQuota.tenant_id == tenant_id,
            MeteringQuota.is_active == True
        ).all()

