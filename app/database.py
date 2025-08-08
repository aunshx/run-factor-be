"""
PostgreSQL database configuration and models
"""
import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/circuity_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CircuityCalculation(Base):
    """Database model for storing circuity calculations"""
    __tablename__ = "circuity_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Origin coordinates
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    origin_name = Column(String(100), nullable=True)
    
    # Destination coordinates  
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    destination_name = Column(String(100), nullable=True)
    
    # Calculation results
    road_distance = Column(Float, nullable=False)
    straight_distance = Column(Float, nullable=False)
    circuity_factor = Column(Float, nullable=False)
    efficiency_percent = Column(Float, nullable=False)
    units = Column(String(10), nullable=False)
    calculation_time_ms = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False