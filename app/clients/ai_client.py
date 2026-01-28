from app.domain.email_category import EmailCategory


class AIClient:
    """
    Cliente de IA (stub inicial).
    No futuro, será substituído por integração real
    (OpenAI, HuggingFace, etc).
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

    def analyze(self, content: str) -> dict:
        text = content.lower()

        category = (
            EmailCategory.PRODUTIVO
            if any(k in text for k in self.PRODUTIVE_KEYWORDS)
            else EmailCategory.IMPRODUTIVO
        )

        return {
            "category": category,
            "suggested_reply": self._default_reply(category),
            "confidence": 0.7,
        }

    def _default_reply(self, category: EmailCategory) -> str:
        if category == EmailCategory.PRODUTIVO:
            return (
                "Olá! Recebemos sua mensagem e "
                "iremos analisar sua solicitação em breve."
            )

        return (
            "Olá! Obrigado pelo contato. "
            "Esta é uma mensagem informativa automática."
        )
