from fastapi import FastAPI

from app.routes.user_routes import router as user_router

app = FastAPI(title="device_systems API", version="1.0.0")
app.include_router(user_router)
