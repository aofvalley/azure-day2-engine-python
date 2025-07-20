-- Sample backup verification script for PostgreSQL
-- This script checks backup-related information and settings

-- Check current backup settings and last backup information
SELECT 
    name,
    setting,
    unit,
    short_desc
FROM pg_settings 
WHERE name IN (
    'archive_mode',
    'archive_command',
    'wal_level',
    'max_wal_senders',
    'wal_keep_segments'
)
ORDER BY name;

-- Check WAL files information
SELECT 
    count(*) as wal_files_count,
    pg_size_pretty(sum(size)) as total_wal_size
FROM pg_ls_waldir();

-- Check replication slots if any
SELECT 
    slot_name,
    slot_type,
    database,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;

-- Database statistics for backup planning
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 10;