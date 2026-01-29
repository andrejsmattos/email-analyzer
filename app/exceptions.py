"""
Handlers para exceções e erros da aplicação.
Centraliza toda a lógica de tratamento de erros.
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.dto import ErrorDetail, ValidationErrorDetail
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request, exc: HTTPException):
    """
    Handler para HTTPException com retornos padronizados
    """
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
    
    error_response = ErrorDetail(
        error=True,
        status_code=exc.status_code,
        detail=exc.detail,
        message=_get_error_message(exc.status_code)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Handler para erros de validação de requisição
    """
    logger.warning(f"Validation Error: {exc.errors()}")
    
    error_response = ValidationErrorDetail(
        error=True,
        status_code=422,
        detail="Validação de requisição falhou",
        message="Os dados enviados não são válidos. Verifique o formato.",
        errors=exc.errors()
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


async def general_exception_handler(request, exc: Exception):
    """
    Handler para exceções genéricas não tratadas
    """
    error_type = type(exc).__name__
    error_msg = str(exc)
    
    logger.error(
        f"Unhandled Exception [{error_type}]: {error_msg}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": error_type
        }
    )
    
    error_response = ErrorDetail(
        error=True,
        status_code=500,
        detail="Erro interno do servidor",
        message="Ocorreu um erro inesperado. Tente novamente mais tarde."
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


def _get_error_message(status_code: int) -> str:
    """
    Retorna mensagens amigáveis para cada código de status HTTP
    """
    messages = {
        400: "Requisição inválida. Verifique os parâmetros enviados.",
        401: "Autenticação necessária. Verifique suas credenciais.",
        403: "Acesso negado. Você não tem permissão para acessar este recurso.",
        404: "Recurso não encontrado.",
        422: "Validação falhou. Verifique o formato dos dados.",
        500: "Erro interno do servidor. Tente novamente mais tarde.",
        502: "Gateway indisponível. Tente novamente em alguns momentos.",
        503: "Serviço indisponível. Tente novamente em alguns momentos.",
    }
    return messages.get(status_code, "Ocorreu um erro. Tente novamente.")
