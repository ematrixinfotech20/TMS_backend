import os
from dotenv import load_dotenv

# Load environment variables based on APP_ENV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app_env = os.getenv("APP_ENV", "env")

if app_env == "production":
    if os.path.exists(os.path.join(BASE_DIR, ".env")):
        load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
elif app_env == "local":
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env.local"))
else:
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env.dev"))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import router as api_router
from core.response import success_response

app = FastAPI(title="Ticket Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Extract the first error message to be more user-friendly
    error_msg = exc.errors()[0].get("msg", "Validation error")
    
    # Try to make it slightly more contextual based on field
    if len(errors) > 0 and "loc" in errors[0] and len(errors[0]["loc"]) > 1:
        field_name = errors[0]["loc"][-1]
        if field_name != "body":
            error_msg = f"{field_name.capitalize()}: {error_msg}"
            
    return JSONResponse(
        status_code=400,
        content={"status": 400, "message": error_msg, "result": None}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "message": exc.detail, "result": None}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Internal Error: {exc}") # Log it for debugging
    return JSONResponse(
        status_code=500,
        content={"status": 500, "message": "An internal server error occurred", "result": None}
    )

app.include_router(api_router)

@app.get("/")
def read_root():
    return success_response(None, "TMS API is running. Check /docs.")

# .\venv\Scripts\activate
# uvicorn main:app --reload --host 0.0.0.0 --port 8000