import os
import sys 

"""
Common constant variable 
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME: str= "NetworkSecurity"
ARTIFACT_DIR: str = "Artifacts"
FILE_NAME: str  = "phisingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

"""
Data ingestion variable 
"""
DATA_INGESTION_COLLECTION_NAME: str= "phising_data"
DATA_INGESTION_DATBASE_NANE: str= "Network_data"
DATA_INGESTION_DIR_NAME:str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2
