-- California Circuity Factor Database Initialization
-- This script creates the database and required tables
-- Create the database (if not exists)
-- Note: This runs automatically due to POSTGRES_DB environment variable
-- Create the circuity_calculations table
CREATE TABLE IF NOT EXISTS circuity_calculations (
    id SERIAL PRIMARY KEY,
    -- Origin coordinates
    origin_lat DOUBLE PRECISION NOT NULL,
    origin_lng DOUBLE PRECISION NOT NULL,
    origin_name VARCHAR(100),
    -- Destination coordinates  
    destination_lat DOUBLE PRECISION NOT NULL,
    destination_lng DOUBLE PRECISION NOT NULL,
    destination_name VARCHAR(100),
    -- Calculation results
    road_distance DOUBLE PRECISION NOT NULL,
    straight_distance DOUBLE PRECISION NOT NULL,
    circuity_factor DOUBLE PRECISION NOT NULL,
    efficiency_percent DOUBLE PRECISION NOT NULL,
    units VARCHAR(10) NOT NULL CHECK (units IN ('miles', 'km')),
    calculation_time_ms INTEGER NOT NULL,
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_circuity_origin ON circuity_calculations (origin_lat, origin_lng);

CREATE INDEX IF NOT EXISTS idx_circuity_destination ON circuity_calculations (destination_lat, destination_lng);

CREATE INDEX IF NOT EXISTS idx_circuity_units ON circuity_calculations (units);

CREATE INDEX IF NOT EXISTS idx_circuity_created_at ON circuity_calculations (created_at DESC);

-- Create a composite index for cache lookups
CREATE INDEX IF NOT EXISTS idx_circuity_cache_lookup ON circuity_calculations (
    origin_lat,
    origin_lng,
    destination_lat,
    destination_lng,
    units
);

-- Insert some sample data for testing (optional)
INSERT INTO
    circuity_calculations (
        origin_lat,
        origin_lng,
        origin_name,
        destination_lat,
        destination_lng,
        destination_name,
        road_distance,
        straight_distance,
        circuity_factor,
        efficiency_percent,
        units,
        calculation_time_ms
    )
VALUES
    (
        37.7749,
        -122.4194,
        'San Francisco',
        34.0522,
        -118.2437,
        'Los Angeles',
        382.45,
        347.42,
        1.101,
        90.84,
        'miles',
        245
    ),
    (
        36.7378,
        -119.7871,
        'Fresno',
        37.8044,
        -122.2711,
        'Oakland',
        156.23,
        134.56,
        1.161,
        86.12,
        'miles',
        198
    ),
    (
        38.5816,
        -121.4944,
        'Sacramento',
        35.3733,
        -119.0187,
        'Bakersfield',
        278.91,
        251.34,
        1.110,
        90.09,
        'miles',
        176
    ) ON CONFLICT DO NOTHING;

-- Create a view for easy analysis
CREATE
OR REPLACE VIEW circuity_analysis AS
SELECT
    id,
    origin_name,
    destination_name,
    road_distance,
    straight_distance,
    circuity_factor,
    efficiency_percent,
    units,
    created_at,
    CASE
        WHEN circuity_factor <= 1.2 THEN 'Excellent'
        WHEN circuity_factor <= 1.4 THEN 'Good'
        WHEN circuity_factor <= 1.8 THEN 'Fair'
        ELSE 'Poor'
    END AS efficiency_rating,
    CASE
        WHEN circuity_factor BETWEEN 1.1
        AND 1.3 THEN 'Highway'
        WHEN circuity_factor BETWEEN 1.2
        AND 1.5 THEN 'Urban'
        WHEN circuity_factor BETWEEN 1.3
        AND 1.7 THEN 'Suburban'
        WHEN circuity_factor BETWEEN 1.4
        AND 2.0 THEN 'Rural'
        WHEN circuity_factor > 2.0 THEN 'Mountain/Complex'
        ELSE 'Unknown'
    END AS route_type
FROM
    circuity_calculations;

-- Grant necessary permissions (if needed for specific users)
-- GRANT ALL PRIVILEGES ON circuity_calculations TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE circuity_calculations_id_seq TO your_app_user;
-- Print success message
DO $ $ BEGIN RAISE NOTICE 'California Circuity Factor database initialized successfully!';

RAISE NOTICE 'Tables created: circuity_calculations';

RAISE NOTICE 'Views created: circuity_analysis';

RAISE NOTICE 'Sample data inserted for testing';

END $ $;