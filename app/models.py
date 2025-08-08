"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime

class Coordinates(BaseModel):
    """Basic coordinate validation"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")

class Location(Coordinates):
    """Location with optional name"""
    name: Optional[str] = Field(None, max_length=100, description="Optional location name")

class CircuityRequest(BaseModel):
    """Request model for circuity calculation"""
    origin: Location
    destination: Location
    units: Literal["miles", "km"] = Field(default="miles", description="Distance units")
    
    @validator('origin', 'destination')
    def validate_coordinates(cls, v):
        """Ensure coordinates are valid numbers"""
        if not (-90 <= v.lat <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        if not (-180 <= v.lng <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v

class CircuityResponse(BaseModel):
    """Response model for circuity calculation"""
    origin: Location
    destination: Location
    road_distance: float = Field(..., description="Road distance in specified units")
    straight_distance: float = Field(..., description="Straight-line distance in specified units") 
    circuity_factor: float = Field(..., description="Road distance / straight distance")
    efficiency_percent: float = Field(..., description="Transportation efficiency percentage")
    units: str
    calculation_time_ms: int
    cached: bool = Field(..., description="Whether result was cached")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    osrm_connected: bool
    database_connected: bool
    timestamp: datetime

class HistoryResponse(BaseModel):
    """Historical calculation response"""
    id: int
    origin_lat: float
    origin_lng: float
    origin_name: Optional[str]
    destination_lat: float
    destination_lng: float
    destination_name: Optional[str]
    road_distance: float
    straight_distance: float
    circuity_factor: float
    units: str
    created_at: datetime
    calculation_time_ms: int