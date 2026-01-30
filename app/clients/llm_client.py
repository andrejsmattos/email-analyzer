import json
import os
import logging
from openai import OpenAI
from app.domain.email_category import EmailCategory

logger = logging.getLogger(__name__)

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

        except Exception as e:
            # Fallback: análise heurística simples baseada em keywords
            logger.warning(f"Falha ao consultar LLM, usando fallback: {str(e)}")
            return _fallback_classify(content)


def _fallback_classify(content: str) -> dict:
    """
    Classificação heurística quando LLM falha.
    Baseada em keywords para determinar se requer ação.
    A confiança reflete o quão claro foi a decisão.
    
    Args:
        content: Texto preprocessado
        
    Returns:
        Dict com classificação básica
    """
    content_lower = content.lower()
    
    # Keywords que indicam PRODUTIVO (requer ação)
    produtivo_keywords = {
        "erro", "problema", "suporte", "ajuda", "socorro",
        "urge", "urgente", "prazo", "deadline", "status",
        "fazer", "realizar", "executar", "implementar",
        "solicit", "pedido", "request", "chamado", "ticket",
        "bug", "falha", "não funciona", "quebrou",
        "preciso", "precisa", "necessário", "necessita",
        "quando", "até quando", "para quando",
        "aprovação", "aprovado", "rejeição", "rejeitado"
    }
    
    # Keywords que indicam IMPRODUTIVO (não requer ação)
    improdutivo_keywords = {
        "obrigado", "obrigada", "agradeço", "agradec",
        "valeu", "thanks", "thank you", "muito obrigado",
        "feliz", "felicid", "parabéns", "parabens",
        "sucesso", "consegui", "conseguiu", "conseguiram",
        "resolveu", "foi resolvido", "foi solucionado",
        "funcionou", "deu certo", "ok", "perfeito",
        "informação", "aviso", "notícia", "comunicado",
        "passou para informar", "informando que",
        "só pra avisar", "só informando"
    }
    
    # Contar ocorrências
    produtivo_count = sum(1 for kw in produtivo_keywords if kw in content_lower)
    improdutivo_count = sum(1 for kw in improdutivo_keywords if kw in content_lower)
    
    # Calcular confiança baseado em clareza da decisão
    total_keywords = produtivo_count + improdutivo_count
    if total_keywords == 0:
        # Nenhuma keyword encontrada = baixíssima confiança
        confidence = 0.3
    else:
        # Quanto maior a diferença, maior a confiança
        diff = abs(produtivo_count - improdutivo_count)
        # Escala: 0 (empate) até 1.0 (muito claro)
        confidence = min(0.95, 0.3 + (diff / total_keywords) * 0.65)
    
    # Decidir baseado em contagem e contexto
    if len(content.strip()) < 10:
        # Textos muito curtos são improdutivos (spam, testes, etc)
        categoria = EmailCategory.IMPRODUTIVO
        reply = "Olá! Recebemos sua mensagem, mas ela parece estar incompleta. Envie mais detalhes para que possamos ajudar."
        confidence = 0.5  # Média confiança para textos muito curtos
    elif improdutivo_count > produtivo_count:
        categoria = EmailCategory.IMPRODUTIVO
        reply = "Olá! Obrigado pelo contato. Mensagem recebida."
    elif produtivo_count > improdutivo_count:
        categoria = EmailCategory.PRODUTIVO
        reply = (
            "Olá! Recebemos sua mensagem e vamos analisar sua solicitação. "
            "Se possível, envie mais detalhes para agilizar."
        )
    else:
        # Empate ou ambos 0: sem contexto suficiente = IMPRODUTIVO
        categoria = EmailCategory.IMPRODUTIVO
        reply = "Olá! Recebemos sua mensagem, mas não identificamos uma solicitação clara. Envie mais informações."
    
    return {
        "category": categoria,
        "suggested_reply": reply,
        "confidence": round(confidence, 2),
        "reason": f"Fallback: análise heurística (produtivo_score={produtivo_count}, improdutivo_score={improdutivo_count})"
    }
