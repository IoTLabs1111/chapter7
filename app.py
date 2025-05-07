from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from motor import motor_asyncio
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from collections import defaultdict
from routers.users import router as users_router
from config import BaseConfig
from routers.cars import router as cars_router
from routers.users import router as users_router  # <-- ✅ Add this line

settings = BaseConfig()

async def lifespan(app: FastAPI):
    app.client = motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    app.db = app.client[settings.DB_NAME]
    try:
        await app.client.admin.command("ping")
        print("Pinged your deployment. You have successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    yield
    app.client.close()

app = FastAPI(lifespan=lifespan)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cars_router, prefix="/cars", tags=["cars"])
app.include_router(users_router, prefix="/users", tags=["users"])  # <-- ✅ Plug users router here

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation Error: {exc}")
    formatted_errors = defaultdict(list)
    for error in exc.errors():
        formatted_errors[error["loc"][0]].append(error["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": formatted_errors}),
    )

# Debug: Show all routes on startup
for route in app.routes:
    print(f"Path: {route.path}, Methods: {route.methods}")

@app.get("/")
async def get_root():
    return {"Message": "Hello Suchart now you web Root working!"}

@app.post("/add-test-car")
async def add_test_car():
    test_car = {
        "brand": "Toyota",
        "make": "Corolla",
        "year": 2020,
        "cm3": 1800,
        "km": 50000,
        "price": 15000,
        "user_id": "dummy-user-id"
    }
    result = await app.db.car_collection.insert_one(test_car)
    return {"status": "success", "message": "Car added", "car_id": str(result.inserted_id)}
