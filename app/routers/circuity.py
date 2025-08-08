"""
API endpoints for circuity calculations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, test_connection
from app.models import CircuityRequest, CircuityResponse, HealthResponse, HistoryResponse
from app.services.distance_service import DistanceService
from app.services.cache_service import CacheService
from datetime import datetime

router = APIRouter()
distance_service = DistanceService()

@router.post("/calculate", response_model=CircuityResponse)
async def calculate_circuity(
    request: CircuityRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate circuity factor between two locations.
    
    Checks cache first, calculates if not found, then stores result.
    """
    try:
        # Check cache first
        cached_result = CacheService.get_cached_calculation(db, request)
        if cached_result:
            return cached_result
        
        # Calculate new result
        road_dist, straight_dist, circuity_factor, efficiency, calc_time = distance_service.calculate_circuity(
            request.origin.lat, request.origin.lng,
            request.destination.lat, request.destination.lng,
            request.units
        )
        
        # Create response
        response = CircuityResponse(
            origin=request.origin,
            destination=request.destination,
            road_distance=road_dist,
            straight_distance=straight_dist,
            circuity_factor=circuity_factor,
            efficiency_percent=efficiency,
            units=request.units,
            calculation_time_ms=calc_time,
            cached=False
        )
        
        # Save to cache
        CacheService.save_calculation(db, request, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}"
        )

@router.get("/history", response_model=List[HistoryResponse])
async def get_calculation_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent calculation history
    """
    try:
        calculations = CacheService.get_calculation_history(db, limit)
        
        return [
            HistoryResponse(
                id=calc.id,
                origin_lat=calc.origin_lat,
                origin_lng=calc.origin_lng,
                origin_name=calc.origin_name,
                destination_lat=calc.destination_lat,
                destination_lng=calc.destination_lng,
                destination_name=calc.destination_name,
                road_distance=calc.road_distance,
                straight_distance=calc.straight_distance,
                circuity_factor=calc.circuity_factor,
                units=calc.units,
                created_at=calc.created_at,
                calculation_time_ms=calc.calculation_time_ms
            )
            for calc in calculations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@router.get("/stats")
async def get_calculation_stats(db: Session = Depends(get_db)):
    """
    Get calculation statistics
    """
    try:
        stats = CacheService.get_calculation_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check health of services (OSRM and Database)
    """
    osrm_status = distance_service.test_osrm_connection()
    db_status = test_connection()
    
    status_code = status.HTTP_200_OK
    if not osrm_status or not db_status:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return HealthResponse(
        status="healthy" if osrm_status and db_status else "unhealthy",
        osrm_connected=osrm_status,
        database_connected=db_status,
        timestamp=datetime.now()
    )