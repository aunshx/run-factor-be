# California Circuity API - Complete Deployment Guide

## 📋 Prerequisites

- Docker and Docker Compose installed
- Your OSRM data files from previous setup
- ~2GB free disk space

## 🗂️ File Structure Setup

Create this exact structure:

```
california-circuity-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── distance_service.py
│   │   └── cache_service.py
│   └── routers/
│       ├── __init__.py
│       └── circuity.py
├── data/                           # Your existing OSRM files
│   ├── california-latest.osrm
│   ├── california-latest.osrm.cells
│   ├── california-latest.osrm.cnbg
│   └── (other OSRM files...)
├── docker-compose.yml              # Docker setup
├── Dockerfile                      # API container
├── requirements.txt                # Python dependencies
├── init.sql                        # Database setup script
├── .env                           # Environment variables
└── README.md
```

## 🚀 Step-by-Step Deployment

### Step 1: Create Project Directory

```bash
mkdir california-circuity-api
cd california-circuity-api
```

### Step 2: Copy Your OSRM Data

```bash
# Copy your existing OSRM data folder
cp -r /path/to/your/data ./data

# Verify OSRM files exist
ls -la data/
# Should show california-latest.osrm and related files
```

### Step 3: Create All Required Files

Copy all the code from the artifacts above into these files:

1. **app/main.py** - FastAPI application
2. **app/models.py** - Pydantic validation models  
3. **app/database.py** - PostgreSQL connection
4. **app/services/distance_service.py** - Distance calculations
5. **app/services/cache_service.py** - Database caching
6. **app/routers/circuity.py** - API endpoints
7. **requirements.txt** - Python dependencies
8. **Dockerfile** - API container setup
9. **docker-compose.yml** - Complete deployment
10. **init.sql** - Database initialization
11. **.env** - Environment configuration

Don't forget the empty `__init__.py` files:

```bash
touch app/__init__.py
touch app/services/__init__.py  
touch app/routers/__init__.py
```

### Step 4: Configure Environment

Create `.env` file:

```bash
DATABASE_URL=postgresql://postgres:password@postgres:5432/circuity_db
OSRM_HOST=osrm
OSRM_PORT=5000
OSRM_TIMEOUT=10
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 5: Deploy Everything

```bash
# Start all services
docker-compose up -d

# Check if everything is running
docker-compose ps
```

You should see:

```
Name                   Command               State           Ports
circuity_api       uvicorn app.main:app --h ...   Up      0.0.0.0:8000->8000/tcp
circuity_osrm      osrm-routed --algorithm  ...   Up      0.0.0.0:5001->5000/tcp
circuity_postgres  docker-entrypoint.sh pos ...   Up      0.0.0.0:5432->5432/tcp
```

### Step 6: Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "osrm_connected": true,
#   "database_connected": true,
#   "timestamp": "2024-01-20T..."
# }

# Test calculation
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco"},
    "destination": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
    "units": "miles"
  }'
```

### Step 7: Check Logs (if issues)

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs osrm
```

## 🗄️ Database Access

### Connect to PostgreSQL

```bash
# Connect via Docker
docker exec -it circuity_postgres psql -U postgres -d circuity_db

# Or connect locally (if you have psql installed)
psql -h localhost -p 5432 -U postgres -d circuity_db
```

### Useful SQL Queries

```sql
-- Check if tables exist
\dt

-- View all calculations
SELECT * FROM circuity_calculations ORDER BY created_at DESC LIMIT 10;

-- View analysis
SELECT * FROM circuity_analysis;

-- Get statistics
SELECT 
    COUNT(*) as total_calculations,
    AVG(circuity_factor) as avg_circuity_factor,
    AVG(efficiency_percent) as avg_efficiency
FROM circuity_calculations;
```

## 🧪 Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Calculate Circuity

```bash
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 36.7378, "lng": -119.7871, "name": "Fresno"},
    "destination": {"lat": 37.8044, "lng": -122.2711, "name": "Oakland"},
    "units": "miles"
  }'
```

### 3. View History

```bash
curl "http://localhost:8000/history?limit=5"
```

### 4. Get Statistics

```bash
curl "http://localhost:8000/stats"
```

### 5. Interactive Documentation

Visit: <http://localhost:8000/docs>

## 🔧 Troubleshooting

### Common Issues

**1. OSRM files not found:**

```bash
# Check your data folder
ls -la data/
# Make sure california-latest.osrm exists

# Check OSRM container logs
docker-compose logs osrm
```

**2. Database connection failed:**

```bash
# Check PostgreSQL container
docker-compose logs postgres

# Verify database was created
docker exec -it circuity_postgres psql -U postgres -l
```

**3. API not starting:**

```bash
# Check API logs
docker-compose logs api

# Check if port 8000 is already in use
lsof -i :8000
```

**4. Permission errors:**

```bash
# Fix Docker permissions
sudo chown -R $USER:$USER ./data
```

### Reset Everything

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes (deletes database data)
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build
```

## 🚀 Production Considerations

### Security

- Change default PostgreSQL password
- Add API authentication
- Use environment secrets for passwords
- Enable SSL/HTTPS

### Scaling

- Add nginx reverse proxy
- Use PostgreSQL connection pooling
- Scale API with multiple instances
- Add Redis for caching

### Monitoring

- Add logging aggregation
- Set up health monitoring
- Configure alerts
- Monitor database performance

## ✅ Success Checklist

- [ ] All containers running (`docker-compose ps`)
- [ ] Health check returns "healthy" (`curl localhost:8000/health`)
- [ ] Can calculate circuity factor (`POST /calculate`)
- [ ] Database stores calculations (`GET /history`)
- [ ] OSRM routes working (`GET /health` shows osrm_connected: true)
- [ ] Interactive docs accessible (`http://localhost:8000/docs`)

You now have a fully functional California Circuity Factor API! 🎉
