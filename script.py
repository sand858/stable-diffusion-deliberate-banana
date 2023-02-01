import json
import requests
import subprocess
from fastapi import FastAPI, Request, Body
from fastapi.testclient import TestClient
from modules.script_callbacks import on_app_started

client = None

def healthcheck():
    gpu = False
    out = subprocess.run("nvidia-smi", shell=True)
    if out.returncode == 0: # success state on shell command
        gpu = True
    return {"state": "healthy", "gpu": gpu}

async def inference(request: Request):
    global client
    body = await request.body()
    model_input = json.loads(body)
    params = None
    if 'endpoint' in model_input:
        endpoint = model_input['endpoint']
        if 'params' in model_input:
            params = model_input['params']
    else:
        endpoint = 'txt2img'
        params = model_input

    if params is not None:
        response = client.post('/sdapi/v1/' + endpoint, json = params)
    else:
        response = client.get('/sdapi/v1/' + endpoint)

    output = response.json()
    return output

def register_endpoints(block, app):
    global client
    app.add_api_route('/healthcheck', healthcheck, methods=['GET'])
    app.add_api_route('/', inference, methods=['POST'])
    client = TestClient(app)

on_app_started(register_endpoints)
