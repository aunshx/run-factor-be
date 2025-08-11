"""
Distance calculation service using OSRM and Haversine formula
"""
import math
import time
import requests
import os
from typing import Tuple

class DistanceService:
    def __init__(self):
        self.osrm_host = os.getenv("OSRM_HOST", "localhost")
        self.osrm_port = os.getenv("OSRM_PORT", "5001")
        self.osrm_url = f"http://{self.osrm_host}:{self.osrm_port}"
        self.timeout = int(os.getenv("OSRM_TIMEOUT", "10"))
    
    def calculate_straight_distance(self, lat1: float, lng1: float, lat2: float, lng2: float, units: str = "miles") -> float:
        """
        Calculate straight-line distance using Haversine formula
        """
        R = 3959 if units == "miles" else 6371  # miles or kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        # Haversine formula
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)
    
    def calculate_road_distance(self, lat1: float, lng1: float, lat2: float, lng2: float, units: str = "miles") -> float:
        """
        Calculate road distance using OSRM
        """
        try:
            url = f"{self.osrm_url}/route/v1/driving/{lng1},{lat1};{lng2},{lat2}"
            params = {
                "overview": "false",
                "alternatives": "false", 
                "steps": "false"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                raise Exception(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            if not data.get("routes"):
                raise Exception("No routes found")
            
            distance_km = data["routes"][0]["distance"] / 1000
            distance = distance_km * 0.621371 if units == "miles" else distance_km
            
            return round(distance, 2)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OSRM connection error: {str(e)}")
        except Exception as e:
            raise Exception(f"Road distance calculation failed: {str(e)}")
    
    def calculate_circuity(self, lat1: float, lng1: float, lat2: float, lng2: float, units: str = "miles") -> Tuple[float, float, float, float, int]:
        """
        Calculate both distances and circuity factor
        Returns: (road_distance, straight_distance, circuity_factor, efficiency_percent, calculation_time_ms)
        """
        start_time = time.time()
        
        straight_distance = self.calculate_straight_distance(lat1, lng1, lat2, lng2, units)
        road_distance = self.calculate_road_distance(lat1, lng1, lat2, lng2, units)
        
        circuity_factor = round(road_distance / straight_distance, 3)
        efficiency_percent = round((straight_distance / road_distance) * 100, 2)
        
        calculation_time = int((time.time() - start_time) * 1000)
        
        return road_distance, straight_distance, circuity_factor, efficiency_percent, calculation_time
    
    def test_osrm_connection(self) -> bool:
        """
        Test OSRM connection with a simple route
        """
        try:
            # Test route: SF to Oakland
            url = f"{self.osrm_url}/route/v1/driving/-122.4194,37.7749;-122.2711,37.8044"
            params = {"overview": "false"}
            
            response = requests.get(url, params=params, timeout=5)
            return response.status_code == 200 and response.json().get("code") == "Ok"
            
        except Exception:
            return False