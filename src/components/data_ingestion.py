from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.entity.config_entity import Data_ingestion_config
from src.entity.artifact_entity import DataIngestionArtifact
import os, sys
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
# import pymongo
import numpy as np
from src.data.sqlite_manager import PhishingDataManager

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: Data_ingestion_config):
        try:
            self.data_ingestion_config = data_ingestion_config
            self.db_manager = PhishingDataManager()
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_collection_as_dataframe(self):
        """Export data from SQLite instead of MongoDB"""
        try:
            # Get all training data
            df = self.db_manager.get_training_data(include_new_only=False)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def move_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file)  
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file, index=False, header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def data_train_test_split(self,dataframe:pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )  
            logging.info("Trained test spltting done on dataframe")
            dir_path = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info("Exporting train and test file path")
            train_set.to_csv(
                self.data_ingestion_config.train_file_path, index = False, header = True
            )
            test_set.to_csv(
                self.data_ingestion_config.test_file_path, index = False, header = True
            )
            logging.info("Exported train and test file path.")
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.move_data_into_feature_store(dataframe)
            self.data_train_test_split(dataframe)
            
            # Mark data as used
            self.db_manager.mark_data_as_trained()
            
            data_ingestion_artifact = DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.train_file_path,
                test_file_path=self.data_ingestion_config.test_file_path
            )
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

