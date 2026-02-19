from fastapi import FastAPI, status

from car_api.routers import brands, cars, users

app = FastAPI()

app.include_router(
    router=brands.router,
    prefix="/api/v1",
    tags=["brands"]
)


app.include_router(
    router=cars.router,
    prefix="/api/v1",
    tags=["cars"]
)

app.include_router(
    router=users.router,
    prefix="/api/v1",
    tags=["users"]
)


@app.get("/health-check", status_code=200)
def read_root():
    return {"status": "healthy"}