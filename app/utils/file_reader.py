from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import io

async def extract_text(file: UploadFile) -> str:
  """
  Extrai texto de UploadFile (.txt ou .pdf).
  Retorna string com conteúdo.
  Lança HTTPException(400) para formato inválido ou arquivo vazio.
  """

  filename = (file.filename or "").lower().strip()

  if filename.endswith(".txt"):
    data = await file.read()
    text = data.decode("utf-8", errors="ignore").strip()
    if not text:
      raise HTTPException(status_code=400, detail="Arquivo .txt vazio")
    return text
  
  if filename.endswith(".pdf"):
    data = await file.read()
    if not data:
      raise HTTPException(
        status_code=400,
        detail="Arquivo .pdf vazio"
        )
    
    try:
      reader = PdfReader(io.BytesIO(data))
      pages_text = []
      for page in reader.pages:
        pages_text.append(page.extract_text() or "")
      text = "\n".join(pages_text).strip()
    except Exception as e:
      raise HTTPException(
        status_code=400,
        detail=f"Falha ao ler o PDF: {str(e)}"
        )
    
    if not text:
      raise HTTPException(
        status_code=400,
        detail="Não foi possível extrair o texto do PDF (pode ser imagem/scaneado)"
      )
    return text
  
  raise HTTPException(
    status_code=400,
    detail="Formato inválido. Envie no formato .txt ou .pdf"
  )