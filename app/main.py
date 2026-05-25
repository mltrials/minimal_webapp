from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    BackgroundTasks,
    Query,
    Path,
    Body,
)
from datetime import datetime
import platform
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="Minimal FastAPI App", version="1.0.0")


# -----------------------------
# Dependency (reusable config)
# -----------------------------
def get_app_mode():
    return {"mode": "development"}


# -----------------------------
# Middleware (CORS)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Pydantic models (request/response validation)
# -----------------------------
class Item(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    tags: Optional[List[str]] = []


# -----------------------------
# Dependency (reusable logic)
# -----------------------------
def common_params(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
):
    return {"q": q, "limit": limit}


# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
def root(
    user: str = Query(None, description="Optional username"),
    debug: bool = Query(False),
    mode: dict = Depends(get_app_mode),
):
    response = {
        "message": "Hello FastAPI 🚀",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
        },
        "app_mode": mode["mode"],
    }

    if user:
        response["greeting"] = f"Welcome, {user}!"

    if debug:
        response["debug_info"] = {
            "active_endpoints": ["/", "/items", "/log"],
            "status": "debug mode enabled",
        }

    return response


# -----------------------------
# Path parameter example
# -----------------------------
@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(..., ge=1, description="Item ID must be >= 1")
):
    if item_id == 999:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}


# -----------------------------
# Query + dependency example
# -----------------------------
@app.get("/items/")
def list_items(params: dict = Depends(common_params)):
    return {
        "message": "List of items",
        "params": params,
    }


# -----------------------------
# Request body (POST)
# -----------------------------
@app.post("/items/")
def create_item(item: Item):
    return {
        "message": "Item created",
        "item": item,
    }


# -----------------------------
# Mixed path + body + validation
# -----------------------------
@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    item: Item = Body(...),
):
    return {
        "message": "Item updated",
        "item_id": item_id,
        "item": item,
    }


# -----------------------------
# Background task example
# -----------------------------
def fake_logger(message: str):
    with open("app.log", "a") as f:
        f.write(message + "\n")


@app.post("/log/")
def log_message(
    message: str,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(fake_logger, message)
    return {"status": "logging scheduled"}


# -----------------------------
# Simple error handling demo
# -----------------------------
@app.get("/error-demo/")
def error_demo(flag: bool = False):
    if flag:
        raise HTTPException(status_code=400, detail="Bad request triggered")
    return {"status": "ok"}