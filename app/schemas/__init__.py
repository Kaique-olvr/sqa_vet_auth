"""
Camada de Schemas (Contratos de Dados com Pydantic).

Objetivo:
- Validar os dados recebidos nas requisições (ex: formato de e-mail, tamanho mínimo de senha).
- Filtrar e definir quais campos a API pode devolver nas respostas, evitando expor dados sensíveis como senhas ou hashes.

"""