import os,sys
import certifi
from dotenv import load_dotenv
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.pipeline.training_pipeline import Trainingpipeline
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from src.utils.ml_utils.model.estimator import NetworkSecurityModel
from prometheus_fastapi_instrumentator import Instrumentator
import time
from prometheus_client import Counter, Histogram, Gauge

ca = certifi.where()
load_dotenv()
mongo_db_uri = os.getenv("MONGO_DB_URI")

from src.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from src.constant.training_pipeline import DATA_INGESTION_DATBASE_NANE
from src.utils.main_utils.utils import load_object
# import pymongo

# client = pymongo.MongoClient(mongo_db_uri,tlsCAFile=ca)
# database = client[DATA_INGESTION_DATBASE_NANE]
# collection = database[DATA_INGESTION_COLLECTION_NAME]
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")  
app = FastAPI()

# Prometheus metrics
prediction_counter = Counter('phishing_predictions_total', 'Total number of predictions', ['result'])
prediction_latency = Histogram('phishing_prediction_latency_seconds', 'Prediction latency in seconds')
phishing_detected = Gauge('phishing_threats_detected', 'Number of phishing threats detected')
safe_sites = Gauge('safe_sites_count', 'Number of safe sites detected')

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

orgin = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=orgin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/", tags = ["authentication"])
# async def index():
#     return RedirectResponse(url="/docs")

@app.get("/train")
async def training_route():
    try: 
        training_pipeline = Trainingpipeline()
        training_pipeline.run_pipeline()
        return Response("Training successfull !!")
    except Exception as e:
        raise NetworkSecurityException(e, sys)

@app.post("/predict") # predict route
async def predict_route(request: Request, file: UploadFile =File(...)):
    try:
        start_time = time.time()
        
        df = pd.read_csv(file.file)
        # Remove target column if it exists
        if 'Result' in df.columns:
            df = df.drop(columns=['Result'])
        preprocessor = load_object(file_path = "final_model/preprocessor.pkl") 
        model = load_object(file_path= "final_model/model.pkl")
        NSmodel = NetworkSecurityModel(preprocessing_object= preprocessor, trained_model_object= model)
        print(df.iloc[0])
        y_pred = NSmodel.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        df.to_csv("final_model/predicted.csv")
        
        # Update Prometheus metrics
        phishing_count = (y_pred == 1).sum()
        safe_count = (y_pred == 0).sum()
        
        prediction_counter.labels(result='phishing').inc(phishing_count)
        prediction_counter.labels(result='safe').inc(safe_count)
        phishing_detected.set(phishing_count)
        safe_sites.set(safe_count)
        
        # Record latency
        latency = time.time() - start_time
        prediction_latency.observe(latency)
        
        table_html = df.to_html(classes = 'table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
    
    except Exception as e:
        raise NetworkSecurityException(e, sys)
if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8080)
    