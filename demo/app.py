import datetime
from urllib.parse import parse_qs

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
import uvicorn

from monquery import (
    pymongo_find,
    FilterSimple,
    Sorting,
    SortingOption,
    PaginationBasic,
    ParamEq,
    parse_string,
    ParamMax,
    ParamMin,
    parse_datetime_iso,
)

app = Starlette(debug=True)

fltr = FilterSimple(
    [
        ParamEq("title", parse_string),
        ParamMax("time[max]", parse_datetime_iso, "created_at", lte=True),
        ParamMin("time[min]", parse_datetime_iso, "created_at", gte=True),
    ]
)
sorting = Sorting(
    [
        SortingOption("title", field="title", direction=pymongo.ASCENDING),
        SortingOption("-title", field="title", direction=pymongo.DESCENDING),
        SortingOption(
            "creation-time", field="created_at", direction=pymongo.DESCENDING
        ),
        SortingOption(
            "-creation-time", field="created_at", direction=pymongo.DESCENDING
        ),
    ],
)
pg = PaginationBasic()


client = AsyncIOMotorClient()
todos_collection = client["monquery-sample-app"]["todos"]


def item_to_json(item):
    return {
        "title": item["title"],
        "description": item["description"],
        "created_at": item["created_at"].isoformat(),
    }


@app.route("/todos/", methods=["GET"])
async def todos(request: Request):
    cursor, err = pymongo_find(
        todos_collection,
        fltr,
        sorting,
        pg,
        parse_qs(request.url.query),
    )
    if err:
        return JSONResponse({"error": err}, status_code=400)
    return JSONResponse([item_to_json(item) async for item in cursor])


@app.route("/todos/", methods=["POST"])
async def create_todo(request: Request):
    post = await request.json()
    ins = await todos_collection.insert_one(
        {
            "title": post["title"],
            "description": post["description"],
            "created_at": datetime.datetime.utcnow(),
        }
    )
    return JSONResponse(
        item_to_json(await todos_collection.find_one({"_id": ins.inserted_id}))
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
