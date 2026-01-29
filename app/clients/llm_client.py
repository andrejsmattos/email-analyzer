import json
import os
from openai import OpenAI
from app.domain.email_category import EmailCategory

EMAIL_ANALYSIS_SCHEMA = {
    "name": "email_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "category": {"type": "string", "enum": ["PRODUTIVO", "IMPRODUTIVO"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reason": {"type": "string", "minLength": 1},
            "suggested_reply": {"type": "string", "minLength": 1},
        },
        "required": ["category", "confidence", "reason", "suggested_reply"],
    },
    "strict": True,
}

SYSTEM_PROMPT = """Você é um classificador de emails corporativos em pt-BR.

Definições:
- PRODUTIVO: requer ação, decisão, resposta específica ou acompanhamento.
- IMPRODUTIVO: não requer ação imediata (agradecimento, felicitação, aviso sem demanda).

Regras:
- Baseie-se apenas no conteúdo fornecido.
- Não invente dados (nomes, prazos, protocolos).
- Seja objetivo.
- A resposta sugerida deve ser educada, curta e útil.
- Retorne APENAS um JSON válido conforme o schema.
"""

def build_user_prompt(email_text: str) -> str:
    return f"""Classifique o email e gere uma resposta automática adequada.

Email:
\"\"\"{email_text}\"\"\"

Critérios:
- Se houver pedido, dúvida, problema, cobrança, solicitação de status/acesso: PRODUTIVO.
- Se for apenas agradecimento/felicitação/aviso sem demanda: IMPRODUTIVO.

Retorne os campos do schema.
"""


class OpenAILLMClient:
    """
    Cliente LLM (OpenAI) com saída estruturada (JSON Schema).
    Mantém a mesma assinatura do AIClient: analyze(content) -> dict
    """

    def __init__(self, model: str = "gpt-4.1-mini"):
        api_key = os.getenv("OPENAI_API_KEY_EMAIL_ANALYZER")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada no ambiente.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze(self, content: str) -> dict:
        # Proteção básica: não mandar texto gigante
        trimmed = content[:6000]

        try:
            resp = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(trimmed)},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": EMAIL_ANALYSIS_SCHEMA["name"],
                        "schema": EMAIL_ANALYSIS_SCHEMA["schema"],
                        "strict": EMAIL_ANALYSIS_SCHEMA["strict"],
                    }
                },
                temperature=0.2,
            )

            # SDK recente expõe output_text. Se não expuser no seu, ajuste para ler o item do output.
            data = json.loads(resp.output_text)

            category = EmailCategory(data["category"])

            return {
                "category": category,
                "suggested_reply": data["suggested_reply"],
                "confidence": round(float(data["confidence"]), 2),
                "reason": data["reason"],
            }

        except Exception:
            # Fallback conservador: se falhar, devolve improdutivo com baixa confiança + reply neutra
            return {
                "category": EmailCategory.PRODUTIVO,
                "suggested_reply": (
                    "Olá! Recebemos sua mensagem e vamos analisar sua solicitação. "
                    "Se possível, envie mais detalhes para agilizar."
                ),
                "confidence": 0.5,
                "reason": "Fallback: falha ao consultar o LLM.",
            }
