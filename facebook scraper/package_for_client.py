#!/usr/bin/env python3
"""
Package Facebook Scraper for Client Delivery
=============================================
Creates a clean zip file with only essential files for the client.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Essential files to include
ESSENTIAL_FILES = [
    # Core scraper files
    'base.py',
    'industrial_scraper.py',
    'perfect_scraper.py',
    'automated_scraper.py',
    'sentiment_analyzer.py',
    'free_api_scraper.py',
    
    # Configuration
    'requirements.txt',
    'README.md',
    'sprint1_signoff_proof.md',
    'create_supabase_table.sql',
    'walkthrough.md',
    
    # Demos
    'perfect_demo.py',
    'industrial_demo.py',
    
    # Config directory (categories.json is REQUIRED)
    'config/categories.json',
    'config/industrial_config.json',
    'config/proxies.txt',
    
    # GitHub Actions workflow
    '.github/workflows/scraper.yml',
    
    # Verification and Testing
    'tests/test_proxy_enforcement.py',
    'verify_db_pipeline.py',
    'check_tables.py',
]

# Files/directories to exclude
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.log',
    '.env',
    'venv',
    'sessions',
    'data',
    'logs',
    'debug',
    '*.zip',
    '.git',
    '.gitignore',
    'demo.py',
    'free_api_demo.py',
    'test_supabase.py',
    'automated_scraper.py.bak',
]

def should_exclude(file_path: Path) -> bool:
    """Check if file should be excluded"""
    file_str = str(file_path)
    file_name = file_path.name
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_str or file_name == pattern or file_name.endswith(pattern.replace('*', '')):
            # But keep README.md
            if file_name == 'README.md':
                continue
            return True
    
    return False

def create_client_package():
    """Create zip package for client"""
    
    project_root = Path(__file__).parent
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f'facebook_scraper_client_{timestamp}.zip'
    zip_path = project_root / zip_name
    
    print("=" * 80)
    print("Creating Client Package")
    print("=" * 80)
    print(f"Project root: {project_root}")
    print(f"Output: {zip_path}")
    print()
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        files_added = []
        files_skipped = []
        
        # Add essential files
        print("Adding essential files...")
        for file_path in ESSENTIAL_FILES:
            full_path = project_root / file_path
            
            if full_path.exists():
                # Get relative path for zip
                arcname = file_path
                zipf.write(full_path, arcname)
                files_added.append(file_path)
                print(f"  [+] {file_path}")
            else:
                files_skipped.append(file_path)
                print(f"  [-] {file_path} (not found)")
        
        print()
        print("=" * 80)
        print("Package Summary")
        print("=" * 80)
        print(f"Files added: {len(files_added)}")
        print(f"Files skipped: {len(files_skipped)}")
        print()
        print("Package created successfully!")
        print(f"Location: {zip_path}")
        print(f"Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        print()
        print("Files included:")
        for file in files_added:
            print(f"  - {file}")
        
        if files_skipped:
            print()
            print("Files not found (optional):")
            for file in files_skipped:
                print(f"  - {file}")
    
    return zip_path

if __name__ == "__main__":
    try:
        zip_path = create_client_package()
        print()
        print("=" * 80)
        print("[SUCCESS] Client package created successfully!")
        print(f"[PACKAGE] File: {zip_path.name}")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Error creating package: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

