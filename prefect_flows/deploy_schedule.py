"""
Deploy Prefect flow with scheduling
Run this script to create a scheduled deployment for automated training
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from training_flow import training_flow

# Create deployment with weekly schedule (every Sunday at 2 AM)
deployment = Deployment.build_from_flow(
    flow=training_flow,
    name="weekly-training",
    schedule=CronSchedule(cron="0 2 * * 0", timezone="UTC"),  # Every Sunday at 2 AM UTC
    work_queue_name="training",
    tags=["production", "ml-training", "phishing-detection"],
    description="Weekly automated retraining of phishing detection model",
    version="1.0.0"
)

if __name__ == "__main__":
    # Deploy the flow
    deployment.apply()
    print("✅ Deployment created successfully!")
    print("📅 Schedule: Every Sunday at 2:00 AM UTC")
    print("\nTo start the worker, run:")
    print("  prefect agent start -q training")
