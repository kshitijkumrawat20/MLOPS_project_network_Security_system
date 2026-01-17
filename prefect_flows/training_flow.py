"""
Prefect Flow for Automated Model Training
Orchestrates the complete training pipeline with scheduling
"""
import sys
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
from datetime import timedelta
import logging

# Add project root to path
sys.path.append('..')
from src.pipeline.training_pipeline import Trainingpipeline
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging as app_logger

@task(name="run_training_pipeline", retries=2, retry_delay_seconds=60)
def train_model():
    """
    Task to run the complete training pipeline
    """
    try:
        app_logger.info("Starting training pipeline via Prefect")
        training_pipeline = Trainingpipeline()
        training_pipeline.run_pipeline()
        app_logger.info("Training pipeline completed successfully")
        return {"status": "success", "message": "Model trained successfully"}
    except Exception as e:
        app_logger.error(f"Training pipeline failed: {str(e)}")
        raise NetworkSecurityException(e, sys)

@task(name="validate_model")
def validate_model():
    """
    Task to validate the trained model
    """
    try:
        from src.utils.main_utils.utils import load_object
        
        app_logger.info("Validating trained model")
        model = load_object("final_model/model.pkl")
        preprocessor = load_object("final_model/preprocessor.pkl")
        
        if model is None or preprocessor is None:
            raise ValueError("Model or preprocessor not found")
        
        app_logger.info("Model validation successful")
        return {"status": "success", "message": "Model validated"}
    except Exception as e:
        app_logger.error(f"Model validation failed: {str(e)}")
        raise

@flow(
    name="phishing-detection-training",
    description="Automated training pipeline for phishing detection model",
    task_runner=ConcurrentTaskRunner()
)
def training_flow():
    """
    Main Prefect flow for training orchestration
    """
    logging.info("="*50)
    logging.info("Starting Phishing Detection Training Flow")
    logging.info("="*50)
    
    # Step 1: Train model
    train_result = train_model()
    logging.info(f"Training result: {train_result}")
    
    # Step 2: Validate model
    validation_result = validate_model()
    logging.info(f"Validation result: {validation_result}")
    
    logging.info("="*50)
    logging.info("Training flow completed successfully!")
    logging.info("="*50)
    
    return {
        "training": train_result,
        "validation": validation_result
    }

if __name__ == "__main__":
    # Run the flow locally
    training_flow()
