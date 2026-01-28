from app.utils.file_reader import extract_text
from app.utils.text_preprocessor import preprocess_text
from fastapi import UploadFile
from app.schemas.dto import AnalyzeResponse

class EmailAnalyzerService:
  async def analyze(
    self,
    text: str | None = None,
    file: UploadFile | None = None
  ) -> AnalyzeResponse:
        """
        Service stub.
        Apenas simula o comportamento para destravar o endpoint.
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
                detail="Conteúdo do email está vazio após o pré-processamento"
            )

        return AnalyzeResponse(
            category="IMPRODUTIVO",
            suggested_reply=(
                "Olá! Obrigado pelo contato. "
                "Esta é uma resposta automática inicial."
            ),
            confidence=0.50,
            extracted_chars=len(content),
            content=content
        )