from fastapi import APIRouter, Form, File, UploadFile, HTTPException
import traceback
from app.schemas.dto import AnalyzeResponse
from app.services.analyzer_service import EmailAnalyzerService

router = APIRouter()
analyzer = EmailAnalyzerService()

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

  if file is not None and not getattr(file, "filename", None):
     file = None

  # Validar entrada: pelo menos texto válido ou arquivo
  text_valid = text and isinstance(text, str) and text.strip()
  
  if not text_valid and file is None:
     raise HTTPException(
        status_code=400,
        detail="Envie um texto ou um arquivo (em .pdf ou .txt) para a análise do email"
     )
  
  try:
     return await analyzer.analyze(text=text, file=file)
  
  except HTTPException:
     raise

  except Exception as e:
   traceback.print_exc()
   raise HTTPException(
        status_code=500,
        detail=f"Erro ao processar a mensagem do email: {str(e)}"
   )
