# ==============================================================================
# File: car_api/app.py
# Description: Entry point app file.
# ==============================================================================

from fastapi import FastAPI

from car_api.routers import auth, brands, cars, users
from car_api.routers.admin import brands as admin_brands
from car_api.routers.admin import cars as admin_cars
from car_api.routers.admin import users as admin_users

app = FastAPI()

prefix = '/api/v1'

# ==============================================================================
# Public & authenticated routes
# ==============================================================================

app.include_router(
    router=auth.router,
    prefix=prefix,
)

app.include_router(
    router=users.router,
    prefix=prefix,
)

app.include_router(
    router=brands.router,
    prefix=prefix,
)

app.include_router(
    router=cars.router,
    prefix=prefix,
)


# ==============================================================================
# Administrative routes
# ==============================================================================

app.include_router(
    router=admin_users.router,
    prefix=prefix,
)

app.include_router(
    router=admin_brands.router,
    prefix=prefix,
)

app.include_router(router=admin_cars.router, prefix=prefix)


# ==============================================================================
# Health check
# ==============================================================================


@app.get('/health-check', status_code=200)
def read_root():
    return {'status': 'healthy'}
