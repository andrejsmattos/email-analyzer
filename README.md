# Email Analyzer

Sistema de análise e classificação automática de emails corporativos usando IA (OpenAI GPT).

## 📋 Descrição

O Email Analyzer é uma API REST que classifica emails corporativos em duas categorias:

- **PRODUTIVO**: emails que requerem ação, decisão ou resposta específica
- **IMPRODUTIVO**: emails que não requerem ação imediata (agradecimentos, avisos gerais, etc)

Além da classificação, o sistema gera automaticamente sugestões de resposta e fornece a justificativa da análise.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **OpenAI API** - LLM para análise e classificação
- **Pydantic** - Validação de dados
- **spaCy** - Processamento NLP em português
- **Python 3.11+** - Linguagem base
- **pypdf** - Extração de texto de PDFs

## 📦 Pré-requisitos

- Python 3.11 ou superior
- Conta na OpenAI com API Key
- pip (gerenciador de pacotes Python)

## ⚙️ Instalação

1. Clone o repositório:

```bash
git clone https://github.com/andrejsmattos/email-analyzer.git
cd email-analyzer
```

2. Crie um ambiente virtual:

```bash
python -m venv venv
```

3. Ative o ambiente virtual:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. **[Opcional]** Instale o modelo de linguagem português para lemmatização avançada:

```bash
python -m spacy download pt_core_news_sm
```

Este modelo é opcional e melhora a qualidade do pré-processamento, mas não é obrigatório para o funcionamento básico.

## 🔑 Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY_EMAIL_ANALYZER=sua-chave-api-aqui
```

## 🏃 Como Executar

### Desenvolvimento (com reload automático)

```bash
uvicorn app.main:app --reload
```

### Produção

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

## 📚 Documentação API

Acesse a documentação interativa (Swagger):

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 Endpoints

### `GET /api/health`

Verifica o status da API.

**Resposta:**

```json
{
  "status": "ok"
}
```

### `POST /api/analyze`

Analisa um email e retorna a classificação com sugestão de resposta.

**Parâmetros (Form Data):**

- `text` (string, opcional): Texto do email
- `file` (file, opcional): Arquivo .txt ou .pdf

**Resposta de sucesso (200):**

```json
{
  "category": "PRODUTIVO",
  "suggested_reply": "Olá! Recebemos sua mensagem e iremos analisar sua solicitação em breve.",
  "confidence": 0.92,
  "extracted_chars": 245,
  "content": "Prezados, temos um problema com o sistema...",
  "reason": "Email contém problema que requer ação e resposta"
}
```

**Resposta de erro (400):**

```json
{
  "error": true,
  "status_code": 400,
  "detail": "Conteúdo do email está vazio",
  "message": "Requisição inválida. Verifique os parâmetros enviados."
}
```

## 📁 Estrutura do Projeto

```
email-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Configuração principal da aplicação
│   ├── exceptions.py           # Handlers de exceções
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # Rotas da API
│   ├── clients/
│   │   ├── __init__.py
│   │   └── llm_client.py       # Cliente OpenAI
│   ├── domain/
│   │   └── email_category.py  # Enum de categorias
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── dto.py              # Modelos Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   └── analyzer_service.py # Lógica de análise
│   └── utils/
│       ├── file_reader.py      # Extração de texto
│       └── text_preprocessor.py # Limpeza de texto
├── scripts/
│   └── eval_emails.py          # Script de avaliação
├── .env                        # Variáveis de ambiente (não commitado)
├── requirements.txt            # Dependências Python
└── README.md                   # Este arquivo
```

## 🧪 Testando a API

### Com curl:

```bash
# Enviando texto
curl -X POST "http://localhost:8000/api/analyze" \
  -F "text=Prezados, estou com um problema no sistema de pedidos."

# Enviando arquivo
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@email.txt"
```

### Com Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    data={"text": "Obrigado pela ajuda!"}
)
print(response.json())
```

## � Pré-processamento de Texto

O sistema realiza pré-processamento robusto dos emails antes da análise:

1. **Normalização** - Remove espaços duplicados, tabs e quebras de linha excessivas
2. **Lowercase** - Converte todo o texto para minúsculas
3. **Remoção de Pontuação** - Remove caracteres especiais (mantém acentos)
4. **Remoção de Stop Words** - Remove palavras vazias em português (a, o, de, etc)
5. **Remoção de Números** - Remove números isolados
6. **Tokenização** - Divide o texto em palavras

Exemplo de transformação:

```
Original: "Olá! Temos um PROBLEMA crítico no sistema (2024). Respondam URGENTE!!!"
Processado: "problema crítico sistema responda urgente"
```

Funções disponíveis em `app/utils/text_preprocessor.py`:

- `preprocess_text()` - Pré-processa o texto completo
- `get_tokens()` - Retorna lista de palavras
- `get_text_stats()` - Retorna estatísticas de processamento

## �🛡️ Tratamento de Erros

O sistema possui tratamento robusto de erros:

- **400**: Requisição inválida (texto vazio, formato inválido)
- **422**: Erro de validação de dados
- **500**: Erro interno do servidor
- **503**: Serviço de IA indisponível

Todos os erros retornam mensagens amigáveis em português.

## 👤 Autor

André Mattos - [GitHub](https://github.com/andrejsmattos)
