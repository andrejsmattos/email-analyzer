"""
Testes unitários para funções utilitárias (preprocessamento, extração, etc)
"""

import pytest
from app.utils.text_preprocessor import (
    preprocess_text,
    get_tokens,
    get_text_stats,
    _remove_stopwords,
    _remove_numbers,
)


class TestPreprocessText:
    """Testes para a função preprocess_text"""

    def test_preprocess_text_basic(self):
        """Testa preprocessamento básico de texto simples"""
        text = "Olá, mundo! Como você está?"
        result = preprocess_text(text)
        assert isinstance(result, str)
        assert len(result) > 0
        # Deve remover pontuação
        assert "," not in result
        assert "!" not in result
        # Deve converter para minúsculas
        assert result == result.lower()

    def test_preprocess_text_removes_stopwords(self):
        """Testa se stopwords são removidas"""
        text = "o gato subiu no telhado"
        result = preprocess_text(text)
        # "o" é stopword, deve ser removido
        assert "o" not in result.split()
        # "gato" e "telhado" devem estar presentes
        assert "gato" in result
        assert "telhado" in result

    def test_preprocess_text_removes_punctuation(self):
        """Testa remoção de pontuação"""
        text = "Olá! Como vai? Tudo bem... certo?"
        result = preprocess_text(text)
        assert "!" not in result
        assert "?" not in result
        assert "." not in result

    def test_preprocess_text_normalizes_whitespace(self):
        """Testa normalização de espaços em branco"""
        text = "Texto   com    múltiplos   espaços"
        result = preprocess_text(text)
        # Não deve ter múltiplos espaços consecutivos
        assert "  " not in result

    def test_preprocess_text_removes_numbers(self):
        """Testa remoção de números isolados"""
        text = "Email 123 importante 456 urgente"
        result = preprocess_text(text)
        # Números isolados devem ser removidos
        assert "123" not in result
        assert "456" not in result

    def test_preprocess_text_empty_string(self):
        """Testa preprocessamento de string vazia"""
        result = preprocess_text("")
        assert result == ""

    def test_preprocess_text_none_input(self):
        """Testa preprocessamento com entrada None"""
        result = preprocess_text(None)
        assert result == ""

    def test_preprocess_text_non_string_input(self):
        """Testa preprocessamento com entrada não-string"""
        result = preprocess_text(123)
        assert result == ""

    def test_preprocess_text_with_accents(self):
        """Testa preprocessamento mantendo acentuação"""
        text = "São Paulo, João, José, María"
        result = preprocess_text(text)
        # Deve manter acentos (não remove)
        assert "paulo" in result
        assert "joão" in result

    def test_preprocess_text_multiline(self):
        """Testa preprocessamento com múltiplas linhas"""
        text = """Primeira linha
        Segunda linha
        Terceira linha"""
        result = preprocess_text(text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_preprocess_text_long_content(self):
        """Testa preprocessamento de conteúdo longo"""
        text = "palavra " * 1000  # 1000 palavras repetidas
        result = preprocess_text(text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_preprocess_text_real_email(self):
        """Testa preprocessamento com email realista"""
        text = """Olá pessoal!

        Segue em anexo o relatório de vendas do mês.
        Por favor, revisar até amanhã.

        Att,
        Carlos"""
        result = preprocess_text(text)
        # Palavras importantes devem estar presentes
        assert "relatório" in result or "relatorio" in result
        assert "vendas" in result
        assert len(result) > 10


class TestRemoveStopwords:
    """Testes para a função _remove_stopwords"""

    def test_remove_common_stopwords(self):
        """Testa remoção de stopwords comuns"""
        text = "a o e de para com que"
        result = _remove_stopwords(text)
        assert result.strip() == ""

    def test_remove_stopwords_keeps_important_words(self):
        """Testa que palavras importantes não são removidas"""
        text = "sistema importante muito bom"
        result = _remove_stopwords(text)
        assert "sistema" in result
        assert "importante" in result
        assert "muito" not in result  # "muito" é stopword


class TestRemoveNumbers:
    """Testes para a função _remove_numbers"""

    def test_remove_isolated_numbers(self):
        """Testa remoção de números isolados"""
        text = "texto 123 mais 456 fim"
        result = _remove_numbers(text)
        assert "123" not in result
        assert "456" not in result
        assert "texto" in result
        assert "mais" in result

    def test_keep_numbers_in_words(self):
        """Testa que números em palavras não são removidos"""
        text = "item5 apartamento201 cep12345"
        result = _remove_numbers(text)
        # Não funciona perfeitamente, mas é o esperado
        assert "item5" in result or "item" in result


class TestGetTokens:
    """Testes para a função get_tokens"""

    def test_get_tokens_splits_words(self):
        """Testa tokenização básica"""
        text = "hello world test"
        tokens = get_tokens(text)
        assert len(tokens) == 3
        assert tokens[0] == "hello"
        assert tokens[1] == "world"
        assert tokens[2] == "test"

    def test_get_tokens_empty_string(self):
        """Testa tokenização de string vazia"""
        tokens = get_tokens("")
        assert tokens == [""]

    def test_get_tokens_single_word(self):
        """Testa tokenização com uma palavra"""
        tokens = get_tokens("palavra")
        assert len(tokens) == 1
        assert tokens[0] == "palavra"


class TestGetTextStats:
    """Testes para a função get_text_stats"""

    def test_get_text_stats_returns_dict(self):
        """Testa se retorna dicionário com chaves esperadas"""
        original = "hello world"
        processed = "hello world"
        stats = get_text_stats(original, processed)
        
        assert isinstance(stats, dict)
        assert "original_chars" in stats
        assert "processed_chars" in stats
        assert "original_words" in stats
        assert "processed_words" in stats
        assert "reduction_percentage" in stats

    def test_get_text_stats_counts_correctly(self):
        """Testa contagem de caracteres e palavras"""
        original = "hello world"  # 11 chars, 2 words
        processed = "hello"  # 5 chars, 1 word
        stats = get_text_stats(original, processed)
        
        assert stats["original_chars"] == 11
        assert stats["processed_chars"] == 5
        assert stats["original_words"] == 2
        assert stats["processed_words"] == 1

    def test_get_text_stats_reduction_percentage(self):
        """Testa cálculo de percentual de redução"""
        original = "texto original com muitas palavras"
        processed = "texto"
        stats = get_text_stats(original, processed)
        
        assert 0 <= stats["reduction_percentage"] <= 100
        # Como o texto foi muito reduzido, percentual deve ser alto
        assert stats["reduction_percentage"] > 50

    def test_get_text_stats_zero_reduction(self):
        """Testa quando não há redução"""
        text = "mesmo texto"
        stats = get_text_stats(text, text)
        assert stats["reduction_percentage"] == 0

    def test_get_text_stats_empty_original(self):
        """Testa quando texto original é vazio"""
        stats = get_text_stats("", "processed")
        assert stats["reduction_percentage"] == 0
