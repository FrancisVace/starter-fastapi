import json
import time

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import FileResponse
import requests

from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    item_id: int


westend_name = "westend"
milton_name = "milton"
newstead_name = "newstead"

branch_ids = {
    westend_name: "D969F1B2-0C9F-49A9-B2AC-D7775642F298",
    milton_name: "690326F9-98CE-4249-BD91-53A0676A137B",
    newstead_name: "A3010228-DFC6-4317-86C0-3839FFDF3FD0"
}


class BranchInfo(BaseModel):
    name: str
    current_occupancy: float


class OccupancyData(BaseModel):
    occupancy: float
    time: str


live_branch_info = {
    westend_name: list(),
    milton_name: list(),
    newstead_name: list(),
}


def reset_data():
    global live_branch_info
    live_branch_info = {
        westend_name: list(),
        milton_name: list(),
        newstead_name: list(),
    }


logging = True


def set_logging(b):
    global logging
    logging = b


def poll_branch_data():
    if not logging:
        return
    get_branch_data()
    time.sleep(600)
    poll_branch_data()


def get_branch_data():
    for k, v in branch_ids.items():
        url = "https://portal.urbanclimb.com.au/uc-services/ajax/gym/occupancy.ashx?branch=" + v
        page = requests.get(url).text
        res = json.loads(page)
        time_str = res["LastUpdated"].split("T")[1][:5].replace(":", "")
        occupancy_data = OccupancyData(occupancy=res['CurrentPercentage'], time=time_str)
        print(occupancy_data)
        live_branch_info[k].append(occupancy_data)


@app.get("/")
async def root():
    return "Welcome to the Urban Climb data logger"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')


@app.get("/logging/start")
async def start_logging(background_tasks: BackgroundTasks):
    set_logging(True)
    background_tasks.add_task(poll_branch_data)
    return "Started Logging data"


@app.get("/logging/stop")
async def stop_logging():
    set_logging(False)
    reset_data()
    return "Stopped Logging data"


@app.get("/data")
async def get_data():
    return live_branch_info


@app.get("/item/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items/")
async def list_items():
    return [{"item_id": 1, "name": "Foo"}, {"item_id": 2, "name": "Bar"}]


@app.post("/items/")
async def create_item(item: Item):
    return item
