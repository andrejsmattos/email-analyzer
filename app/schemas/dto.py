from pydantic import BaseModel, Field
from typing import Optional, List
from app.domain.email_category import EmailCategory

class AnalyzeResponse(BaseModel):
  """Resposta de análise de email"""
  category: EmailCategory = Field(
    ...,
    description="Categoria do email: PRODUTIVO ou IMPRODUTIVO",
    example="PRODUTIVO"
  )
  suggested_reply: str = Field(
    ...,
    description="Resposta sugerida automaticamente",
    example="Olá! Recebemos sua mensagem e iremos analisar sua solicitação em breve."
  )
  confidence: Optional[float] = Field(
    default=None,
    description="Confiança da classificação (0.0 a 1.0)",
    ge=0.0,
    le=1.0,
    example=0.95
  )

  class Config:
    json_schema_extra = {
      "example": {
        "category": "PRODUTIVO",
        "suggested_reply": "Olá! Recebemos sua mensagem e iremos analisar sua solicitação em breve. Se possível, envie mais detalhes.",
        "confidence": 0.92
      }
    }

class ErrorDetail(BaseModel):
  """Detalhe de erro"""
  error: bool = Field(..., description="Indicador de erro")
  status_code: int = Field(..., description="Código HTTP de status")
  detail: str = Field(..., description="Descrição técnica do erro")
  message: str = Field(..., description="Mensagem amigável para o usuário")

class ValidationErrorDetail(BaseModel):
  """Detalhe de erro de validação"""
  error: bool = Field(..., description="Indicador de erro")
  status_code: int = Field(default=422, description="Código HTTP")
  detail: str = Field(..., description="Descrição técnica")
  message: str = Field(..., description="Mensagem amigável")
  errors: Optional[List[dict]] = Field(
    default=None,
    description="Lista de erros de validação"
  )