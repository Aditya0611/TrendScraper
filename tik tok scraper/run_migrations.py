"""
Migration Runner Script

This script helps run database migrations in the correct order.
It can be used to apply all migrations or specific ones.

Usage:
    # Run all migrations
    python run_migrations.py

    # Run specific migration
    python run_migrations.py 006_add_daily_snapshots.sql

    # Run migrations via Supabase connection
    python run_migrations.py --supabase
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Migration order (must be run in this sequence)
MIGRATION_ORDER = [
    "002_create_tiktok_table.sql",
    "003_add_trend_lifecycle_tracking.sql",
    "004_add_language_detection.sql",
    "005_add_collected_at_hour.sql",
    "006_add_daily_snapshots.sql",
    "007_add_covering_indexes.sql",
    "008_add_maintenance_policy.sql",
    "009_create_scheduler_settings.sql",
    "010_create_job_queue.sql",
]


def get_migration_files() -> List[Path]:
    """Get all migration files in order."""
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return []
    
    files = []
    for migration_name in MIGRATION_ORDER:
        migration_file = migrations_dir / migration_name
        if migration_file.exists():
            files.append(migration_file)
        else:
            logger.warning(f"Migration file not found: {migration_name}")
    
    return files


def read_migration_file(file_path: Path) -> str:
    """Read migration file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return ""


def run_migration_via_supabase(migration_sql: str, migration_name: str) -> bool:
    """Run migration via Supabase client."""
    try:
        from supabase import create_client, Client
        
        SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("SUPABASE_URL and SUPABASE_KEY must be set")
            return False
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Split SQL into individual statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        logger.info(f"Running {migration_name} via Supabase...")
        
        # Note: Supabase REST API doesn't support arbitrary SQL execution
        # This would need to be run via Supabase SQL Editor or psql
        logger.warning("Supabase REST API doesn't support arbitrary SQL execution")
        logger.info("Please run migrations via Supabase SQL Editor or psql connection")
        logger.info(f"Migration SQL for {migration_name}:")
        print("\n" + "="*60)
        print(f"Migration: {migration_name}")
        print("="*60)
        print(migration_sql)
        print("="*60 + "\n")
        
        return False
        
    except ImportError:
        logger.error("Supabase client not available. Install with: pip install supabase")
        return False
    except Exception as e:
        logger.error(f"Failed to run migration via Supabase: {e}")
        return False


def print_migration_instructions():
    """Print instructions for running migrations."""
    print("\n" + "="*60)
    print("MIGRATION INSTRUCTIONS")
    print("="*60)
    print("\nTo run migrations, you have several options:\n")
    
    print("1. Via Supabase SQL Editor (Recommended):")
    print("   - Go to your Supabase project dashboard")
    print("   - Navigate to SQL Editor")
    print("   - Copy and paste the migration SQL")
    print("   - Click 'Run'\n")
    
    print("2. Via psql (PostgreSQL client):")
    print("   - Connect to your Supabase database:")
    print("     psql 'postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres'")
    print("   - Run migrations:")
    print("     \\i migrations/002_create_tiktok_table.sql")
    print("     \\i migrations/003_add_trend_lifecycle_tracking.sql")
    print("     ...\n")
    
    print("3. Via Supabase CLI:")
    print("   - Install Supabase CLI: https://supabase.com/docs/guides/cli")
    print("   - Run: supabase db push\n")
    
    print("="*60 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific migration
        migration_name = sys.argv[1]
        migrations_dir = Path(__file__).parent / "migrations"
        migration_file = migrations_dir / migration_name
        
        if not migration_file.exists():
            logger.error(f"Migration file not found: {migration_file}")
            return
        
        migration_sql = read_migration_file(migration_file)
        if not migration_sql:
            return
        
        print("\n" + "="*60)
        print(f"Migration: {migration_name}")
        print("="*60)
        print(migration_sql)
        print("="*60 + "\n")
        
        if "--supabase" in sys.argv:
            run_migration_via_supabase(migration_sql, migration_name)
        else:
            print_migration_instructions()
    else:
        # Show all migrations
        print("\n" + "="*60)
        print("AVAILABLE MIGRATIONS")
        print("="*60 + "\n")
        
        migration_files = get_migration_files()
        
        if not migration_files:
            logger.error("No migration files found")
            return
        
        for i, migration_file in enumerate(migration_files, 1):
            print(f"{i}. {migration_file.name}")
            migration_sql = read_migration_file(migration_file)
            if migration_sql:
                # Show first few lines as preview
                lines = migration_sql.split('\n')[:5]
                print("   Preview:")
                for line in lines:
                    if line.strip() and not line.strip().startswith('--'):
                        print(f"   {line[:70]}...")
                        break
            print()
        
        print("="*60)
        print("\nTo run a specific migration:")
        print(f"  python {sys.argv[0]} <migration_file_name>")
        print("\nExample:")
        print(f"  python {sys.argv[0]} 006_add_daily_snapshots.sql")
        print("\n" + "="*60 + "\n")
        
        print_migration_instructions()


if __name__ == "__main__":
    main()
