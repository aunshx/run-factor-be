# California Circuity Factor API

A FastAPI-based service for calculating transportation efficiency using circuity factors across California. Built with OSRM routing engine, PostgreSQL caching, and car routing profiles.

## What This API Does

Calculate the **circuity factor** between any two locations in California:
- **Circuity Factor** = Road Distance ÷ Straight-line Distance
- **Efficiency Percentage** = (1 ÷ Circuity Factor) × 100
- **Smart Caching** - Duplicate calculations return instantly from PostgreSQL
- **Car Routing** - Uses standard automotive routing for general transportation analysis

## Quick Start

### Prerequisites
- Docker and Docker Compose
- ~5GB free disk space
- Stable internet connection for initial data download

### 1. Create Project Structure

```bash
mkdir california-circuity-api
cd california-circuity-api
```

Create this exact file structure:

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
├── data/                           # Your OSRM files will go here
├── docker-compose.yml              # Docker setup
├── Dockerfile                      # API container
├── requirements.txt                # Python dependencies
├── init.sql                        # Database setup script
├── .env                           # Environment variables
└── README.md
```

**Create the empty `__init__.py` files:**
```bash
mkdir -p app/services app/routers
touch app/__init__.py
touch app/services/__init__.py  
touch app/routers/__init__.py
```

**Copy all the application files from the deployment guide artifacts into the correct locations.**

### 2. Create OSRM Routing Data

**Download California Map Data:**
```bash
mkdir -p data
cd data
curl -L -o california-latest.osm.pbf \
  "https://download.geofabrik.de/north-america/us/california-latest.osm.pbf"
cd ..
```

**Process Routing Data (30-40 minutes):**
```bash
# Extract routing graph with car profile
docker run --platform linux/amd64 -t -v $(pwd)/data:/data osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/california-latest.osm.pbf

# Partition graph
docker run --platform linux/amd64 -t -v $(pwd)/data:/data osrm/osrm-backend \
  osrm-partition /data/california-latest.osrm

# Customize graph
docker run --platform linux/amd64 -t -v $(pwd)/data:/data osrm/osrm-backend \
  osrm-customize /data/california-latest.osrm
```

### 3. Start the API

```bash
# Start all services
docker-compose up -d

# Verify everything is running
docker-compose ps

# Test the API
curl http://localhost:8000/health
```

## API Usage

### Base URL
`http://localhost:8000`

### Calculate Circuity Factor

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
  "origin": {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco"},
  "destination": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
  "road_distance": 382.45,
  "straight_distance": 347.42,
  "circuity_factor": 1.101,
  "efficiency_percent": 90.84,
  "units": "miles",
  "calculation_time_ms": 245,
  "cached": false
}
```

### Other Endpoints

- **GET `/health`** - Service health check
- **GET `/history?limit=10`** - View calculation history
- **GET `/stats`** - Get aggregate statistics
- **GET `/docs`** - Interactive API documentation

## Example Use Cases

### Agricultural Transport Analysis
```bash
# Farm to processing facility
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 36.7378, "lng": -119.7871, "name": "Fresno Farm"},
    "destination": {"lat": 37.8044, "lng": -122.2711, "name": "Oakland Port"},
    "units": "miles"
  }'
```

### Supply Chain Efficiency
```bash
# Distribution center to retail
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 34.0522, "lng": -118.2437, "name": "LA Distribution"},
    "destination": {"lat": 32.7157, "lng": -117.1611, "name": "San Diego Store"},
    "units": "miles"
  }'
```

## Architecture

### Services
- **FastAPI Application** (Port 8000) - REST API with validation
- **PostgreSQL Database** (Port 5600) - Calculation caching and history
- **OSRM Routing Engine** (Port 5001) - Route calculations with truck profile

### Key Features
- **Car Routing** - Standard automotive routing for general transportation analysis
- **Intelligent Caching** - Identical requests return cached results instantly
- **Input Validation** - Pydantic models ensure data quality
- **Health Monitoring** - Built-in health checks for all dependencies

## Configuration

### Environment Variables
Create `.env` file for custom configuration:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/circuity_db

# OSRM
OSRM_HOST=osrm
OSRM_PORT=5000
OSRM_TIMEOUT=10

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Docker Compose Ports
- API: `localhost:8000`
- PostgreSQL: `localhost:5600`
- OSRM: `localhost:5001`

## Development

### Local Development Setup
```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start supporting services
docker-compose up postgres osrm -d

# Run API locally
uvicorn app.main:app --reload --port 8000
```

### Database Access
```bash
# Connect to database
docker exec -it circuity_postgres psql -U postgres -d circuity_db

# View calculations
SELECT * FROM circuity_calculations ORDER BY created_at DESC LIMIT 10;

# Get statistics
SELECT 
    COUNT(*) as total_calculations,
    AVG(circuity_factor) as avg_circuity_factor,
    AVG(efficiency_percent) as avg_efficiency
FROM circuity_calculations;
```

### Required Files

You need to create these files with the complete code (see deployment guide for full contents):

- **app/main.py** - FastAPI application setup
- **app/models.py** - Pydantic validation models  
- **app/database.py** - PostgreSQL connection setup
- **app/services/distance_service.py** - OSRM and distance calculations
- **app/services/cache_service.py** - Database caching logic
- **app/routers/circuity.py** - API endpoint definitions
- **requirements.txt** - Python dependencies
- **Dockerfile** - API container configuration
- **docker-compose.yml** - Complete service orchestration
- **init.sql** - Database schema and setup
- **.env** - Environment configuration

## Troubleshooting

### Common Issues

**Health Check Fails:**
```bash
# Check service logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs osrm
```

**OSRM Processing Fails:**
- Ensure 5GB+ free disk space
- Verify california-latest.osm.pbf downloaded completely (~1.2GB)
- Add `--platform linux/amd64` flag on Apple Silicon Macs

**Database Connection Issues:**
```bash
# Restart database
docker-compose restart postgres

# Check database exists
docker exec -it circuity_postgres psql -U postgres -l
```

### Reset Everything
```bash
# Stop and remove all containers and data
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build
```

## Performance

### Typical Response Times
- **Cached calculations**: 50-100ms
- **New calculations**: 200-500ms
- **Complex routes**: 500-1000ms

### Capacity
- **OSRM Memory Usage**: ~3-4GB during processing, ~1GB running
- **PostgreSQL**: Scales to millions of cached calculations
- **API**: Handles 100+ concurrent requests

## Data Sources

- **Map Data**: OpenStreetMap via Geofabrik (California extract)
- **Routing Engine**: OSRM with car profile for standard automotive routing
- **Routing Profile**: Built-in car.lua profile optimized for general vehicle routing

## License

This project uses:
- OpenStreetMap data (ODbL license)
- OSRM routing engine (BSD license)
- FastAPI framework (MIT license)

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with description

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker logs: `docker-compose logs`
3. Verify health endpoint: `curl localhost:8000/health`
4. Open an issue with log details