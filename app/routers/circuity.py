"""
Updated API endpoints for circuity calculations with pagination and search
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional

from app.database import get_db, test_connection
from app.models import CircuityRequest, CircuityResponse, HealthResponse, HistoryResponse, PaginatedHistoryResponse
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
        cached_result = CacheService.get_cached_calculation(db, request)
        if cached_result:
            return cached_result
        
        road_dist, straight_dist, circuity_factor, efficiency, calc_time = distance_service.calculate_circuity(
            request.origin.lat, request.origin.lng,
            request.destination.lat, request.destination.lng,
            request.units
        )
        
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
        
        CacheService.save_calculation(db, request, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}"
        )

@router.get("/history", response_model=PaginatedHistoryResponse)
async def get_calculation_history(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search in origin/destination names"),
    sort_by: str = Query("newest", description="Sort by: newest, oldest, circuity_asc, circuity_desc"),
    db: Session = Depends(get_db)
):
    """
    Get paginated calculation history with search and sorting
    """
    try:
        result = CacheService.get_calculation_history_paginated(
            db, page=page, limit=limit, search=search, sort_by=sort_by
        )
        
        calculations, total_count = result
        total_pages = (total_count + limit - 1) // limit 
        
        history_items = [
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
        
        return PaginatedHistoryResponse(
            items=history_items,
            total_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

# Keep the old endpoint for backward compatibility
@router.get("/history_simple", response_model=List[HistoryResponse])
async def get_calculation_history_simple(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent calculation history (legacy endpoint for backward compatibility)
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