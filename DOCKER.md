# Email Analyzer - Docker Setup

## Build e Executar com Container

### Opção 1: Docker Compose (Recomendado)

```bash
# Build da imagem
docker compose build
# (ou: docker compose build)

# Executar o container
docker compose up -d
# (ou: docker compose up -d)

# Ver logs
docker compose logs -f
# (ou: docker compose logs -f)

# Parar o container
docker compose down
# (ou: docker compose down)
```

### Opção 2: Docker CLI

```bash
# Build da imagem
docker build -t email-analyzer:latest .

# Executar o container
docker run -d \
  --name email-analyzer \
  -p 8000:8000 \
  --env-file .env \
  email-analyzer:latest

# Ver logs
docker logs -f email-analyzer

# Parar o container
docker stop email-analyzer
docker rm email-analyzer
```

### Opção 3: Podman

```bash
# Build da imagem
podman build -t email-analyzer:local .

# Executar o container
podman run -d \
  --name email-analyzer \
  -p 8000:8000 \
  --env-file .env \
  localhost/email-analyzer:local

# Ver logs
podman logs -f email-analyzer

# Parar e remover
podman stop email-analyzer
podman rm email-analyzer
```

## Verificação de Saúde

```bash
# Verificar se o serviço está rodando
curl http://localhost:8000/api/health
```

## Variáveis de Ambiente

As seguintes variáveis devem estar configuradas no arquivo `.env`:

- `OPENAI_API_KEY_EMAIL_ANALYZER` - Chave da API OpenAI
- `MAX_UPLOAD_SIZE` - Tamanho máximo de upload em bytes (padrão: 16MB)

## Estrutura da Imagem

- **Base Image:** `python:3.11-slim`
- **Working Directory:** `/app`
- **Port:** 8000
- **User:** `appuser` (não-root por segurança)
- **Health Check:** Verifica `/api/health` a cada 30 segundos

## Troubleshooting

### Container não inicia

```bash
# Verificar logs detalhados
docker compose logs email-analyzer

# Verificar se a porta 8000 já está em uso

# Windows
netstat -ano | findstr :8000

# Linux / macOS
lsof -i :8000
```

### Erro de API Key

- Certifique-se de que o arquivo `.env` existe na raiz do projeto
- Verifique se `OPENAI_API_KEY_EMAIL_ANALYZER` está configurado corretamente
- Não versionar o arquivo `.env` no repositório

### Arquivo muito grande

```bash
# Se receber erro 413 (Payload Too Large)
# Verifique o valor de MAX_UPLOAD_SIZE no .env
# Padrão: 16777216 (16MB)
```

### spaCy model não encontrado

```bash
# Se o container falhar ao baixar o modelo português
# Tente reconstruir a imagem
docker compose build --no-cache
```

### Port já em uso

```bash
# Se a porta 8000 está em uso, mude no docker compose.yml:
# Altere "8000:8000" para "8001:8000"
# Depois execute:
docker compose up -d
```

## Notas

- O Dockerfile usa uma imagem `slim` para reduzir tamanho
- O usuário `appuser` é criado para segurança
- O health check está configurado para monitoramento automático
- O spaCy language model (pt_core_news_sm) é baixado durante o build
- O frontend é servido separadamente (não incluído neste container)


### Erro de API Key

- Certifique-se de que o arquivo `.env` existe na raiz do projeto
- Verifique se `OPENAI_API_KEY_EMAIL_ANALYZER` está configurado corretamente
- Não commit do `.env` no repositório

### Arquivo muito grande

```bash
# Se receber erro 413 (Payload Too Large)
# Verifique o valor de MAX_UPLOAD_SIZE no .env
# Padrão: 16777216 (16MB)
```

### spaCy model não encontrado

```bash
# Se o container falhar ao baixar o modelo português
# Tente reconstruir a imagem
docker compose build --no-cache
```

### Port já em uso

```bash
# Se a porta 8000 está em uso, mude no docker compose.yml:
# Altere "8000:8000" para "8001:8000"
# Depois execute:
docker compose up -d
```

- O frontend é servido separadamente (não incluído neste container)
