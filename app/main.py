from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.api.routes import router as api_router
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from dotenv import load_dotenv
import logging

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Analyzer", version="0.1.0")

# Registrar Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api_router, prefix="/api")
