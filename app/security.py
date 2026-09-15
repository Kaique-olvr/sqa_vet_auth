import bcrypt
# A função bcrypt só funciona com dados em bytes. Por isso as conversões foram feitas

def gerar_hash_senha(senha_original: str) -> str:

    '''Função responsável pelo hashing da senha digitada pelo usuário.
       Retorna o hash em str para armazenamento'''

    senha_bytes = senha_original.encode('utf-8') # Converte a senha digitada para bytes 'utf-8'
    salt = bcrypt.gensalt() # Gera um salt (sequencia aleatoria para gerar hashes únicos)
    hash_bytes = bcrypt.hashpw(senha_bytes, salt) # Faz o hashing utilizando a senha em bytes e o salt
    hash_senha = hash_bytes.decode('utf-8') # Converte o texto em bytes para Str de volta
    return hash_senha # Retorna o hash em str

def verificar_senha(senha_original: str, hash_senha: str) -> bool:

    '''Verifica se a senha digitada corresponde com o hash salvo.
       Retorna um valor Booleano'''

    senha_bytes = senha_original.encode('utf-8') # Transforma a senha digitada em bytes
    hash_senha = hash_senha.encode('utf-8') # Transforma o hash da senha salva em bytes
    return bcrypt.checkpw(senha_bytes, hash_senha) # Compara o bytes da senha digitada e do hash salvo e retorna um booleano 