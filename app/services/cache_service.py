"""
Database caching service for storing and retrieving calculations
"""
from sqlalchemy.orm import Session
from app.database import CircuityCalculation
from app.models import CircuityRequest, CircuityResponse, Location
from typing import Optional, List

class CacheService:
    
    @staticmethod
    def _create_cache_key(lat1: float, lng1: float, lat2: float, lng2: float, units: str) -> str:
        """
        Create a cache key from coordinates and units
        Round coordinates to 6 decimal places for reasonable precision
        """
        lat1_rounded = round(lat1, 6)
        lng1_rounded = round(lng1, 6) 
        lat2_rounded = round(lat2, 6)
        lng2_rounded = round(lng2, 6)
        return f"{lat1_rounded},{lng1_rounded}|{lat2_rounded},{lng2_rounded}|{units}"
    
    @staticmethod
    def get_cached_calculation(db: Session, request: CircuityRequest) -> Optional[CircuityResponse]:
        # Check both directions (A->B and B->A should give same result)
        calc = db.query(CircuityCalculation).filter(
            CircuityCalculation.origin_lat == round(request.origin.lat, 6),
            CircuityCalculation.origin_lng == round(request.origin.lng, 6),
            CircuityCalculation.destination_lat == round(request.destination.lat, 6),
            CircuityCalculation.destination_lng == round(request.destination.lng, 6),
            CircuityCalculation.units == request.units
        ).first()
        
        if not calc:
            # Try reverse direction
            calc = db.query(CircuityCalculation).filter(
                CircuityCalculation.origin_lat == round(request.destination.lat, 6),
                CircuityCalculation.origin_lng == round(request.destination.lng, 6),
                CircuityCalculation.destination_lat == round(request.origin.lat, 6),
                CircuityCalculation.destination_lng == round(request.origin.lng, 6),
                CircuityCalculation.units == request.units
            ).first()
        
        if calc:
            return CircuityResponse(
                origin=request.origin,
                destination=request.destination,
                road_distance=calc.road_distance,
                straight_distance=calc.straight_distance,
                circuity_factor=calc.circuity_factor,
                efficiency_percent=calc.efficiency_percent,
                units=calc.units,
                calculation_time_ms=calc.calculation_time_ms,
                cached=True
            )
        
        return None
    
    @staticmethod
    def save_calculation(db: Session, request: CircuityRequest, response: CircuityResponse) -> None:
        """
        Save calculation to database
        """
        calc = CircuityCalculation(
            origin_lat=round(request.origin.lat, 6),
            origin_lng=round(request.origin.lng, 6),
            origin_name=request.origin.name,
            destination_lat=round(request.destination.lat, 6),
            destination_lng=round(request.destination.lng, 6),
            destination_name=request.destination.name,
            road_distance=response.road_distance,
            straight_distance=response.straight_distance,
            circuity_factor=response.circuity_factor,
            efficiency_percent=response.efficiency_percent,
            units=response.units,
            calculation_time_ms=response.calculation_time_ms
        )
        
        db.add(calc)
        db.commit()
    
    @staticmethod
    def get_calculation_history(db: Session, limit: int = 50) -> List[CircuityCalculation]:
        """
        Get recent calculation history
        """
        return db.query(CircuityCalculation)\
                 .order_by(CircuityCalculation.created_at.desc())\
                 .limit(limit)\
                 .all()
    
    @staticmethod
    def get_calculation_stats(db: Session) -> dict:
        """
        Get basic statistics about calculations
        """
        total_calculations = db.query(CircuityCalculation).count()
        
        if total_calculations == 0:
            return {
                "total_calculations": 0,
                "average_circuity_factor": 0,
                "average_efficiency_percent": 0
            }
        
        # Calculate averages
        avg_circuity = db.query(
            db.func.avg(CircuityCalculation.circuity_factor)
        ).scalar()
        
        avg_efficiency = db.query(
            db.func.avg(CircuityCalculation.efficiency_percent)
        ).scalar()
        
        return {
            "total_calculations": total_calculations,
            "average_circuity_factor": round(float(avg_circuity or 0), 3),
            "average_efficiency_percent": round(float(avg_efficiency or 0), 2)
        }