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

1. Em POST /auth/login, clique em "Try it out" e "Execute" (o exemplo já vem com { "email": "vet@clinica.com", "senha": "senha123" })
2. Copie só o valor do "access_token", sem as aspas
3. Clique em "Authorize" e cole o token (não precisa escrever "Bearer")
4. Teste GET /auth/meu-perfil e POST /prontuarios (este só libera para veterinário)

# Rotas de cadastro

- POST /auth/cadastro: público, cria sempre uma conta com perfil cliente (RN04). Não aceita o campo perfil_acesso.
- POST /auth/cadastro/funcionario: somente adm (RN03). Cadastra veterinario, recepcionista ou adm. Para veterinario o campo crmv é obrigatório (RF03).

As contas abaixo são dados de demonstração em memória (senha "senha123"); não são persistidas e são perdidas ao reiniciar a aplicação:

- vet@clinica.com (veterinario)
- recepcao@clinica.com (recepcionista)
- cliente@clinica.com (cliente)
- adm@clinica.com (adm)

# Testes de carga (Locust)

Os cenários ficam em tests/carga/locustfile.py e simulam veterinários, recepcionistas e novos clientes usando a API ao mesmo tempo.

1. Em um terminal, suba a API: uvicorn app.main:app
2. Em outro terminal, rode um dos cenários:

        # Carga normal: 50 usuários
        locust -f tests/carga/locustfile.py --host http://127.0.0.1:8000 --headless -u 50 -r 5 -t 90s --html relatorio_50.html

        # Estresse: 200 usuários
        locust -f tests/carga/locustfile.py --host http://127.0.0.1:8000 --headless -u 200 -r 10 -t 90s --html relatorio_200.html

   Para ver os gráficos ao vivo, rode sem o --headless e abra http://localhost:8089

O teste reprova (código de saída 1) se tiver qualquer erro ou se o p95 do cadastro ou do login passar de 5 segundos (RNF04).
