import pytest
from app.schemas.user_schemas import UsuarioCreate, PerfilAcesso
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.user_repository import _USUARIOS_POR_EMAIL
import copy

# Instancia um cliente de teste para a API
teste = TestClient(app)

@pytest.fixture(autouse = True)
def limpar_banco_dados_cada_teste():
    estado_inicial = copy.deepcopy(_USUARIOS_POR_EMAIL)

    # Interrompe para o pytest fazer os testes
    yield  

    # limpa o banco de dados após o teste 
    _USUARIOS_POR_EMAIL.clear()
    # retorna ao estado inicial do banco (em: app/repositories/user_repository)
    _USUARIOS_POR_EMAIL.update(estado_inicial)


# Cadastro de CLientes (CT-CC)
@pytest.mark.parametrize('ct_id ,email, senha, perfil, cod_esperado',   

[   # Cenário Valido
    ("CT-CC-01", "novo@email.com", "senha123", PerfilAcesso.CLIENTE, 201),       # Usuario com email, senha e perfil corretos

    # Cenários inválidos              
    ("CT-CC-02", "jáexiste@email.com", "senha123", PerfilAcesso.CLIENTE, 400),   # Email já existente
    ("CT-CC-03", "", "senha123", PerfilAcesso.CLIENTE, 400),                     # Email vazio
    ("CT-CC-04", "cadc04@email.com", "", PerfilAcesso.CLIENTE, 400),             # Senha vazia
    ("CT-CC-05", "cadc05@email.com", "senha12", PerfilAcesso.CLIENTE, 400),      # Senha menor que 8 caracteres
    ("CT-CC-06", "cadc06@email.com", "senha12345678901234567890123456789012345678901234567890123456789012345678", PerfilAcesso.CLIENTE, 400),       
                                                                                 # Senha maior que 72 caracteres
    ("CT-CC-07", "cadc07@email.com", "senha123", PerfilAcesso.VETERINARIO, 400), # Perfil de acesso errado (não cliente)
    ("CT-CC-08", "cadc08@email.com", "senha123", "", 400)                        # Perfil de acesso vazio
    
])
def test_cadastro_clientes(ct_id, email, senha, perfil, cod_esperado):
    payload = {
        "email" : email,
        "senha" : senha,
        "perfil_acesso" : perfil.value if hasattr(perfil, "value") else perfil,
    }
    resposta = teste.post("/auth/cadastro", json=payload)
    assert resposta.status_code == cod_esperado, f"falha no {ct_id}: O esperado seria: {cod_esperado} e obteve {resposta.status_code}"




# Cadastro de Funcionários (CT-CF)
@pytest.mark.parametrize('ct_id, email, senha, perfil, CRMV, cod_esperado',                       
    [   
        # Cenários válidos
        ("CT-CF-01", "novo1@email.com", "senha123", PerfilAcesso.RECEPCIONISTA, "", 201),         # Cadastro de funcionario comum (sem CRMV)
        ("CT-CF-02", "novo2@email.com", "senha123", PerfilAcesso.VETERINARIO, "SP 12345", 201),   # Cadastro de veterinário

        # Cenários Inválidos
        ("CT-CF-03", "recepcao@clinica.com", "senha123", PerfilAcesso.RECEPCIONISTA, "", 400),    # Email existente
        ("CT-CF-04", "", "senha123", PerfilAcesso.RECEPCIONISTA, "", 400),                        # Email vazio
        ("CT-CF-05", "cadf05@email.com", "", PerfilAcesso.RECEPCIONISTA, "", 400),                # Senha vazia         
        ("CT-CF-06", "cadf06@email.com", "senha12", PerfilAcesso.RECEPCIONISTA, "", 400),         # Senha inferior a 8 caracteres
        ("CT-CF-07", "cadf07@email.com", "senha12345678901234567890123456789012345678901234567890123456789012345678", PerfilAcesso.RECEPCIONISTA, "", 400), 
                                                                                                  # Senha superior a 72 caracteres
        ("CT-CF-08", "cadf08@email.com", "senha123", PerfilAcesso.CLIENTE, "", 400),              # Perfil de acesso errado (cliente)
        ("CT-CF-09", "cadf09@email.com", "senha123", "", "", 400),                                # Perfil de acesso vazio
        ("CT-CF-10", "cadf10@email.com", "senha123", PerfilAcesso.VETERINARIO, "", 400)           # Perfil de acesso veterinário sem CRMV
    ])

def test_cadastro_funcionarios(ct_id, email, senha, perfil, CRMV, cod_esperado):
    payload = { 
        "email" : email, 
        "senha" : senha,
        "perfil_acesso" : perfil.value if hasattr(perfil, "value") else perfil, 
        "crmv" : CRMV,
    }
    resposta = teste.post("auth/cadastro", json=payload)
    assert resposta.status_code == cod_esperado, f"falha no {ct_id}: O esperado seria {cod_esperado} e foi entregue {resposta.status_code}"
    