from app.clients.llm_client import OpenAILLMClient
from app.utils.file_reader import extract_text
from app.utils.text_preprocessor import preprocess_text
from fastapi import HTTPException, UploadFile
from app.schemas.dto import AnalyzeResponse
import logging

logger = logging.getLogger(__name__)

class EmailAnalyzerService:
  def __init__(self):
      self.ai_client = OpenAILLMClient()


  async def analyze(
    self,
    text: str | None = None,
    file: UploadFile | None = None
  ) -> AnalyzeResponse:
        """
        Orquestra o pipeline:
        entrada -> extração -> pré-processamento -> IA(stub) -> response
        """
        
        try:
            logger.info(f"Iniciando análise. text={bool(text)}, file={bool(file)}")
            
            if text and text.strip():
                content = text.strip()
                logger.info(f"Usando texto direto. Tamanho: {len(content)} chars")
            elif file:
                logger.info(f"Extraindo texto do arquivo: {file.filename}")
                content = await extract_text(file)
            else:
                content = ""
            
            logger.info(f"Conteúdo bruto extraído: {len(content)} chars")
            
            content = preprocess_text(content)
            logger.info(f"Conteúdo processado: {len(content)} chars")

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="Conteúdo do email está vazio"
                )
            
            logger.info("Enviando para análise de IA...")
            ai_result = self.ai_client.analyze(content)
            logger.info(f"IA respondeu: categoria={ai_result['category']}, confidence={ai_result['confidence']}")
            logger.debug(f"Reason (interno): {ai_result['reason']}")

            return AnalyzeResponse(
                category=ai_result["category"],
                suggested_reply=ai_result["suggested_reply"],
                confidence=ai_result["confidence"]
            )
            
        except HTTPException as exc:
            logger.warning(f"HTTPException lançada: {exc.status_code}")
            raise
        except Exception as e:
            logger.error(f"Erro durante análise: {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar: {str(e)}"
            )