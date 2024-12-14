from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.entity.config_entity import Data_ingestion_config, TrainingPipelineConfig, Data_validation_config, Data_transformation_config, Model_trainer_config
from src.components.model_trainer import ModelTrainer

import sys

if __name__ == "__main__":
    try:
        traingning_pipeline_config = TrainingPipelineConfig()       
        data_ingestion_config = Data_ingestion_config(traingning_pipeline_config)
        Data_ingestion  = DataIngestion(data_ingestion_config)
        logging.info("Data ingestion started")
        data_ingestion_artifacts = Data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed")
        print("Data ingestion completed")
        
        data_validation_config = Data_validation_config(traingning_pipeline_config)
        Data_validation = DataValidation(data_ingestion_artifacts, data_validation_config)
        logging.info("Data validation started")
        data_validation_artifacts = Data_validation.intiate_data_validation()
        logging.info("Data validation completed")
        print(data_validation_artifacts)
        
        data_transformation_config = Data_transformation_config(traingning_pipeline_config)
        logging.info("data Transformation started")
        data_transformation = DataTransformation(data_validation_artifacts, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("data Transformation completed")
        
        logging.info("Model training started")
        model_trainer_config = Model_trainer_config(traingning_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed")
    except Exception as e:
        raise NetworkSecurityException(e, sys)