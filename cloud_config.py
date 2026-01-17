"""
Cloud MLOps Configuration for HuggingFace Spaces
Handles Prefect Cloud and Evidently integration via environment variables
"""
import os
import sys
from pathlib import Path

# Prefect Cloud Configuration
PREFECT_API_KEY = os.getenv("PREFECT_API_KEY")
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "https://api.prefect.cloud/api")
PREFECT_WORKSPACE = os.getenv("PREFECT_WORKSPACE")
AUTO_DEPLOY_FLOWS = os.getenv("AUTO_DEPLOY_FLOWS", "false").lower() == "true"

# Evidently Cloud Configuration (Optional)
EVIDENTLY_CLOUD_TOKEN = os.getenv("EVIDENTLY_CLOUD_TOKEN") or os.getenv("EVIDENTLY_API_KEY")
EVIDENTLY_PROJECT_ID = os.getenv("EVIDENTLY_PROJECT_ID")

# Feature Flags
ENABLE_PREFECT = PREFECT_API_KEY is not None
ENABLE_EVIDENTLY_CLOUD = EVIDENTLY_CLOUD_TOKEN is not None

# Monitoring Configuration
MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
DRIFT_CHECK_ENABLED = os.getenv("DRIFT_CHECK_ENABLED", "false").lower() == "true"

def setup_prefect_cloud():
    """Configure Prefect Cloud connection"""
    if not ENABLE_PREFECT:
        print("ℹ️  Prefect Cloud disabled - No API key provided")
        return False
    
    try:
        from prefect import settings
        
        print("🔧 Configuring Prefect Cloud...")
        os.environ["PREFECT_API_KEY"] = PREFECT_API_KEY
        os.environ["PREFECT_API_URL"] = PREFECT_API_URL
        
        if PREFECT_WORKSPACE:
            os.environ["PREFECT_WORKSPACE"] = PREFECT_WORKSPACE
        
        print("✅ Prefect Cloud configured successfully")
        return True
    except Exception as e:
        print(f"⚠️  Failed to configure Prefect Cloud: {e}")
        return False

def setup_evidently_cloud():
    """Configure Evidently Cloud connection"""
    if not ENABLE_EVIDENTLY_CLOUD:
        print("ℹ️  Evidently Cloud disabled - Using open source version")
        return False
    
    try:
        os.environ["EVIDENTLY_CLOUD_TOKEN"] = EVIDENTLY_CLOUD_TOKEN
        if EVIDENTLY_PROJECT_ID:
            os.environ["EVIDENTLY_PROJECT_ID"] = EVIDENTLY_PROJECT_ID
        
        print("✅ Evidently Cloud configured successfully")
        return True
    except Exception as e:
        print(f"⚠️  Failed to configure Evidently Cloud: {e}")
        return False

def initialize_monitoring():
    """Initialize monitoring systems"""
    print("\n" + "="*60)
    print("🔧 Cloud MLOps Configuration")
    print("="*60)
    
    # Setup Prefect
    prefect_ok = setup_prefect_cloud()
    
    # Setup Evidently
    evidently_ok = setup_evidently_cloud()
    
    # Create monitoring directories
    Path("monitoring/reports").mkdir(parents=True, exist_ok=True)
    Path("final_model").mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("✅ Monitoring Configuration Summary")
    print("="*60)
    print(f"Prefect Cloud:     {'✅ Enabled' if prefect_ok else '❌ Disabled'}")
    print(f"Evidently Cloud:   {'✅ Enabled' if evidently_ok else '❌ Open Source'}")
    print(f"Drift Monitoring:  {'✅ Enabled' if DRIFT_CHECK_ENABLED else '❌ Disabled'}")
    print("="*60 + "\n")
    
    return {
        "prefect": prefect_ok,
        "evidently": evidently_ok,
        "monitoring": MONITORING_ENABLED
    }

if __name__ == "__main__":
    # Run initialization
    config = initialize_monitoring()
    
    # Print configuration for debugging
    import json
    print("Configuration:", json.dumps(config, indent=2))
