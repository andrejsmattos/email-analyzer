"""
Testes unitários para o serviço de análise de email (com mocks)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from app.services.analyzer_service import EmailAnalyzerService
from app.schemas.dto import AnalyzeResponse


class TestEmailAnalyzerService:
    """Testes para a classe EmailAnalyzerService"""

    @pytest.fixture
    def service(self):
        """Fixture que cria uma instância do serviço com mock do cliente LLM"""
        service = EmailAnalyzerService()
        service.ai_client = Mock()
        return service

    # Valida se a análise processa texto corretamente e retorna resposta estruturada
    @pytest.mark.asyncio
    async def test_analyze_with_text_success(self, service):
        """Testa análise bem-sucedida com texto"""
        service.ai_client.analyze.return_value = {
            "category": "PRODUTIVO",
            "suggested_reply": "Entendido, vou processar",
            "confidence": 0.95,
            "reason": "Email com demanda clara"
        }

        result = await service.analyze(text="Preciso de suporte urgente")

        assert isinstance(result, AnalyzeResponse)
        assert result.category == "PRODUTIVO"
        assert result.suggested_reply == "Entendido, vou processar"
        assert abs(result.confidence - 0.95) < 1e-9
        service.ai_client.analyze.assert_called_once()

    # Testa que texto vazio ou apenas espaços retorna erro apropriado
    @pytest.mark.asyncio
    async def test_analyze_with_empty_text_returns_error(self, service):
        """Testa que texto vazio retorna erro"""
        with pytest.raises(HTTPException) as exc_info:
            await service.analyze(text="   ")
        
        assert exc_info.value.status_code == 400
        assert "vazio" in exc_info.value.detail.lower()

    # Valida que error é retornado quando nenhum texto ou arquivo é fornecido
    @pytest.mark.asyncio
    async def test_analyze_with_none_text_and_none_file_returns_error(self, service):
        """Testa erro quando texto e arquivo são None"""
        with pytest.raises(HTTPException) as exc_info:
            await service.analyze(text=None, file=None)
        
        assert exc_info.value.status_code == 400

    # Testa análise bem-sucedida quando arquivo é fornecido ao invés de texto
    @pytest.mark.asyncio
    async def test_analyze_with_file_success(self, service):
        """Testa análise bem-sucedida com arquivo"""
        # Setup do mock
        service.ai_client.analyze.return_value = {
            "category": "IMPRODUTIVO",
            "suggested_reply": "Obrigado pela informação",
            "confidence": 0.87,
            "reason": "Email informativo"
        }

        mock_file = AsyncMock()
        mock_file.filename = "email.txt"
        
        with patch("app.services.analyzer_service.extract_text", 
                   return_value="Conteúdo extraído do arquivo"):
            result = await service.analyze(text=None, file=mock_file)

        assert isinstance(result, AnalyzeResponse)
        assert result.category == "IMPRODUTIVO"
        assert result.suggested_reply == "Obrigado pela informação"

    # Valida se a classificação IMPRODUTIVO é retornada corretamente
    @pytest.mark.asyncio
    async def test_analyze_improdutivo_category(self, service):
        """Testa classificação IMPRODUTIVO"""
        service.ai_client.analyze.return_value = {
            "category": "IMPRODUTIVO",
            "suggested_reply": "Obrigado",
            "confidence": 0.92,
            "reason": "Agradecimento"
        }

        result = await service.analyze(text="Muito obrigado pela atenção")

        assert result.category == "IMPRODUTIVO"

    # Verifica se o texto é preprocessado antes de ser enviado para análise de IA
    @pytest.mark.asyncio
    async def test_analyze_preprocesses_text(self, service):
        """Testa que o texto é pré-processado antes de enviar ao LLM"""
        service.ai_client.analyze.return_value = {
            "category": "PRODUTIVO",
            "suggested_reply": "OK",
            "confidence": 0.9,
            "reason": "Test"
        }

        with patch("app.services.analyzer_service.preprocess_text", 
                   return_value="texto processado"):
            await service.analyze(text="Texto, com! pontuação?")

        service.ai_client.analyze.assert_called_once()
        called_text = service.ai_client.analyze.call_args[0][0]
        assert called_text == "texto processado"

    # Testa se tratamento de exceção funciona quando cliente LLM falha
    @pytest.mark.asyncio
    async def test_analyze_handles_ai_error(self, service):
        """Testa tratamento de erro do cliente LLM"""
        service.ai_client.analyze.side_effect = Exception("API Error")

        with pytest.raises(HTTPException) as exc_info:
            await service.analyze(text="Algum texto")

        assert exc_info.value.status_code == 500
        assert "erro" in exc_info.value.detail.lower()

    # Valida se o valor de confiança retornado está sempre no intervalo [0, 1]
    @pytest.mark.asyncio
    async def test_analyze_with_valid_confidence_range(self, service):
        """Testa que confidence está no intervalo [0, 1]"""
        for confidence in [0.0, 0.5, 0.99, 1.0]:
            service.ai_client.analyze.return_value = {
                "category": "PRODUTIVO",
                "suggested_reply": "OK",
                "confidence": confidence,
                "reason": "Test"
            }

            result = await service.analyze(text="Teste")
            assert 0.0 <= result.confidence <= 1.0

    # Testa que análise rejeita entrada contendo apenas espaços e quebras de linha
    @pytest.mark.asyncio
    async def test_analyze_with_whitespace_text(self, service):
        """Testa análise com texto contendo apenas espaços"""
        with pytest.raises(HTTPException) as exc_info:
            await service.analyze(text="\n\n   \t  ")

        assert exc_info.value.status_code == 400

    # Valida se texto com múltiplas linhas é processado corretamente
    @pytest.mark.asyncio
    async def test_analyze_processes_multiline_text(self, service):
        """Testa processamento de texto multilinhas"""
        service.ai_client.analyze.return_value = {
            "category": "PRODUTIVO",
            "suggested_reply": "Processado",
            "confidence": 0.88,
            "reason": "Test"
        }

        multiline_text = """Primeira linha
        Segunda linha
        Terceira linha"""

        result = await service.analyze(text=multiline_text)
        assert result.category == "PRODUTIVO"
