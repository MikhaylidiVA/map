-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create enum for roles
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer');

-- Note: Tables will be created by SQLAlchemy ORM in the backend application
-- This file is for additional database setup and extensions

-- Create spatial index template (will be applied to geometry columns)
-- CREATE INDEX idx_<table>_geometry ON <table> USING GIST (geometry);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE gis_platform TO postgres;
