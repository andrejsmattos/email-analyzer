"""
Testes unitários para extração de arquivo
"""

import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import UploadFile, HTTPException
from app.utils.file_reader import extract_text
import io


class TestExtractText:
    """Testes para a função extract_text"""

    # Valida se o conteúdo é extraído corretamente de um arquivo de texto simples
    @pytest.mark.asyncio
    async def test_extract_text_from_txt_file(self):
        """Testa extração de texto de arquivo .txt"""
        # Criar mock do arquivo
        file_content = b"Conteudo do email"
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "email.txt"
        mock_file.read.return_value = file_content

        result = await extract_text(mock_file)

        assert result == "Conteudo do email"
        mock_file.read.assert_called_once()

    # Verifica se espaços em branco nas extremidades do arquivo são removidos
    @pytest.mark.asyncio
    async def test_extract_text_from_txt_with_whitespace(self):
        """Testa extração com espaços em branco"""
        file_content = "   Texto com espaços   ".encode("utf-8")
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.read.return_value = file_content

        result = await extract_text(mock_file)

        assert result == "Texto com espaços"

    # Testa se erro é retornado quando arquivo .txt não contém conteúdo
    @pytest.mark.asyncio
    async def test_extract_text_from_empty_txt_file(self):
        """Testa erro ao extrair de arquivo .txt vazio"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "empty.txt"
        mock_file.read.return_value = b""

        with pytest.raises(HTTPException) as exc_info:
            await extract_text(mock_file)

        assert exc_info.value.status_code == 400
        assert "vazio" in exc_info.value.detail.lower()

    # Valida que erro é retornado quando arquivo contém apenas espaços em branco
    @pytest.mark.asyncio
    async def test_extract_text_from_whitespace_only_txt(self):
        """Testa erro ao extrair de arquivo contendo apenas espaços"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "whitespace.txt"
        mock_file.read.return_value = b"   \n\t  "

        with pytest.raises(HTTPException) as exc_info:
            await extract_text(mock_file)

        assert exc_info.value.status_code == 400

    # Verifica se caracteres acentuados em português são preservados durante extração
    @pytest.mark.asyncio
    async def test_extract_text_with_utf8_encoding(self):
        """Testa extração de texto com caracteres UTF-8"""
        text = "São Paulo, José, María, João"
        file_content = text.encode("utf-8")
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "utf8.txt"
        mock_file.read.return_value = file_content

        result = await extract_text(mock_file)

        assert result == text
        assert "São" in result
        assert "José" in result

    # Testa comportamento quando arquivo contém bytes inválidos em UTF-8 (usar ignore)
    @pytest.mark.asyncio
    async def test_extract_text_with_invalid_encoding(self):
        """Testa extração com encoding inválido (usa ignore)"""
        # Bytes inválidos em UTF-8
        file_content = b"Texto v\xE1lido com \xFF\xFE bytes inv\xE1lidos"
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "bad_encoding.txt"
        mock_file.read.return_value = file_content

        # Não deve lançar erro, mas ignorar bytes inválidos
        result = await extract_text(mock_file)
        assert isinstance(result, str)

    # Valida que erro é retornado para formatos de arquivo não suportados
    @pytest.mark.asyncio
    async def test_extract_text_from_invalid_format(self):
        """Testa erro ao tentar extrair de formato não suportado"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "image.jpg"
        mock_file.read.return_value = b"fake image data"

        with pytest.raises(HTTPException) as exc_info:
            await extract_text(mock_file)

        assert exc_info.value.status_code == 400
        assert "formato" in exc_info.value.detail.lower()

    # Testa se reconhecimento de extensão funciona independente de maiúsculas/minúsculas
    @pytest.mark.asyncio
    async def test_extract_text_case_insensitive_extension(self):
        """Testa reconhecimento de extensão case-insensitive"""
        file_content = b"Conteudo"
        
        for filename in ["test.TXT", "test.Txt", "test.txt"]:
            mock_file = AsyncMock(spec=UploadFile)
            mock_file.filename = filename
            mock_file.read.return_value = file_content

            result = await extract_text(mock_file)
            assert result == "Conteudo"

    # Valida extração de arquivo cujo nome contém espaços
    @pytest.mark.asyncio
    async def test_extract_text_with_spaces_in_filename(self):
        """Testa extração de arquivo com espaços no nome"""
        file_content = b"Conteudo"
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "meu email importante.txt"
        mock_file.read.return_value = file_content

        result = await extract_text(mock_file)
        assert result == "Conteudo"

    # Testa extração de arquivo com conteúdo muito longo (stress test)
    @pytest.mark.asyncio
    async def test_extract_text_long_content(self):
        """Testa extração de arquivo com conteúdo longo"""
        # Arquivo com 10000 caracteres
        long_text = "A" * 10000
        file_content = long_text.encode("utf-8")
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "large.txt"
        mock_file.read.return_value = file_content

        result = await extract_text(mock_file)
        assert len(result) == 10000
        assert result == long_text

    # Testa extração de arquivo PDF com mock da biblioteca PdfReader
    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_file(self):
        """Testa tentativa de extração de PDF (sucesso)"""
        # Nota: Este teste requer um PDF válido
        # Para este exemplo, vamos simular o comportamento
        from unittest.mock import patch

        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "document.pdf"
        mock_file.read.return_value = b"%PDF-1.4 fake pdf content"

        with patch("app.utils.file_reader.PdfReader") as mock_pdf:
            # Simular página extraída
            mock_page = Mock()
            mock_page.extract_text.return_value = "Texto extraído do PDF"
            mock_pdf.return_value.pages = [mock_page]

            result = await extract_text(mock_file)
            assert "Texto extraído do PDF" in result

    # Valida que erro é retornado quando arquivo PDF está vazio
    @pytest.mark.asyncio
    async def test_extract_text_from_empty_pdf(self):
        """Testa erro ao extrair de PDF vazio"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "empty.pdf"
        mock_file.read.return_value = b""

        with pytest.raises(HTTPException) as exc_info:
            await extract_text(mock_file)

        assert exc_info.value.status_code == 400
        assert "vazio" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_extract_text_filename_none(self):
        """Testa comportamento quando filename é None"""
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = None
        mock_file.read.return_value = b"content"

        with pytest.raises(HTTPException) as exc_info:
            await extract_text(mock_file)

        assert exc_info.value.status_code == 400
        assert "formato" in exc_info.value.detail.lower()
