from app.clients.ai_client import AIClient
from app.utils.file_reader import extract_text
from app.utils.text_preprocessor import preprocess_text
from fastapi import HTTPException, UploadFile
from app.schemas.dto import AnalyzeResponse

class EmailAnalyzerService:
  def __init__(self):
      self.ai_client = AIClient()


  async def analyze(
    self,
    text: str | None = None,
    file: UploadFile | None = None
  ) -> AnalyzeResponse:
        """
        Orquestra o pipeline:
        entrada -> extração -> pré-processamento -> IA(stub) -> response
        """

        if text and text.strip():
            content = text.strip()
        elif file:
            content = await extract_text(file)
        else:
            content = ""

        content = preprocess_text(content)

        if not content:
            raise HTTPException(
                status=400,
                detail="Conteúdo do email está vazio"
            )
        
        ai_result = self.ai_client.analyze(content)

        return AnalyzeResponse(
            category=ai_result["category"],
            suggested_reply=ai_result["suggested_reply"],
            confidence=ai_result["confidence"],
            extracted_chars=len(content),
            content=content
        )