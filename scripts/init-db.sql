-- =============================================================================
-- WealthBot Database Initialization Script
-- =============================================================================
-- This script runs automatically when the PostgreSQL container starts for the
-- first time. It sets up extensions and initial configurations.

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for fuzzy text search (useful for merchant name matching)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types (optional, using string enums in SQLAlchemy instead)
-- This is here as a reference for future database-level enums

-- Grant permissions (for production, use more restrictive permissions)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wealthbot_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wealthbot_user;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'WealthBot database initialized successfully at %', now();
END $$;
