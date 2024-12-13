import os
import sys 
import numpy as np 

"""
Common constant variable 
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME: str= "NetworkSecurity"
ARTIFACT_DIR: str = "Artifacts"
FILE_NAME: str  = "phisingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"
SCHEMA_FILE_PATH = os.path.join("data_schema", "schema.yaml")

SAVED_MODEL_DIR = os.path.join("saved_models")
MODEL_FILE_NAME = "model.pkl"
"""
Data ingestion variable 
"""
DATA_INGESTION_COLLECTION_NAME: str= "phising_data"
DATA_INGESTION_DATBASE_NANE: str= "Network_data"
DATA_INGESTION_DIR_NAME:str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2


"""
Data validation realated constant start with DATA_VALIDATION VAR NAME
    
"""
DATA_VALIDATION_DIR_NAMR:str = "data_validation"
DATA_VALIDATION_VALID_DIR: str = "validated"
DATA_VALIDATION_INVALID_DIR: str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"


"""
Data transformation realated constant start with DATA_TRANSFORMATION VAR NAME
"""
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DIR_NAME: str = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR:str = "transformed_object"
PREPROCESSING_OBJECT_FILE_NAME:str = "preprocessing.pkl"
# using knn imputer 
DATA_TRANSFORMATION_IMPUTER_PARAMS: dict = {
    "missing_values": np.nan, 
    "n_neighbors" : 3, 
    "weights" : "uniform"
}

"""
Model trainer realated constant start with DATA_TRANSFORMATION VAR NAME
"""
MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_MODEL_DIR:str = "trained_model"
MODEL_TRAINER_MODEL_NAME:str = "model.pkl"
MODEL_TRAINER_EXPECTED_SCORE: float = 0.6
MODEL_TRAINER_OVERFITTING_UNDERFITTING_THRESHOLD: float = 0.05

TRAINING_BUCKET_NAME = "networksecuritymodelbucket"