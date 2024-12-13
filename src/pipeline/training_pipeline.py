import os,sys
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact, ModelTrainerArtifact
from src.entity.config_entity import TrainingPipelineConfig, Data_ingestion_config, Data_transformation_config, Data_validation_config, Model_trainer_config
from src.constant.training_pipeline import TRAINING_BUCKET_NAME
from src.cloud.s3_syncer import s3sync
class Trainingpipeline:
    def __init__(self):
        try:
            self.training_pipeline_config = TrainingPipelineConfig()
            self.s3_sync = s3sync()
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_ingestion(self):
        try:
            self.data_ingestion_config = Data_ingestion_config(training_pipeline_config=self.training_pipeline_config)
            logging.info("Data ingestion started!")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact= data_ingestion.initiate_data_ingestion()
            logging.info("Data ingestion completed!")
            return data_ingestion_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try: 
            data_validation_config = Data_validation_config(training_pipeline_config = self.training_pipeline_config)
            Data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
            logging.info("Data validation started")
            data_validation_artifacts = Data_validation.intiate_data_validation()
            logging.info("Data validation completed")
            print(data_validation_artifacts)
            return data_validation_artifacts
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact):
        try:
            data_transformation_config = Data_transformation_config(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=data_transformation_config)
            logging.info("Data Transformation started !")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data Transformation completed !")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_model_training(self, data_transformation_artifact: DataTransformationArtifact)-> ModelTrainerArtifact:
        try: 
            self.model_trainer_config:Model_trainer_config = Model_trainer_config(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(
                data_transformation_artifact= data_transformation_artifact,
                model_trainer_config=self.model_trainer_config,
                )
            logging.info("Model training started!")
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model training completed!")
            return model_trainer_artifact
        
            # logging.info("Model training started")
            # model_trainer_config = Model_trainer_config(traingning_pipeline_config)
            # model_trainer = ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
            # model_trainer_artifact = model_trainer.initiate_model_trainer()
            # logging.info("Model training completed")
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e 
    
     # artifacts to s3 bucket    
    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.artifact_dir,
                aws_bucket_url=aws_bucket_url
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    # model to s3 bucket  
    def sync_saved_model_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.model_dir, aws_bucket_url=aws_bucket_url
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_training(data_transformation_artifact=data_transformation_artifact)
            
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_to_s3()
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e