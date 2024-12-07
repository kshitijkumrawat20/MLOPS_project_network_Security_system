from src.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from src.entity.config_entity import Data_validation_config
from src.exception.exception import NetworkSecurityException
from src.constant.training_pipeline import SCHEMA_FILE_PATH
from src.logging.logger import logging
from scipy.stats import ks_2samp
import pandas as pd
import os, sys
from src.utils.main_utils.utils import read_yaml_file, write_yaml_file

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: Data_validation_config):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod 
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
       
    def validate_number_of_columns(self, dataframe: pd.DataFrame)->  bool:
        try: 
            number_of_columns = len(self._schema_config)
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len(dataframe.columns)==number_of_columns:
                return True 
            else:
                return False
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    def detect_drift(self,base_df, current_df, threshold=0.05)->bool:
        try:
            status = True
            report = {}
            for column in base_df:
                d1 = base_df[column]
                d2 = current_df[column]
                is_sample_dist = ks_2samp(d1, d2)
                if threshold <= is_sample_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report.update({column: {
                    "p_value": float(is_sample_dist.pvalue),
                    "drift_status": is_found
                }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            # Create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys )  
        
    def intiate_data_validation(self)-> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            # read the data from train and test csv
            train_df = DataValidation.read_data(train_file_path)
            test_df = DataValidation.read_data(test_file_path)
            
            # validating no. of columns 
            status = self.validate_number_of_columns(dataframe=train_df)
            if not status:
                error_message = f"{train_file_path} does not match schema"  
                
                
            status = self.validate_number_of_columns(dataframe=test_df)
            if not status:
                error_message = f"{test_file_path} does not match schema"
        
            # check data drift
            status = self.detect_drift(base_df=train_df, current_df=test_df)   
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path) 
            os.makedirs(dir_path, exist_ok=True)
            
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False, header = True)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header = True)
            
            
            data_validation_artifacts = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.train_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)   