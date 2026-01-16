# Test code
# import os
# from pymongo.mongo_client import MongoClient
# from dotenv import load_dotenv
# load_dotenv()
# uri = os.getenv("MONGODB_URL")

# # Create a new client and connect to the server
# client = MongoClient(uri)

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


import os
import sys
import json
import certifi
import pandas as pd 
import numpy as np 
# import pymongo 
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
print(MONGODB_URL)
ca = certifi.where() # ca=  certified authority 

class NetworkDataExtract():
    def __init__(self):
        try: 
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    def csv_to_json_converter(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records 
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_to_mongodb(self, records, database, collection):
        try: 
            self.database = database 
            self.collection = collection 
            self.records = records 
            
            self.mongo_client = pymongo.MongoClient(MONGODB_URL)
            self.database = self.mongo_client[self.database]
            
            self.collection = self.database[self.collection ]
            self.collection.insert_many(self.records)
            return(len(self.records))
        except Exception as e: 
            raise NetworkSecurityException(e, sys)
        
if __name__  == "__main__":
    FILE_PATH = "data\phisingData.csv"
    DATABASE = "Network_data"
    Collection = "phising_data"
    obj = NetworkDataExtract()
    records = obj.csv_to_json_converter(file_path=FILE_PATH)
    print("records converted to json")
    noOfRecords = obj.insert_data_to_mongodb(records,DATABASE, Collection)
    print(noOfRecords)