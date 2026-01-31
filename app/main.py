from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Configurar FastAPI com metadata correta
app = FastAPI(
    title="Email Analyzer API",
    version="1.0.0",
    description="""
Sistema de análise e classificação automática de emails corporativos usando IA (OpenAI GPT).

## Funcionalidades

* **Análise de Emails**: Classifica emails em PRODUTIVO ou IMPRODUTIVO
* **Sugestão de Resposta**: Gera respostas automáticas contextualizadas
* **Múltiplos Formatos**: Suporta texto direto, arquivos .txt e .pdf

## Categorias

* **PRODUTIVO**: Emails que requerem ação ou resposta específica
* **IMPRODUTIVO**: Emails que não necessitam de uma ação imediata
    """,
    contact={
        "name": "André Mattos",
        "url": "https://github.com/andrejsmattos",
    },
    openapi_version="3.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    servers=[{"url": "http://emailanalyzer.site", "description": "Produção"}]
)

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
allow_origins=[
        "http://emailanalyzer.site",
        "http://52.3.3.229",
        "http://localhost",
        "http://localhost:8000"
    ],
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
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"Arquivo muito grande. Tamanho máximo permitido: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
                }
            )
    return await call_next(request)

# Registrar Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Incluir rotas da API
app.include_router(api_router, prefix="/api", tags=["API"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raiz da API
    
    Retorna informações básicas sobre a API e links úteis.
    """
    return {
        "message": "Email Analyzer API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)