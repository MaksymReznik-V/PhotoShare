from fastapi import FastAPI

from routers.comments import router as comments_router
from routers.photos import router as pictures_router
from routers.ratings import router as rating_router
from routers.users import router as users_router

app = FastAPI(
    title="PhotoShare API",
    description="REST API for sharing and managing photos",
    version="1.0.0",
)

app.include_router(users_router)
app.include_router(pictures_router)
app.include_router(comments_router)
app.include_router(rating_router)
