#!/usr/bin/env python3
"""Script to seed sample data for development and testing."""

import hashlib
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import MeteringEvent, MeteringQuota, MeteringAPIKey
from app.core.redis import get_redis
from app.config import settings
from app.services.cache_service import CacheService

def seed_data():
    """Seed sample data into database and Redis."""
    # Connect to database
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🌱 Seeding sample data...")
    
    # 1. Create API Key
    api_key = "dev_key_12345"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    existing_key = session.query(MeteringAPIKey).filter(
        MeteringAPIKey.key_hash == key_hash
    ).first()
    
    if not existing_key:
        api_key_obj = MeteringAPIKey(
            key_hash=key_hash,
            name="Development Key",
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(api_key_obj)
        session.commit()
        print(f"✅ Created API key: {api_key}")
    else:
        print(f"✅ API key already exists: {api_key}")
    
    # 2. Create Quotas
    tenants = ["org_001", "org_002", "org_003"]
    resources = ["billing", "analytics", "storage"]
    features = ["invoice_generate", "pdf_export", "data_export", "api_call"]
    
    for tenant_id in tenants:
        for resource in resources:
            for feature in features:
                existing_quota = session.query(MeteringQuota).filter(
                    MeteringQuota.tenant_id == tenant_id,
                    MeteringQuota.resource == resource,
                    MeteringQuota.feature == feature
                ).first()
                
                if not existing_quota:
                    quota = MeteringQuota(
                        tenant_id=tenant_id,
                        resource=resource,
                        feature=feature,
                        limit_value=1000,
                        period="monthly",
                        alert_threshold=80,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    session.add(quota)
    
    session.commit()
    print(f"✅ Created quotas for {len(tenants)} tenants")
    
    # 3. Create Sample Events (last 30 days)
    print("📊 Creating sample events...")
    cache_service = CacheService()
    redis = get_redis()
    
    base_time = datetime.utcnow()
    events_created = 0
    
    for day_offset in range(30):
        event_date = base_time - timedelta(days=day_offset)
        
        # Create events for each tenant/resource/feature combination
        for tenant_id in tenants:
            for resource in resources:
                for feature in features:
                    # Random number of events per day (1-50)
                    import random
                    num_events = random.randint(1, 50)
                    
                    for i in range(num_events):
                        # Random time during the day
                        hour = random.randint(0, 23)
                        minute = random.randint(0, 59)
                        event_timestamp = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        quantity = random.randint(1, 5)
                        
                        event = MeteringEvent(
                            tenant_id=tenant_id,
                            resource=resource,
                            feature=feature,
                            quantity=quantity,
                            timestamp=event_timestamp,
                            event_metadata={
                                "user": f"user_{random.randint(1, 100)}",
                                "session_id": f"session_{random.randint(1000, 9999)}",
                                "ip_address": f"192.168.1.{random.randint(1, 255)}"
                            }
                        )
                        session.add(event)
                        events_created += 1
                        
                        # Update Redis counters
                        for period in ["hourly", "daily", "monthly"]:
                            cache_service.increment_counter(
                                tenant_id,
                                resource,
                                feature,
                                period,
                                event_timestamp,
                                quantity
                            )
    
    session.commit()
    print(f"✅ Created {events_created} sample events")
    
    # 4. Create some recent events (last hour) for real-time feel
    print("⚡ Creating recent events...")
    recent_events = 0
    for i in range(20):
        tenant_id = random.choice(tenants)
        resource = random.choice(resources)
        feature = random.choice(features)
        
        event = MeteringEvent(
            tenant_id=tenant_id,
            resource=resource,
            feature=feature,
            quantity=1,
            timestamp=base_time - timedelta(minutes=random.randint(0, 60)),
            event_metadata={
                "user": f"user_{random.randint(1, 100)}",
                "session_id": f"session_{random.randint(1000, 9999)}"
            }
        )
        session.add(event)
        recent_events += 1
        
        # Update Redis counters
        for period in ["hourly", "daily", "monthly"]:
            cache_service.increment_counter(
                tenant_id,
                resource,
                feature,
                period,
                event.timestamp,
                1
            )
    
    session.commit()
    print(f"✅ Created {recent_events} recent events")
    
    session.close()
    
    print("\n" + "="*60)
    print("✅ Sample data seeding completed!")
    print("="*60)
    print(f"📊 Total events created: {events_created + recent_events}")
    print(f"🏢 Tenants: {', '.join(tenants)}")
    print(f"📦 Resources: {', '.join(resources)}")
    print(f"⚙️  Features: {', '.join(features)}")
    print(f"🔑 API Key: {api_key}")
    print("\n💡 Use this API key in your UI .env.local file:")
    print(f"   VITE_API_KEY={api_key}")
    print("="*60)

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

