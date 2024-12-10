from src.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging  
import os, sys

class NetworkSecurityModel:
    def __init__(self, preprocessing_object, trained_model_object):
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object
        
    def predict(self, X):
        try:
            transformed_feature = self.preprocessing_object.transform(X)
            y_hat = self.trained_model_object.predict(transformed_feature)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    