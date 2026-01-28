from enum import Enum

class EmailCategory(str, Enum):
  PRODUTIVO = "PRODUTIVO",
  IMPRODUTIVO = "IMPRODUTIVO"