import asyncio

from app.services.analyzer_service import EmailAnalyzerService
from app.domain.email_category import EmailCategory

TEST_CASES = [
    {
        "id": 1,
        "expected": EmailCategory.PRODUTIVO,
        "email": "Olá, não consigo acessar o sistema desde ontem. Aparece erro 500. Podem verificar?",
    },
    {
        "id": 2,
        "expected": EmailCategory.IMPRODUTIVO,
        "email": "Oi! Passando pra agradecer o suporte, resolveu tudo. Obrigado!",
    },
    {
        "id": 3,
        "expected": EmailCategory.PRODUTIVO,
        "email": "Bom dia, poderia me informar o status do chamado #1234 e a previsão de solução?",
    },
    {
        "id": 4,
        "expected": EmailCategory.IMPRODUTIVO,
        "email": "Parabéns pelo lançamento da nova versão! Ficou excelente.",
    },
    {
        "id": 5,
        "expected": EmailCategory.PRODUTIVO,
        "email": "Preciso atualizar os dados cadastrais da empresa. Como faço essa alteração no sistema?",
    },
]

async def main():
    service = EmailAnalyzerService()

    total = len(TEST_CASES)
    correct = 0

    for t in TEST_CASES:
        resp = await service.analyze(text=t["email"])
        ok = resp.category == t["expected"]
        correct += 1 if ok else 0

        status = "✅ ACERTOU" if ok else "❌ ERROU"
        print("=" * 80)
        print(f"[{t['id']}] {status}")
        print(f"Esperado: {t['expected']}")
        print(f"Previsto : {resp.category} (conf={resp.confidence})")
        if resp.reason:
            print(f"Motivo   : {resp.reason}")
        print("-" * 80)
        print("Email:")
        print(t["email"])
        print("-" * 80)
        print("Resposta sugerida:")
        print(resp.suggested_reply)

    print("=" * 80)
    print(f"Resumo: {correct}/{total} = {correct/total:.0%} accuracy")

if __name__ == "__main__":
    asyncio.run(main())
