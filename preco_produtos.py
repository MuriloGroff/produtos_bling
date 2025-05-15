import requests
import json
import mysql.connector
from datetime import datetime
import base64
import time
import os

token_file = "tokens.json"
token_file_id = "refresh_token.json"
token_file_secret = "refresh_token.json"

token_file = os.path.join(os.getcwd(), "Autorizações", "tokens.json")
token_file_id = os.path.join(os.getcwd(), "Autorizações", "refresh_token.json")
token_file_secret = os.path.join(os.getcwd(), "Autorizações", "refresh_token.json")


def get_tokens():
    try:
        with open(token_file, "r") as f:
            tokens = json.load(f)
        return tokens
    except FileNotFoundError:
        return None

def save_tokens(tokens):
    with open(token_file, "w") as f:
        json.dump(tokens, f)

def renovar_token(refresh_token):
    credenciais = f"{client_id}:{client_secret}"
    credenciais_base64 = base64.b64encode(credenciais.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "1.0",
        "Authorization": f"Basic {credenciais_base64}"
    }

    dados = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post("https://api.bling.com.br/Api/v3/oauth/token", headers=headers, data=dados)

    if response.status_code == 200:
        token_info = response.json()
        save_tokens(token_info)
        return token_info["access_token"], token_info["refresh_token"]
    else:
        print("Erro ao atualizar o Access Token:", response.status_code)
        print("Resposta recebida:", response.text)
        return None, None

def atualizar_headers(access_token):
    global headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

# Iniciar o processo de renovação de token e atualização de headers
tokens = get_tokens()

if tokens:
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Testando se o token ainda é válido antes da requisição
    test_response = requests.get("https://api.bling.com.br/v3/produtos?pagina=1&limite=1", headers={"Authorization": f"Bearer {access_token}"})

    if test_response.status_code == 401:  # Token expirado
        print("Token expirado, renovando...")
        access_token, refresh_token = renovar_token(refresh_token)
        if access_token:
            atualizar_headers(access_token)
        else:
            print("Erro ao renovar o token, encerrando execução.")
            exit()
    else:
        atualizar_headers(access_token)
else:
    print("Arquivo de tokens não encontrado ou vazio. É necessário obter um novo authorization code.")
    exit()

# Conectando ao banco de dados
# Carregar as credenciais do arquivo JSON
db_config_file = os.path.join(os.getcwd(), "Autorizações", "db_config.json")

with open(db_config_file, "r") as f:
    db_config = json.load(f)

cnx = mysql.connector.connect(
host=db_config["host"],
user=db_config["user"],
password=db_config["password"],
database=db_config["database"],
)

cursor = cnx.cursor()

# Recuperar o ID máximo já presente na tabela
cursor.execute("SELECT MAX(id) FROM produtos_2")
resultado = cursor.fetchone()
max_id_atual = resultado[0] if resultado[0] else 0

pular_pagina = 1

try:
    while True:
        response = requests.get(f"https://api.bling.com.br/v3/produtos?pagina={pular_pagina}&limite=200", headers=headers)
        if response.status_code == 429: #Excedeu o limite de requisições
            print("Limite de requisições excedido, aguardando 1 segundo...")
            time.sleep(1)
            continue
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            print("Resposta recebida:", response.text)
            break

        try:
            informacoes = response.json()
            print(f"Requisição bem-sucedida para a página {pular_pagina}")
        except ValueError:
            print(f"Erro ao decodificar JSON: {response.text}")
            break

        if len(informacoes['data']) < 1:
            print("Nenhum dado encontrado na página, encerrando.")
            break

        for item in informacoes['data']:
            id_do_item = item['id']
            response_item = requests.get(f"https://api.bling.com.br/v3/produtos/{id_do_item}", headers=headers)

            if response_item.status_code == 401:  # Token expirado durante a requisição
                print(f"Token expirado ao buscar item {id_do_item}, renovando...")
                access_token, refresh_token = renovar_token(refresh_token)
                if access_token:
                    atualizar_headers(access_token)
                    response_item = requests.get(f"https://api.bling.com.br/v3/produtos/{id_do_item}", headers=headers)
                else:
                    print("Erro ao renovar o token, ignorando item.")
                    continue

            if response_item.status_code != 200:
                print(f"Erro na requisição para o item {id_do_item}: {response_item.status_code}")
                continue

            try:
                informacoes_item = response_item.json()
            except ValueError:
                print(f"Erro ao decodificar JSON do item {id_do_item}: {response_item.text}")
                continue

            # Extraindo informações do produto
            nome = informacoes_item['data'].get('nome', 'Desconhecido')
            codigo = informacoes_item['data'].get('codigo', 'Desconhecido')
            preco = informacoes_item['data'].get('preco', 0.0)
            preco_custo = informacoes_item['data'].get('fornecedor', {}).get('precoCusto', 0.0)
            saldo_virtual = informacoes_item['data'].get('estoque', {}).get('saldoVirtualTotal', 0)
            peso_liquido = informacoes_item['data'].get('pesoLiquido', 0.0)
            estoque_minimo = informacoes_item['data'].get('estoque', {}).get('minimo', 0)
            altura = informacoes_item['data'].get('dimensoes', {}).get('altura', 0.0)
            largura = informacoes_item['data'].get('dimensoes', {}).get('largura', 0.0)
            profundidade = informacoes_item['data'].get('dimensoes', {}).get('profundidade', 0.0)
            fornecedor_nome = informacoes_item['data'].get('fornecedor', {}).get('contato', {}).get('nome', 'Desconhecido')
            # Obtendo os dados da estrutura
            estrutura = informacoes_item['data'].get('estrutura', {})

            # Verificar se a lista 'componentes' tem elementos
            componentes = estrutura.get('componentes', [])

            if componentes:
                # Se existir, pega o primeiro componente e extrai o produto_id
                primeiro_componente = componentes[0]
                produto_id = primeiro_componente.get('produto', {}).get('id', None)
                quantidade = primeiro_componente.get('quantidade', 0)
                
            else:
                # Se não houver componentes, apenas segue sem definir produto_id
                produto_id = None  # Define um valor seguro quando não há componentes
                quantidade = 0

            # Definir tipoEstoque, permitindo valores vazios
            tipo_estoque = estrutura.get('tipoEstoque', None)


            if preco_custo == 0.0:
                print(f"Atenção: precoCusto está {preco_custo} para o item ID: {id_do_item}")

            # Inserindo dados na nova tabela de produtos
            cursor.execute('''
                INSERT INTO produtos_2 (id, nome, codigo, preco, precoCusto, saldoVirtualTotal, pesoLiquido, estoqueMinimo, altura, largura, profundidade, fornecedorNome, tipoEstoque, produto_id, quantidade)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE nome=VALUES(nome), codigo=VALUES(codigo), preco=VALUES(preco), precoCusto=VALUES(precoCusto), saldoVirtualTotal=VALUES(saldoVirtualTotal), pesoLiquido=VALUES(pesoLiquido), estoqueMinimo=VALUES(estoqueMinimo), altura=VALUES(altura), largura=VALUES(largura), profundidade=VALUES(profundidade), fornecedorNome=VALUES(fornecedorNome), tipoEstoque=VALUES(tipoEstoque), produto_id=VALUES(produto_id), quantidade=VALUES(quantidade);
            ''', (id_do_item, nome, codigo, preco, preco_custo, saldo_virtual, peso_liquido, estoque_minimo, altura, largura, profundidade, fornecedor_nome, tipo_estoque, produto_id if produto_id else None, quantidade if quantidade else 0))

           
            cursor.execute("SELECT preco FROM historico_precos WHERE produto_sku = %s ORDER BY id DESC LIMIT 1", (codigo,))
            resultado = cursor.fetchone()
            preco_anterior = float(resultado[0] if resultado else None)
            # print(f"Preço anterior para o produto {codigo}: {preco_anterior}")

            if preco_anterior is None or preco_anterior != float(preco_custo):
                # print(f"Preço mudou para o produto {codigo}: {preco_custo}")

                cursor.execute('''
                INSERT INTO historico_precos (produto_sku, data_alteracao, preco)
                VALUES (%s, %s, %s)
            ''', (codigo, datetime.now().date(), preco_custo))
            # print(f"Preço atualizado para o produto {codigo}: {preco_custo}")

        # Confirmar as alterações a cada página processada
        cnx.commit()
        print(f"Alterações confirmadas para a página {pular_pagina}")
        pular_pagina += 1  # Ir para a próxima página
        time.sleep(4)  # Aguardar 4 segundos entre as solicitações para evitar erro 429

finally:
    cursor.close()
    cnx.close()
    print("Conexão encerrada.")
    total_processado = (pular_pagina - 1) * 100 + (len(informacoes['data']) if 'data' in informacoes else 0)
    print(f"Total de produtos processados: {total_processado}")
    print("Processo concluído com sucesso.")          