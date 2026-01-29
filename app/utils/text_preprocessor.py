import re
import string
import logging
from typing import List

logger = logging.getLogger(__name__)

# Stop words em português (palavras sem significado semântico)
PORTUGUESE_STOP_WORDS = {
    "a", "o", "e", "é", "de", "da", "do", "em", "um", "uma",
    "por", "para", "com", "que", "se", "não", "os", "as", "dos", "das",
    "mais", "como", "mas", "ao", "ele", "ela", "seu", "sua", "ou", "ser",
    "quando", "muito", "há", "nos", "já", "está", "eu", "também", "só",
    "pelo", "pela", "peor", "pera", "este", "esse", "aquele", "este",
    "aquilo", "isso", "este", "estes", "essas", "aquelas", "nosso", "vosso",
    "meu", "teu", "dele", "dela", "nos", "vos", "lhe", "lhes", "me", "te",
    "nos", "vos", "o", "a", "os", "as", "um", "uma", "uns", "umas"
}

def preprocess_text(text: str) -> str:
    """
    Pré-processa o texto com processamento NLP completo:
    1. Normaliza quebras de linha e espaços
    2. Remove pontuação e caracteres especiais
    3. Converte para lowercase
    4. Remove stop words
    5. Remove números isolados
    6. Remove espaços duplicados finais
    
    Args:
        text: Texto bruto a processar
        
    Returns:
        Texto preprocessado e limpo
    """
    
    if not text or not isinstance(text, str):
        return ""
    
    # 1. Normalizar quebras de linha e espaços
    text = _normalize_whitespace(text)
    
    # 2. Converter para lowercase
    text = text.lower()
    
    # 3. Remover pontuação e caracteres especiais (mantém acentos)
    text = _remove_punctuation(text)
    
    # 4. Remover stop words
    text = _remove_stopwords(text)
    
    # 5. Remover números isolados
    text = _remove_numbers(text)
    
    # 6. Limpar espaços duplicados finais
    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def _normalize_whitespace(text: str) -> str:
    """Normaliza quebras de linha e espaços"""
    # Normaliza quebras de linha (Windows / Mac / Unix)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Remove tabs
    text = text.replace("\t", " ")
    
    # Remove espaços duplicados
    text = re.sub(r"[ ]{2,}", " ", text)
    
    # Remove excesso de quebras de linha (máx 2 consecutivas)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text


def _remove_punctuation(text: str) -> str:
    """Remove pontuação mantendo apenas palavras e números"""
    # Remove pontuação padrão (mantém hífens em palavras compostas)
    text = re.sub(r"[^\w\s\-áéíóúàãõâêôç]", " ", text)
    
    # Remove hífens isolados
    text = re.sub(r"\s\-\s", " ", text)
    
    return text


def _remove_stopwords(text: str) -> str:
    """Remove stop words em português"""
    words = text.split()
    filtered_words = [
        word for word in words 
        if word not in PORTUGUESE_STOP_WORDS and len(word) > 1
    ]
    return " ".join(filtered_words)


def _remove_numbers(text: str) -> str:
    """Remove números isolados mantendo palavras com dígitos"""
    # Remove números isolados
    text = re.sub(r"\b\d+\b", "", text)
    return text


def get_tokens(text: str) -> List[str]:
    """
    Tokeniza o texto processado em palavras.
    
    Args:
        text: Texto preprocessado
        
    Returns:
        Lista de tokens (palavras)
    """
    return text.split()


def get_text_stats(original_text: str, processed_text: str) -> dict:
    """
    Retorna estatísticas de processamento do texto.
    
    Args:
        original_text: Texto original
        processed_text: Texto processado
        
    Returns:
        Dict com estatísticas
    """
    return {
        "original_chars": len(original_text),
        "processed_chars": len(processed_text),
        "original_words": len(original_text.split()),
        "processed_words": len(processed_text.split()),
        "reduction_percentage": round(
            (1 - len(processed_text) / len(original_text)) * 100, 2
        ) if original_text else 0
    }