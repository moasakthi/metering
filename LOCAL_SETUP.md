# Local Development Setup Guide

This guide will help you set up and run the Metering Framework locally without Docker.

## Prerequisites

1. **Python 3.11+** (or 3.9+ minimum)
2. **Node.js 18+** and npm
3. **PostgreSQL 14+**
4. **Redis 6+**

## Step 1: Install Prerequisites

### macOS (using Homebrew)

```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Install Redis
brew install redis
brew services start redis

# Verify installations
psql --version
redis-cli --version
```

### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql-14 postgresql-contrib

# Install Redis
sudo apt install redis-server

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl enable redis-server
```

### Windows

1. Download and install PostgreSQL from https://www.postgresql.org/download/windows/
2. Download and install Redis from https://github.com/microsoftarchive/redis/releases
3. Or use WSL2 with the Linux instructions above

## Step 2: Database Setup

### Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# In PostgreSQL shell, run:
CREATE DATABASE metering;
CREATE USER metering WITH PASSWORD 'metering';
GRANT ALL PRIVILEGES ON DATABASE metering TO metering;
\q
```

Or if using your existing PostgreSQL setup (based on your config):
```bash
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE metering;
\q
```

### Verify Redis

```bash
redis-cli ping
# Should return: PONG
```

## Step 3: API Service Setup

```bash
# Navigate to API directory
cd services/api

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file with your database credentials
# Update DATABASE_URL if needed:
# DATABASE_URL=postgresql://postgres:admin@localhost:5432/metering
```

### Update .env file

Edit `services/api/.env`:
```bash
DATABASE_URL=postgresql://postgres:admin@localhost:5432/metering
REDIS_URL=redis://localhost:6379/0
API_HOST=0.0.0.0
API_PORT=8000
```

### Run Database Migrations

```bash
# Make sure you're in services/api directory
# Make sure virtual environment is activated

# Initialize Alembic (if not already done)
python3 -m alembic init alembic

# Create initial migration
python3 -m alembic revision --autogenerate -m "Initial migration"

# Apply migrations
python3 -m alembic upgrade head
```

### Start API Service

```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 4: UI Service Setup

```bash
# Navigate to UI directory
cd services/ui

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local file
# VITE_API_URL=http://localhost:8000
# VITE_API_KEY=your_api_key_here
```

### Start UI Service

```bash
# Development server
npm run dev

# The UI will be available at http://localhost:3000
```

## Step 5: Metering Annotator Setup (Optional)

If you want to use the annotator library in your own projects:

```bash
# Navigate to annotator directory
cd metering-annotator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Step 6: Create Initial API Key

You'll need an API key to use the service. You can create one manually in the database:

```bash
# Connect to PostgreSQL
psql -U postgres -d metering

# Generate a hash for your API key (use Python)
python3 -c "import hashlib; print(hashlib.sha256(b'your_secret_key_here').hexdigest())"

# Insert API key (replace the hash and name)
INSERT INTO metering_api_keys (key_hash, name, is_active, created_at)
VALUES (
    'your_hashed_key_here',
    'Development Key',
    true,
    NOW()
);

# Note: Use 'your_secret_key_here' as your API key in requests
```

Or create a simple script to generate API keys:

```python
# create_api_key.py
import hashlib
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import MeteringAPIKey

# Your API key (keep this secret!)
API_KEY = "dev_key_12345"
KEY_NAME = "Development Key"

# Hash the key
key_hash = hashlib.sha256(API_KEY.encode()).hexdigest()

# Connect to database
engine = create_engine("postgresql://postgres:admin@localhost:5432/metering")
Session = sessionmaker(bind=engine)
session = Session()

# Create API key
api_key = MeteringAPIKey(
    key_hash=key_hash,
    name=KEY_NAME,
    is_active=True,
    created_at=datetime.utcnow()
)

session.add(api_key)
session.commit()
print(f"API Key created: {API_KEY}")
print(f"Use this in your requests: X-API-Key: {API_KEY}")
```

Run it:
```bash
cd services/api
python3 create_api_key.py
```

## Step 7: Verify Setup

### Test API

```bash
# Health check (no auth required)
curl http://localhost:8000/v1/meter/health

# Create an event (requires API key)
curl -X POST http://localhost:8000/v1/meter/events \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "tenant_id": "org_001",
    "resource": "billing",
    "feature": "invoice_generate",
    "quantity": 1,
    "metadata": {"user": "test_user"}
  }'
```

### Test UI

1. Open http://localhost:3000 in your browser
2. You should see the dashboard (may show empty data initially)

## Running Everything

### Terminal 1: API Service
```bash
cd services/api
source venv/bin/activate  # If using venv
uvicorn app.main:app --reload
```

### Terminal 2: UI Service
```bash
cd services/ui
npm run dev
```

### Terminal 3: Redis (if not running as service)
```bash
redis-server
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check database exists
psql -U postgres -l | grep metering
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Test connection
redis-cli
> ping
PONG
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID with actual process ID)
kill -9 <PID>

# Or change port in .env file
```

### Migration Issues

```bash
# Check current migration status
python3 -m alembic current

# Show migration history
python3 -m alembic history

# Rollback if needed
python3 -m alembic downgrade -1
```

## Development Workflow

1. **Start services**: API and UI in separate terminals
2. **Make changes**: Code changes auto-reload (API with --reload, UI with Vite HMR)
3. **Database changes**: Create new migration with `alembic revision --autogenerate`
4. **Test**: Use API docs at http://localhost:8000/docs

## Environment Variables Reference

### API Service (.env)
```bash
DATABASE_URL=postgresql://postgres:admin@localhost:5432/metering
REDIS_URL=redis://localhost:6379/0
API_HOST=0.0.0.0
API_PORT=8000
```

### UI Service (.env.local)
```bash
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

### Annotator (.env)
```bash
METERING_API_URL=http://localhost:8000
METERING_API_KEY=your_api_key_here
METERING_TRANSPORT_MODE=async
```

## Next Steps

1. Create your first API key
2. Test event ingestion via API docs
3. View events in the UI dashboard
4. Integrate the annotator in your Python projects

## Additional Resources

- API Documentation: http://localhost:8000/docs
- Project Structure: See PROJECT_STRUCTURE.md
- Architecture: See HLD.md and LLD.md

