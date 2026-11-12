"""
Repositório em memória com contas de demonstração para autenticação.
"""
from typing import TypedDict
from app.schemas.user_schemas import PerfilAcesso


class UsuarioArmazenado(TypedDict):
    email: str
    senha_hash: str
    perfil: PerfilAcesso


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
}


def buscar_usuario_por_email(email: str) -> UsuarioArmazenado | None:
    """Retorna uma conta de demonstração pelo e-mail, se estiver cadastrada."""
    return _USUARIOS_POR_EMAIL.get(email)
