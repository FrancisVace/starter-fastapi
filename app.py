import json

from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests

from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    item_id: int


branch_ids = {
    'westend': "D969F1B2-0C9F-49A9-B2AC-D7775642F298",
    'milton': "690326F9-98CE-4249-BD91-53A0676A137B",
    'newstead': "A3010228-DFC6-4317-86C0-3839FFDF3FD0"
}


class BranchInfo(BaseModel):
    name: str
    current_occupancy: float


@app.get("/")
async def root():
    branch_list = []
    for k, v in branch_ids.items():
        url = "https://portal.urbanclimb.com.au/uc-services/ajax/gym/occupancy.ashx?branch=" + v
        page = requests.get(url).text
        res = json.loads(page)
        branch_list.append(BranchInfo(name=k, current_occupancy=res['CurrentPercentage']))
    return branch_list


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')


@app.get("/item/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items/")
async def list_items():
    return [{"item_id": 1, "name": "Foo"}, {"item_id": 2, "name": "Bar"}]


@app.post("/items/")
async def create_item(item: Item):
    return item
