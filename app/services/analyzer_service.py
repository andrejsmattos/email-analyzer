from app.services.classification_service import EmailClassificationService
from app.domain.email_category import EmailCategory
from app.utils.file_reader import extract_text
from app.utils.text_preprocessor import preprocess_text
from fastapi import HTTPException, UploadFile
from app.schemas.dto import AnalyzeResponse

class EmailAnalyzerService:
  def __init__(self):
      self.classifier = EmailClassificationService()

  async def analyze(
    self,
    text: str | None = None,
    file: UploadFile | None = None
  ) -> AnalyzeResponse:
        """
        Service stub.
        Apenas simula o comportamento do MVP para destravar o endpoint.
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
        
        category = self.classifier.classify(content)

        return AnalyzeResponse(
            category=category,
            suggested_reply=self.suggest_reply(category),
            confidence=0.70,
            extracted_chars=len(content),
            content=content
        )
  
  def suggest_reply(self, category: EmailCategory) -> str:
      if category == EmailCategory.PRODUTIVO:
        return (
          "Olá! Recebemos sua mensagem e "
          "iremos analisar sua solicitação em breve."
        )

      return (
        "Olá! Obrigado pelo contato. "
        "Esta é uma mensagem informativa automática."
      )