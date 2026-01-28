from fastapi import APIRouter, Form, File, UploadFile, HTTPException

from app.schemas.dto import AnalyzeResponse
from app.services.analyzer_service import EmailAnalyzerService

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
   text: str | None = Form(default=None),
   file: UploadFile | None = File(default=None)
):
  """
  Analisa um email enviado como texto ou arquivo (.txt ou .pdf)
  """

  if (not text or not text.strip()) and file is None:
     raise HTTPException(
        status_code=400,
        detail="Envie um texto ou um arquivo (em .pdf ou .txt) para a análise do email"
     )
  
  try:
     analyzer = EmailAnalyzerService()
     result = await analyzer.analyze(text=text, file=file)
     return result
  except Exception:
     raise HTTPException(
        status_code=500,
        detail="Erro ao processar a mensagem do email"
     )
