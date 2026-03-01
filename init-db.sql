-- LuminalLib Database Initialization Script
-- This script runs when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if it doesn't exist (already created by POSTGRES_DB env var, but keeping for reference)
-- CREATE DATABASE luminallib_db;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO postgres;

-- Tables are created by SQLAlchemy ORM (in python code)
-- This script just sets up the database and extensions

COMMENT ON DATABASE luminallib_db IS 'LuminalLib - Book Library and Summarization Platform';
