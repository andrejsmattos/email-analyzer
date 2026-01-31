# Usar imagem oficial do Python como base
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para melhor cache
COPY requirements.txt .

# Install Python dependencies (inclui spacy==3.7.2)
RUN pip install --no-cache-dir -r requirements.txt

# Instalar modelo PT do spaCy via wheel fixado (build reprodutível)
ARG SPACY_MODEL_URL="https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.7.0/pt_core_news_sm-3.7.0-py3-none-any.whl"
RUN pip install --no-cache-dir "${SPACY_MODEL_URL}"

# Validar que o modelo carrega (falha rápida)
RUN python -c "import spacy; nlp=spacy.load('pt_core_news_sm'); print('spaCy OK:', nlp.pipe_names)"

# Excluir testes e cache do build Docker
RUN echo ".pytest_cache" >> .dockerignore
RUN echo "tests" >> .dockerignore

# Copiar código da aplicação
COPY . .

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Verificação de saúde
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()"

# Executar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
