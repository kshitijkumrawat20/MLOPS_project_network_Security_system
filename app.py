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

# Initialize cloud configuration
try:
    from cloud_config import initialize_monitoring, ENABLE_PREFECT
    cloud_status = initialize_monitoring()
    logging.info(f"Cloud MLOps initialized: {cloud_status}")
except Exception as e:
    logging.warning(f"Cloud config initialization failed: {e}")
    ENABLE_PREFECT = False
    cloud_status = {"prefect": False, "evidently": False}

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

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "status": "running",
        "service": "Network Security System - Phishing Detection",
        "cloud_mlops": {
            "prefect_cloud": "enabled" if cloud_status.get("prefect") else "disabled",
            "evidently": "cloud" if cloud_status.get("evidently") else "open-source",
            "monitoring": "enabled" if cloud_status.get("monitoring") else "disabled"
        },
        "endpoints": {
            "docs": "/docs",
            "train": "/train",
            "predict": "/predict"
        }
    }

@app.get("/train")
async def training_route():
    try: 
        logging.info("Starting training pipeline...")
        
        # Use Prefect Cloud if available
        if ENABLE_PREFECT:
            try:
                logging.info("Triggering training via Prefect Cloud...")
                from prefect_flows.training_flow import training_flow
                result = training_flow()
                return Response(f"Training triggered via Prefect Cloud! Check dashboard: https://app.prefect.cloud/")
            except Exception as prefect_error:
                logging.warning(f"Prefect training failed, falling back to direct: {prefect_error}")
        
        # Fallback: Direct training
        training_pipeline = Trainingpipeline()
        training_pipeline.run_pipeline()
        return Response("Training completed successfully (direct mode)")
    except Exception as e:
        raise NetworkSecurityException(e, sys)

@app.post("/predict") # predict route
async def predict_route(request: Request, file: UploadFile =File(...)):
    try:
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
        
        table_html = df.to_html(classes = 'table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
    
    except Exception as e:
        raise NetworkSecurityException(e, sys)
if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8080)
    