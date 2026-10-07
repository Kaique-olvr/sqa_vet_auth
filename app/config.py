import os # Biblioteca para uso de variaveis de ambiente
from dotenv import load_dotenv # Biblioteca para carregar variaveis de ambiente do arquivo .env

'''Centraliza todas as configurações do sistema em um único lugar.
   Os outros módulos (ex: security.py) importam daqui em vez de lerem o .env por conta própria.
'''

load_dotenv() # Carrega as variaveis de ambiente do arquivo .env

CHAVE_PADRAO_DESENVOLVIMENTO = "chave_secreta_padrao_para_desenvolvimento_local" # Chave usada SOMENTE quando estamos rodando localmente (development)

def carregar_secret_key(environment: str, secret_key: str | None) -> str:

    '''Decide qual chave secreta será usada para assinar os tokens JWT.
       - Em "development": se não tiver SECRET_KEY no .env, usa a chave padrão (facilita rodar local).
       - Em qualquer outro ambiente (ex: "production"): a SECRET_KEY é OBRIGATÓRIA.
         Se não existir, a aplicação nem sobe, evitando assinar tokens com uma chave pública que está no código.
       Retorna a chave em str'''

    if secret_key: # Se a chave foi definida no .env, usa ela em qualquer ambiente
        return secret_key

    if environment == "development": # Sem chave definida, mas rodando local: libera a chave padrão
        return CHAVE_PADRAO_DESENVOLVIMENTO

    # Sem chave definida fora do ambiente de desenvolvimento: trava a aplicação com um erro claro
    raise RuntimeError(f"SECRET_KEY não definida para o ambiente '{environment}'. Configure a variável no arquivo .env")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development") # Fase atual do software, caso não exista, considera que está em desenvolvimento

SECRET_KEY = carregar_secret_key(ENVIRONMENT, os.getenv("SECRET_KEY")) # Chave secreta que assina os tokens JWT
ALGORITHM = "HS256" # Algoritmo de criptografia para o token JWT

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)) # Tempo de expiração do token, caso nao exista no .env, usa um valor padrão de 60 minutos
