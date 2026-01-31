from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from dotenv import load_dotenv
import logging
import os

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar limite de upload (16MB por padrão)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 16 * 1024 * 1024))  # 16MB em bytes

app = FastAPI(
    title="Email Analyzer",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para validar tamanho do arquivo
@app.middleware("http")
async def limit_upload_size(request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_SIZE:
            return HTTPException(
                status_code=413,
                detail=f"Arquivo muito grande. Tamanho máximo permitido: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
            )
    return await call_next(request)

# Registrar Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api_router, prefix="/api")
