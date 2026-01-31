from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Testa se o endpoint de health check retorna status 200 e contém a chave 'status'
def test_health_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data

# Testa se o endpoint de análise processa texto corretamente e retorna categoria e resposta sugerida
def test_analyze_with_text_returns_200():
    resp = client.post(
        "/api/analyze",
        data={"text": "Tenho um problema no sistema e preciso de suporte"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "category" in data
    assert "suggested_reply" in data

# Testa se o endpoint retorna erro quando nenhum texto ou arquivo é fornecido
def test_analyze_without_text_and_file_returns_error():
    resp = client.post("/api/analyze", data={})
    assert resp.status_code in (400, 422)

# Testa se a página de documentação Swagger UI está disponível no endpoint /api/docs
def test_docs_page_available():
    resp = client.get("/api/docs")
    assert resp.status_code == 200
    assert "Swagger UI" in resp.text or "swagger" in resp.text.lower()

# Testa se o arquivo JSON do OpenAPI está disponível e contém estrutura válida
def test_openapi_json_available():
    resp = client.get("/api/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "openapi" in data
    assert "paths" in data

# Testa se a resposta da análise segue o contrato esperado com categoria válida, resposta e confidence opcionalmente
def test_analyze_response_contract():
    resp = client.post("/api/analyze", data={"text": "Preciso de suporte no sistema"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["category"] in ("PRODUTIVO", "IMPRODUTIVO")
    assert isinstance(data["suggested_reply"], str)
    assert len(data["suggested_reply"]) > 0

    # se existir confidence:
    if "confidence" in data and data["confidence"] is not None:
        assert 0.0 <= float(data["confidence"]) <= 1.0

# Testa se o endpoint processa arquivos .txt corretamente e retorna análise válida
def test_analyze_with_txt_file_returns_200():
    file_content = "Olá, preciso de atualização do chamado 123.".encode("utf-8")
    files = {"file": ("email.txt", file_content, "text/plain")}

    resp = client.post("/api/analyze", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "category" in data
    assert "suggested_reply" in data

# Testa se o endpoint rejeita tipos de arquivo inválidos (como imagens) com erro apropriado
def test_analyze_rejects_invalid_file_type():
    files = {"file": ("image.jpg", b"fake", "image/jpeg")}
    resp = client.post("/api/analyze", files=files)
    assert resp.status_code in (400, 415, 422)
