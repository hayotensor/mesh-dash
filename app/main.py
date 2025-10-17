import asyncio
import datetime
import json
import os
import random

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from substrate.chain_functions import Hypertensor
import requests
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

api_keys = json.loads(os.getenv('API_KEYS'))

print("api_keys", api_keys)

# Mount static files (for JS, CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

SUBNET_ID = 1

hypertensor = Hypertensor("ws://127.0.0.1:9944")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/nodes")
async def get_nodes():
    # Generate 12 nodes with random positions
    nodes = []
    for i in range(12):
        nodes.append({
            "id": f"node{i+1}",
            "x": random.uniform(-5, 5),
            "y": random.uniform(-5, 5),
            "z": random.uniform(-5, 5),
        })
    return {"nodes": nodes}

@app.websocket("/api/heartbeat")
async def heartbeat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = [
            {"peer": "123D", "status": "ONLINE", "expiration": datetime.datetime.utcnow().isoformat()},
            {"peer": "Q1rmase", "status": "ONLINE", "expiration": datetime.datetime.utcnow().isoformat()},
        ]
        await websocket.send_json(data)
        await asyncio.sleep(2)


"""
Note all of the API calls must be cached into a database to avoid constant calls to the API on user reloads
"""
@app.websocket("/api/heartbeat_v2/{subnet_id}")
async def heartbeat_v2(websocket: WebSocket, subnet_id: int):
    print("heartbeat_v2")
    await websocket.accept()
    while True:
        api_key = api_keys[str(subnet_id)]["key"]
        url = api_keys[str(subnet_id)]["url"]
        endpoint = "/get_heartbeat"

        print("api_key", api_key)
        print("url", url)

        response = requests.get(
            url + endpoint,
            headers={"X-API-Key": api_key}
        )

        results = response.json()

        data = []

        # TODO
        # Before appending data, check if data is fresh
        for item in results['value']:
            peer_id = item["peer_id"]
            state = item["server"]["state"]
            expiration_time = item["expiration_time"]
            data.append({
                "peer_id": peer_id,
                "state": state,
                "expiration_time": expiration_time,
            })
        await websocket.send_json(data)
        await asyncio.sleep(30)

@app.websocket("/api/subnet_node_infos/{subnet_id}")
async def get_subnet_node_infos(websocket: WebSocket, subnet_id: int):
    await websocket.accept()
    while True:
        subnet_nodes = hypertensor.get_subnet_nodes_info_formatted(subnet_id)
        print("get_subnet_node_infos subnet_nodes", subnet_nodes)
        data = []
        for node in subnet_nodes:
            peer_id = node.peer_id
            coldkey = node.coldkey
            hotkey = node.hotkey

            # identity
            identity = node.identity
            name = identity['name']
            if not name:
                name = "None"
            x = identity['x']
            if not x:
                x = "None"

            # reputation
            reputation = node.reputation
            rep_score = float(reputation['score']) / float(1e18)
            average_attestation = float(reputation['average_attestation']) / float(1e18)
            if average_attestation == 0.0:
                average_attestation = "None"

            data.append({
                "peer_id": peer_id,
                "coldkey": coldkey,
                "hotkey": hotkey,
                "name": name,
                "x": x,
                "rep_score": rep_score,
                "average_attestation": average_attestation,
            })
        await websocket.send_json(data)
        await asyncio.sleep(30)

@app.websocket("/api/get_peers_info/{subnet_id}")
async def get_peers_info(websocket: WebSocket, subnet_id: int):
    await websocket.accept()
    while True:
        api_key = api_keys[str(subnet_id)]["key"]
        url = api_keys[str(subnet_id)]["url"]
        endpoint = "/get_peers_info"

        response = requests.get(
            url + endpoint,
            headers={"X-API-Key": api_key}
        )

        results = response.json()

        data = []

        # for peer_id, peer_info in results["value"].items():
        #     location = peer_info.get('location', {})
            
        #     # Check if location query was successful
        #     if location.get('status') == 'success':
        #         lat = location.get('lat')
        #         lon = location.get('lon')
                
        #         if lat is not None and lon is not None:
        #             data.append({
        #                 "name": peer_id,
        #                 "lat": float(lat),
        #                 "lon": float(lon),
        #             })
        #         else:
        #             data.append({
        #                 "name": peer_id,
        #                 "lat": 34.0549,
        #                 "lon": -118.2426,
        #             })
        #     else:
        #         data.append({
        #             "name": "Unknown",
        #             "lat": 34.0549,
        #             "lon": -118.2426,
        #         })

        data = [
            {
                "name": "peer_1",
                "lat": 0.07 * 180,
                "lon": 0.07 * 360,
                "elevation": 10000
            },
            {
                "name": "peer_2",
                "lat": -0.01 * 180,
                "lon": -0.01 * 360,
                "elevation": 10000
            },
            {
                "name": "peer_3",
                "lat": 0.91 * 180,
                "lon": -0.097 * 360,
                "elevation": 10000
            },
            {
                "name": "peer_4",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
            {
                "name": "peer_5",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
            {
                "name": "peer_6",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
            {
                "name": "peer_7",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
            {
                "name": "peer_8",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
            {
                "name": "peer_9",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
            {
                "name": "peer_10",
                "lat": 34.0549,
                "lon": -118.2426,
                "elevation": 10000
            },
        ]
        await websocket.send_json(data)
        await asyncio.sleep(30)
