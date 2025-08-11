"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, List
from datetime import datetime

class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")

class Location(Coordinates):
    name: Optional[str] = Field(None, max_length=100, description="Optional location name")

class CircuityRequest(BaseModel):
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
    status: str
    osrm_connected: bool
    database_connected: bool
    timestamp: datetime

class HistoryResponse(BaseModel):
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

class PaginatedHistoryResponse(BaseModel):
    items: List[HistoryResponse] = Field(..., description="List of history items for current page")
    total_count: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")