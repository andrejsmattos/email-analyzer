import re

def preprocess_text(text: str) -> str:
  """
  Pré-processa o texto para análise:
  - normaliza quebras de linha
  - remove espaços duplicados
  - remove excesso de quebras de linha
  - remove espaços no início/fim
  """

  if not text:
    return ""
  
  # Normaliza quebras de linha (Windows / Mac)
  text = text.replace("\r\n", "\n").replace("\r", "\n")

  # Remove tabs
  text = text.replace("\t", " ")

  # Remove espaços duplicados
  text = re.sub(r"[ ]{2,}", " ", text)

  # Remove excesso de quebras de linha
  text = re.sub(r"\n{3,}", "\n\n", text)

  return text.strip()