"""
Repositório em memória com contas de demonstração para autenticação.
"""
from typing import NotRequired, TypedDict
from app.schemas.user_schemas import PerfilAcesso


class UsuarioArmazenado(TypedDict):
    email: str
    senha_hash: str
    perfil: PerfilAcesso
    crmv: NotRequired[str] # Só existe para veterinário


# Hash bcrypt da senha de demonstração "senha123".
_HASH_SENHA_DEMO = "$2b$12$KehcZRumtIPEg3iUtYi.9.lAehxi.qxbMdVjdCb/d7btwoc1.0Roy"

_USUARIOS_POR_EMAIL: dict[str, UsuarioArmazenado] = {
    "vet@clinica.com": {
        "email": "vet@clinica.com",
        "senha_hash": _HASH_SENHA_DEMO,
        "perfil": PerfilAcesso.VETERINARIO,
    },
    "recepcao@clinica.com": {
        "email": "recepcao@clinica.com",
        "senha_hash": _HASH_SENHA_DEMO,
        "perfil": PerfilAcesso.RECEPCIONISTA,
    },
    "cliente@clinica.com": {
        "email": "cliente@clinica.com",
        "senha_hash": _HASH_SENHA_DEMO,
        "perfil": PerfilAcesso.CLIENTE,
    },
    "adm@clinica.com": {
        "email": "adm@clinica.com",
        "senha_hash": _HASH_SENHA_DEMO,
        "perfil": PerfilAcesso.ADM,
    },

    "jáexiste@email.com": {
        "email": "jáexiste@email.com",
        "senha_hash": _HASH_SENHA_DEMO,
        "perfil": PerfilAcesso.CLIENTE,
    },
}


def normalizar_email(email: str) -> str:
    '''Deixa o e-mail num formato único para busca e cadastro (sem espaços nas pontas e tudo minúsculo).
       Sem isso, "VET@clinica.com" virava uma conta nova e o login com "Vet@clinica.com" falhava.
       Retorna o e-mail normalizado em str'''

    return email.strip().lower()


def buscar_usuario_por_email(email: str) -> UsuarioArmazenado | None:
    """Retorna uma conta de demonstração pelo e-mail, se estiver cadastrada."""
    return _USUARIOS_POR_EMAIL.get(normalizar_email(email))


def salvar_usuario(usuario: UsuarioArmazenado) -> UsuarioArmazenado:
    '''Guarda o usuário no "banco" em memória usando o e-mail normalizado como chave.
       Retorna o usuário salvo'''

    usuario["email"] = normalizar_email(usuario["email"]) # Salva sempre minúsculo para não duplicar conta
    _USUARIOS_POR_EMAIL[usuario["email"]] = usuario
    return usuario
