import os
import zipfile
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Packaging")

def create_delivery_zip():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"tiktok_scraper_delivery_{timestamp}.zip"
    
    # Files and directories to include
    include_files = [
        "base.py",
        "worker_apscheduler.py",
        "proxy_pool.py",
        "supabase_utils.py",
        "logging_metrics.py",
        "admin_api.py",
        "job_queue.py",
        "offline_queue_worker.py",
        "cache_manager.py",
        "requirements.txt",
        "requirements-base.txt",
        "README.md",
        ".env.example",
        "odoo_sync.py",
        "start_worker.bat",
        "start_worker.sh",
        "start_scheduler.bat",
        "start_scheduler.sh",
        "start_admin_api.bat",
        "start_admin_api.sh",
        "cron_setup.sh"
    ]
    
    include_dirs = [
        "migrations",
        "odoo_module",
        "docs"
    ]
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add individual files
            for file in include_files:
                if os.path.exists(file):
                    logger.info(f"Adding file: {file}")
                    zipf.write(file, arcname=file)
                else:
                    logger.warning(f"File missing: {file}")
            
            # Add directories
            for dir_name in include_dirs:
                if os.path.exists(dir_name):
                    logger.info(f"Adding directory: {dir_name}")
                    for root, dirs, files in os.walk(dir_name):
                        for file in files:
                            if file == "__pycache__" or file.endswith(".pyc"):
                                continue
                            
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.getcwd())
                            zipf.write(file_path, arcname=arcname)
                else:
                    logger.warning(f"Directory missing: {dir_name}")
                    
        logger.info(f"✅ Successfully created: {zip_filename}")
        return zip_filename
        
    except Exception as e:
        logger.error(f"❌ Failed to create zip: {e}")
        return None

if __name__ == "__main__":
    create_delivery_zip()
