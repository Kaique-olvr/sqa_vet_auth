'''Testes de carga e desempenho do microsserviço usando o Locust.

Cada classe abaixo simula um tipo de usuário da clínica fazendo requisições ao mesmo tempo.
O Locust mede o tempo de resposta de cada rota e conta quantas falharam (taxa de erros).

Como rodar (com a API já ligada em outro terminal com: uvicorn app.main:app):
    Com tela:  locust -f tests/carga/locustfile.py --host http://127.0.0.1:8000
               e abrir http://localhost:8089 no navegador
    Sem tela:  ver os comandos no README (seção "Testes de carga")

Critério de aprovação: RNF04, a validação de email e senha (cadastro e login) deve responder em até 5 segundos.
'''
import uuid # Gera um código único, usado para criar emails diferentes em cada cadastro
from locust import HttpUser, task, between, events

SENHA_DEMO = "senha123" # Senha das contas de demonstração (app/repositories/user_repository.py)
LIMITE_RNF04_MS = 5000 # 5 segundos, em milissegundos, que é a unidade que o Locust usa


def fazer_login(usuario: HttpUser, email: str, senha: str = SENHA_DEMO) -> dict:
    '''Faz o login pela API e devolve o header Authorization pronto para usar nas próximas requisições.
       Se o login falhar, devolve um header vazio (as rotas protegidas vão responder 401 e isso aparece como erro)'''

    resposta = usuario.client.post("/auth/login", json={"email": email, "senha": senha}, name="POST /auth/login")

    if resposta.status_code != 200:
        return {}

    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def validar_status(resposta, status_esperado: int):
    '''Marca a requisição como sucesso só se o status for o esperado.
       Usado porque um 403 para a recepcionista é o comportamento CERTO (RN01), então não pode contar como erro.
       Também marca como falha qualquer resposta acima do limite do RNF04'''

    if resposta.status_code != status_esperado:
        resposta.failure(f"Esperado {status_esperado}, recebido {resposta.status_code}")
    elif resposta.elapsed.total_seconds() * 1000 > LIMITE_RNF04_MS:
        resposta.failure(f"Passou do limite de {LIMITE_RNF04_MS} ms do RNF04")
    else:
        resposta.success()


class Veterinario(HttpUser):
    """
    Veterinário logado consultando o perfil e criando prontuários (deve receber 200).
    """
    weight = 3 # Peso: de cada 6 usuários simulados, 3 são veterinários
    wait_time = between(1, 3) # Espera de 1 a 3 segundos entre uma ação e outra, como uma pessoa usando o sistema

    def on_start(self):
        # Executa uma vez quando o usuário simulado "entra" no sistema
        self.header = fazer_login(self, "vet@clinica.com")

    @task(3)
    def ver_perfil(self):
        with self.client.get("/auth/meu-perfil", headers=self.header, name="GET /auth/meu-perfil", catch_response=True) as resposta:
            validar_status(resposta, 200)

    @task(2)
    def criar_prontuario(self):
        with self.client.post("/prontuarios", headers=self.header, name="POST /prontuarios (vet)", catch_response=True) as resposta:
            validar_status(resposta, 200)


class Recepcionista(HttpUser):
    """
    Recepcionista logada tentando criar prontuário (deve receber 403, RN01).
    """
    weight = 2
    wait_time = between(1, 3)

    def on_start(self):
        self.header = fazer_login(self, "recepcao@clinica.com")

    @task(2)
    def ver_perfil(self):
        with self.client.get("/auth/meu-perfil", headers=self.header, name="GET /auth/meu-perfil", catch_response=True) as resposta:
            validar_status(resposta, 200)

    @task(1)
    def tentar_criar_prontuario(self):
        with self.client.post("/prontuarios", headers=self.header, name="POST /prontuarios (recepção, 403)", catch_response=True) as resposta:
            validar_status(resposta, 403) # Bloqueio esperado, conta como sucesso


class NovoCliente(HttpUser):
    """
    Pessoa nova se cadastrando como cliente e depois fazendo login.
    É o fluxo mais pesado, porque o bcrypt é usado no cadastro (hash) e no login (verificação).
    """
    weight = 1
    wait_time = between(1, 3)

    @task
    def cadastrar_e_logar(self):
        email = f"cliente_{uuid.uuid4().hex[:10]}@carga.com" # Email diferente a cada cadastro para não dar "email já utilizado"

        with self.client.post("/auth/cadastro", json={"email": email, "senha": "senhacarga123"}, name="POST /auth/cadastro", catch_response=True) as resposta:
            validar_status(resposta, 201)

        with self.client.post("/auth/login", json={"email": email, "senha": "senhacarga123"}, name="POST /auth/login", catch_response=True) as resposta:
            validar_status(resposta, 200)


@events.quitting.add_listener
def verificar_rnf04(environment, **kwargs):
    '''No fim do teste, confere o p95 (95% das requisições) de cadastro e login contra o RNF04.
       Se passar de 5 s ou tiver qualquer erro, o Locust termina com código 1 (útil para rodar em pipeline)'''

    estatisticas = environment.stats

    for rota in ("POST /auth/cadastro", "POST /auth/login"):
        entrada = estatisticas.get(rota, "POST")
        if entrada.num_requests and entrada.get_response_time_percentile(0.95) > LIMITE_RNF04_MS:
            print(f"[RNF04] REPROVADO: p95 de {rota} acima de {LIMITE_RNF04_MS} ms")
            environment.process_exit_code = 1

    if estatisticas.total.fail_ratio > 0:
        print(f"[ERROS] Taxa de erros de {estatisticas.total.fail_ratio:.2%}")
        environment.process_exit_code = 1
