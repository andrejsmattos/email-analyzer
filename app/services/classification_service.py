from app.domain.email_category import EmailCategory

class EmailClassificationService:
  """
  Serviço responsável por classificar o email com base em regras simples
  """

  PRODUTIVE_KEYWORDS = [
      "erro",
      "problema",
      "suporte",
      "status",
      "atualização",
      "prazo",
      "solicito",
      "solicitação",
      "chamado",
      "dúvida",
      "acesso",
  ]

  def classify(self, content: str) -> EmailCategory:
    text = content.lower()

    for keyword in self.PRODUTIVE_KEYWORDS:
      if keyword in text:
        return EmailCategory.PRODUTIVO
      
    return EmailCategory.IMPRODUTIVO