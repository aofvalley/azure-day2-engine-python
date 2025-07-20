-- Sample health check script for PostgreSQL
-- This script performs basic health checks on the database

-- Check database version and current time
SELECT 
    version() as postgresql_version,
    current_timestamp as current_time,
    current_database() as database_name;

-- Check database size
SELECT 
    pg_database.datname as database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) as size
FROM pg_database
WHERE pg_database.datname = current_database();

-- Check active connections
SELECT 
    count(*) as active_connections,
    max(max_conn.setting::int) as max_connections,
    round((count(*)::decimal / max(max_conn.setting::int)) * 100, 2) as connection_usage_percent
FROM pg_stat_activity 
CROSS JOIN pg_settings max_conn 
WHERE max_conn.name = 'max_connections'
  AND pg_stat_activity.state = 'active';

-- Check table count in current database
SELECT 
    schemaname,
    count(*) as table_count
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
GROUP BY schemaname
ORDER BY table_count DESC;