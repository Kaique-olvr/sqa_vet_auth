# sqa_vet_auth
Microsserviço de autenticação e controle de acesso (RBAC) com FastAPI e suíte de testes em Pytest para SQA.

# Rodando localmente

1. Criar o ambiente virtual:
   python -m venv venv

2. Ativar o ambiente virtual:
   .\venv\Scripts\Activate.ps1   # Windows

3. Instalar dependências:
   pip install -r requirements.txt

4. Criar o arquivo .env a partir do exemplo:
   copy .env.example .env   # Windows

5. Rodar os testes:
   pytest -v

6. Rodar a API:
   uvicorn app.main:app --reload
   Documentação interativa em http://127.0.0.1:8000/docs

# Testando pelo Swagger (/docs)

1. Em POST /auth/login, envie { "email": "vet@clinica.com", "senha": "senha123" }
2. Copie o "access_token" da resposta
3. Clique em "Authorize" e cole o token
4. Teste GET /auth/meu-perfil e POST /prontuarios (este só libera para veterinário)

Usuários de teste (senha "senha123"): vet@clinica.com (veterinario) e recepcao@clinica.com (recepcionista)
