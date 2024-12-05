from src.components.data_ingestion import DataIngestion
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.entity.config_entity import Data_ingestion_config, TrainingPipelineConfig
import sys

if __name__ == "__main__":
    try:
        traingning_pipeline_config = TrainingPipelineConfig()       
        data_ingestion_config = Data_ingestion_config(traingning_pipeline_config)
        Data_ingestion  = DataIngestion(data_ingestion_config)
        logging.info("Data ingestion started")
        data_ingestion_artifacts = Data_ingestion.initiate_data_ingestion()
        print(data_ingestion_artifacts)
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)