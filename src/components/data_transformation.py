import sys
import os
import numpy as np 
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from src.constant.training_pipeline import TARGET_COLUMN
from src.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from src.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact,
)
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.utils.main_utils.utils import save_np_array, save_object
from src.entity.config_entity import Data_transformation_config
class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: Data_transformation_config):
        try:
            self.data_validation_artifact:DataValidationArtifact = data_validation_artifact
            self.data_transformation_config:Data_transformation_config = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod 
    def read_data(file_path) -> pd.DataFrame:
        try: 
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def get_data_transformer_object(self) -> Pipeline:
        """
        it initialises a KNNImputer object with the parameter specified in the training_pipeline.py file and returns
        a pipeline with the KNNImputer object as the first step.

        args:
            cls: DataTransformation
        Returns:
            a pipeline object 
        """
        logging.info("Entered get_data_transformation_object methof of transformation class")
        
        try:
            knn_imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"intialise knn imputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            pipeline = Pipeline(steps=[("imputer", knn_imputer)])
            return pipeline
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def initiate_data_transformation(self)-> DataTransformationArtifact:
        try: 
            logging.info("Started data transformation!")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
            # training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN],axis = 1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1,0)
            # testing dataframe 
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN],axis = 1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1,0)
            
            preprocessor = self.get_data_transformer_object()
            preprocessor_obj = preprocessor.fit(input_feature_train_df)
            logging.info("Preprocessor object created and fitted on training data")
            
            transformed_input_train_feature = preprocessor_obj.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_obj.transform(input_feature_test_df)
            
            # combining transformed input features with target feature
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]
            
            # save numpy array data
            save_np_array(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_np_array(self.data_transformation_config.transformed_test_file_path,array = test_arr )
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_obj)
            save_object("final_model/preprocessor.pkl", preprocessor_obj)
            
            # preparing artifacts 
            Data_transformation_artifact = DataTransformationArtifact(
            transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
            transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
            transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
            )
            return Data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
