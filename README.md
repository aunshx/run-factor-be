# California Circuity Factor API - FastAPI Version

A simple, fast API for calculating transportation efficiency using circuity factors. Built with FastAPI, PostgreSQL caching, and OSRM integration.

## 🎯 What This Does

- **Calculate circuity factors** between two locations (road distance ÷ straight-line distance)
- **Cache results** in PostgreSQL - no duplicate calculations
- **Fast responses** - cached calculations return instantly
- **Clean API** - Simple JSON endpoints with validation
- **Docker ready** - Complete deployment with one command

## 📁 Project Structure

```
california-circuity-api/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic validation models
│   ├── database.py             # PostgreSQL setup
│   ├── services/
│   │   ├── distance_service.py # OSRM + Haversine calculations
│   │   └── cache_service.py    # Database caching logic
│   └── routers/
│       └── circuity.py         # API endpoints
├── data/                       # Your existing OSRM files
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Complete deployment
├── Dockerfile                  # API container
├── .env                        # Configuration
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone/create the project structure
mkdir california-circuity-api
cd california-circuity-api

# 2. Copy all the files from the artifacts above

# 3. Make sure your OSRM data is in the data/ folder
ls data/
# Should show: california-latest.osrm and other OSRM files

# 4. Start everything with Docker
docker-compose up -d

# 5. Check status
docker-compose ps

# 6. Test the API
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# 1. Install PostgreSQL locally
createdb circuity_db

# 2. Start your OSRM server (as you did before)
docker run -t -i -p 5001:5000 -v $(pwd)/data:/data osrm/osrm-backend osrm-routed --algorithm mld /data/california-latest.osrm

# 3. Install Python dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env if needed

# 5. Start the API
uvicorn app.main:app --reload --port 8000
```

## 📡 API Endpoints

### Base URL: `http://localhost:8000`

### 1. Calculate Circuity Factor

**POST `/calculate`**

```bash
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {
      "lat": 37.7749,
      "lng": -122.4194,
      "name": "San Francisco"
    },
    "destination": {
      "lat": 34.0522,
      "lng": -118.2437,
      "name": "Los Angeles"
    },
    "units": "miles"
  }'
```

**Response:**

```json
{
  "origin": {
    "lat": 37.7749,
    "lng": -122.4194,
    "name": "San Francisco"
  },
  "destination": {
    "lat": 34.0522,
    "lng": -118.2437,
    "name": "Los Angeles"
  },
  "road_distance": 382.45,
  "straight_distance": 347.42,
  "circuity_factor": 1.101,
  "efficiency_percent": 90.84,
  "units": "miles",
  "calculation_time_ms": 245,
  "cached": false
}
```

### 2. Get Calculation History

**GET `/history?limit=10`**

```bash
curl "http://localhost:8000/history?limit=10"
```

### 3. Get Statistics

**GET `/stats`**

```bash
curl "http://localhost:8000/stats"
```

Returns:

```json
{
  "total_calculations": 42,
  "average_circuity_factor": 1.234,
  "average_efficiency_percent": 81.05
}
```

### 4. Health Check

**GET `/health`**

```bash
curl "http://localhost:8000/health"
```

### 5. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## 🧪 Testing the API

### Test Basic Functionality

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Calculate SF to LA
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco"},
    "destination": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
    "units": "miles"
  }'

# 3. Run the same calculation again (should be cached)
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco"},
    "destination": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
    "units": "miles"
  }'

# 4. Check history
curl "http://localhost:8000/history"

# 5. Check stats
curl "http://localhost:8000/stats"
```

### Test Agricultural Routes

```bash
# Farm to Port route
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 36.7378, "lng": -119.7871, "name": "Fresno Farm"},
    "destination": {"lat": 37.8044, "lng": -122.2711, "name": "Oakland Port"},
    "units": "miles"
  }'
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/circuity_db

# OSRM
OSRM_HOST=localhost
OSRM_PORT=5001
OSRM_TIMEOUT=10

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### For Production

Update `.env` for production:

```bash
DATABASE_URL=postgresql://user:pass@prod-db:5432/circuity_db
OSRM_HOST=prod-osrm-server
API_HOST=0.0.0.0
API_PORT=8000
```

## 🗄️ Database Schema

The API automatically creates this table:

```sql
CREATE TABLE circuity_calculations (
    id SERIAL PRIMARY KEY,
    origin_lat DOUBLE PRECISION NOT NULL,
    origin_lng DOUBLE PRECISION NOT NULL,
    origin_name VARCHAR(100),
    destination_lat DOUBLE PRECISION NOT NULL,
    destination_lng DOUBLE PRECISION NOT NULL,
    destination_name VARCHAR(100),
    road_distance DOUBLE PRECISION NOT NULL,
    straight_distance DOUBLE PRECISION NOT NULL,
    circuity_factor DOUBLE PRECISION NOT NULL,
    efficiency_percent DOUBLE PRECISION NOT NULL,
    units VARCHAR(10) NOT NULL,
    calculation_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🚀 Deployment

### Docker Compose (Production)

```bash
# 1. Update environment variables for production
vim .env

# 2. Start services
docker-compose up -d

# 3. Check logs
docker-compose logs -f api

# 4. Scale if needed
docker-compose up -d --scale api=3
```

### Manual Deployment

```bash
# 1. Set up PostgreSQL
# 2. Set up OSRM server
# 3. Deploy API with gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🎯 Key Features

✅ **Simple & Fast** - Clean FastAPI with minimal dependencies
✅ **Smart Caching** - PostgreSQL caches all calculations
✅ **Input Validation** - Pydantic models validate all requests
✅ **OSRM Integration** - Uses your existing California routing data
✅ **Health Monitoring** - Built-in health checks for all services
✅ **Docker Ready** - Complete deployment with docker-compose
✅ **Agricultural Focus** - Perfect for farm-to-market analysis

## 🔍 What's Next

1. **Test the basic API** - Make sure everything works
2. **Load some test data** - Try various California routes
3. **Build a frontend** - React/Vue.js mapping interface
4. **Add more features** - Batch processing, route optimization
5. **Scale up** - Load balancer, multiple API instances

This gives you a solid, production-ready foundation for your California transportation efficiency analysis! 🚜📊
