"""
Example: Run Evidently monitoring on scheduled basis
Can be integrated with Prefect for automated monitoring
"""
import sys
sys.path.append('..')

from monitoring.evidently_monitor import PhishingModelMonitor
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
import pandas as pd
from src.logging.logger import logging

@task(name="check_data_drift")
def check_drift():
    """Check for data drift in recent predictions"""
    try:
        logging.info("Checking for data drift...")
        monitor = PhishingModelMonitor()
        
        # Load recent predictions
        current_data = pd.read_csv("final_model/predicted.csv")
        
        # Generate drift report
        drift_result = monitor.generate_data_drift_report(current_data)
        
        logging.info(f"Drift metrics: {drift_result['metrics']}")
        
        # Check if retraining needed
        needs_retraining = monitor.check_drift_threshold(drift_result)
        
        if needs_retraining:
            logging.warning("⚠️ Significant drift detected! Retraining recommended.")
        else:
            logging.info("✅ Drift within acceptable limits.")
        
        return {
            "needs_retraining": needs_retraining,
            "drift_metrics": drift_result['metrics'],
            "report_path": drift_result['report_path']
        }
    except Exception as e:
        logging.error(f"Drift monitoring failed: {str(e)}")
        raise

@task(name="trigger_retraining")
def trigger_retraining():
    """Trigger retraining pipeline if drift detected"""
    try:
        from training_flow import training_flow
        logging.info("Triggering retraining due to drift...")
        
        # Run training flow
        result = training_flow()
        
        logging.info(f"Retraining completed: {result}")
        return result
    except Exception as e:
        logging.error(f"Retraining failed: {str(e)}")
        raise

@flow(
    name="drift-monitoring-flow",
    description="Monitor data drift and trigger retraining if needed",
    task_runner=ConcurrentTaskRunner()
)
def drift_monitoring_flow():
    """
    Main flow for drift monitoring
    Checks drift and triggers retraining if threshold exceeded
    """
    logging.info("="*50)
    logging.info("Starting Drift Monitoring Flow")
    logging.info("="*50)
    
    # Check drift
    drift_result = check_drift()
    
    # Trigger retraining if needed
    if drift_result["needs_retraining"]:
        training_result = trigger_retraining()
        return {
            "status": "retraining_triggered",
            "drift": drift_result,
            "training": training_result
        }
    else:
        return {
            "status": "no_action_needed",
            "drift": drift_result
        }

if __name__ == "__main__":
    # Run monitoring flow
    result = drift_monitoring_flow()
    print(f"\n📊 Monitoring Result: {result}")
