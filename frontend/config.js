// API Configuration
// Altere esta variável conforme o ambiente:
// - Desenvolvimento: http://localhost:8000/api
// - Produção: https://seu-dominio.com/api
const API_URL =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000/api"
    : `${window.location.protocol}//${window.location.host}/api`;

// Ou configure manualmente (descomente a linha abaixo):
// const API_URL = 'http://localhost:8000/api';
