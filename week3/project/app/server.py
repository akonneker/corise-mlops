from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

from datetime import datetime, timedelta
import json

from classifier import NewsCategoryClassifier


class PredictRequest(BaseModel):
    source: str
    url: str
    title: str
    description: str


class PredictResponse(BaseModel):
    scores: dict
    label: str


MODEL_PATH = "../data/news_classifier.joblib"
LOGS_OUTPUT_PATH = "../data/logs.out"

app = FastAPI()
app.classifier = None
app.log_file = None


@app.on_event("startup")
def startup_event():
    """
    [TO BE IMPLEMENTED]
    1. Initialize an instance of `NewsCategoryClassifier`.
    2. Load the serialized trained model parameters (pointed to by `MODEL_PATH`) into the NewsCategoryClassifier you initialized.
    3. Open an output file to write logs, at the destimation specififed by `LOGS_OUTPUT_PATH`
        
    Access to the model instance and log file will be needed in /predict endpoint, make sure you
    store them as global variables
    """

    app.classifier = NewsCategoryClassifier()
    app.classifier.load(MODEL_PATH)
    app.log_file = open(LOGS_OUTPUT_PATH, 'w')

    logger.info("Setup completed")


@app.on_event("shutdown")
def shutdown_event():
    # clean up
    """
    [TO BE IMPLEMENTED]
    1. Make sure to flush the log file and close any file pointers to avoid corruption
    2. Any other cleanups
    """

    app.log_file.flush()
    app.log_file.close()

    logger.info("Shutting down application")


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    # get model prediction for the input request
    # construct the data to be logged
    # construct response
    """
    [TO BE IMPLEMENTED]
    1. run model inference and get model predictions for model inputs specified in `request`
    2. Log the following data to the log file (the data should be logged to the file that was opened in `startup_event`)
    {
        'timestamp': <YYYY:MM:DD HH:MM:SS> format, when the request was received,
        'request': dictionary representation of the input request,
        'prediction': dictionary representation of the response,
        'latency': time it took to serve the request, in millisec
    }
    3. Construct an instance of `PredictResponse` and return
    """

    start_time = datetime.now()

    log_dict = {}
    log_dict['timestamp'] = start_time.strftime("%Y:%m:%d %H:%M:%S")
    log_dict['request'] = {'source': request.source, 'url' : request.url, 'title' : request.title, 'description': request.description}
    

    pred_scores = app.classifier.predict_proba(log_dict['request'])
    pred_label = app.classifier.predict_label(log_dict['request'])

    log_dict['prediction'] = {'scores': pred_scores, 'label': pred_label}
    stop_time = datetime.now()

    
    log_dict['latency'] = (stop_time - start_time) / timedelta(milliseconds=1)
   

    #print(log_dict)
    app.log_file.write(json.dumps(log_dict))
    app.log_file.flush()

    response = PredictResponse(scores=pred_scores, label=pred_label)
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}
