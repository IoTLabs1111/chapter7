from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status
)
from fastapi.responses import Response
from typing import List
from bson import ObjectId
from pymongo import ReturnDocument
import cloudinary
from cloudinary import uploader  # noqa: F401

from models import CarModel, UpdateCarModel, CarCollectionPagination
from auth import auth_handler
from config import base_config

# Cloudinary configuration
cloudinary.config(
    cloud_name=base_config.CLOUDINARY_CLOUD_NAME,
    api_key=base_config.CLOUDINARY_API_KEY,
    api_secret=base_config.CLOUDINARY_API_SECRET,
)

router = APIRouter()
CARS_PER_PAGE = 10


@router.post(
    "/",
    response_description="Add new car with picture",
    response_model=CarModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_car_with_picture(
    request: Request,
    brand: str = Form(...),
    make: str = Form(...),
    year: int = Form(...),
    cm3: int = Form(...),
    km: int = Form(...),
    price: int = Form(...),
    picture: UploadFile = File(...),
    user: str = Depends(auth_handler.auth_wrapper),
):
    cloudinary_image = cloudinary.uploader.upload(
        picture.file, folder="FARM2", crop="fill", width=800
    )
    picture_url = cloudinary_image["url"]

    car = CarModel(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user_id=user["user_id"],
    )

    cars = request.app.db["cars"]
    document = car.model_dump(by_alias=True, exclude=["id"])
    inserted = await cars.insert_one(document)
    return await cars.find_one({"_id": inserted.inserted_id})


@router.get(
    "/",
    response_description="List all cars, paginated",
    response_model=CarCollectionPagination,
    response_model_by_alias=False,
)
async def list_cars(
    request: Request,
    page: int = 1,
    limit: int = CARS_PER_PAGE,
):
    cars = request.app.db["cars"]
    skip = (page - 1) * limit
    results = []

    cursor = cars.find().skip(skip).limit(limit)
    async for car in cursor:
        results.append(car)

    has_more = await cars.count_documents({}) > page * limit

    return CarCollectionPagination(
        cars=results,
        page=page,
        has_more=has_more
    )


@router.get(
    "/{id}",
    response_description="Get a single car by ID",
    response_model=CarModel,
    response_model_by_alias=False,
)
async def show_car(id: str, request: Request):
    cars = request.app.db["cars"]
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")

    if (car := await cars.find_one({"_id": obj_id})) is not None:
        return car

    raise HTTPException(status_code=404, detail=f"Car with {id} not found")


@router.put("/cars/{id}")
async def update_car(
    id: str,
    request: Request,
    user=Depends(auth_handler.auth_wrapper),
    car: UpdateCarModel = Body(...),
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")

    update_data = {
        k: v
        for k, v in car.model_dump(by_alias=True).items()
        if v is not None and k != "_id"
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    result = await request.app.db["cars"].update_one({"_id": obj_id}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")

    updated_car = await request.app.db["cars"].find_one({"_id": obj_id})
    return updated_car


@router.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: str, request: Request):
    try:
        obj_id = ObjectId(car_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Car {car_id} not found")

    delete_result = await request.app.db["cars"].delete_one({"_id": obj_id})
    if delete_result.deleted_count == 1:
        return

    raise HTTPException(status_code=404, detail=f"Car with ID {car_id} not found")
