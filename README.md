# 🛒 Integração com a API do Bling para Gerenciamento de Produtos

Este repositório contém um script Python que integra a API do Bling para buscar e armazenar informações detalhadas de produtos em um banco de dados MySQL. O foco principal é a tabela `produtos_2`, que organiza os dados de produtos de forma estruturada.

## 🛠️ Funcionalidades

### Autenticação com a API do Bling
- Utiliza o fluxo OAuth 2.0 para autenticação.
- Renova automaticamente o token de acesso quando necessário.

### Busca de Produtos
- Realiza a busca de produtos com suporte à paginação.
- Obtém informações detalhadas de cada produto, incluindo preço, estoque, dimensões e fornecedor.

### Armazenamento no Banco de Dados
- Insere ou atualiza os dados de produtos na tabela `produtos_2`.
- Garante que os dados sejam consistentes com a cláusula `ON DUPLICATE KEY UPDATE`.

### Histórico de Preços
- Monitora alterações nos preços dos produtos e registra as mudanças em uma tabela de histórico.

### Tratamento de Erros
- Lida com erros de requisição, como limite de requisições excedido (`429`) e token expirado (`401`).
- Implementa tentativas automáticas para garantir a continuidade do processo.

---

## 🧩 Estrutura do Código

### 1️⃣ Autenticação
O script utiliza um arquivo JSON para armazenar os tokens de acesso e renovação. Caso o token expire, ele é renovado automaticamente.  
![Autenticação](https://github.com/user-attachments/assets/1795ff72-38c5-48f5-b9fe-35028c547328)

### 2️⃣ Busca de Produtos
A função realiza a busca de produtos com suporte à paginação. Para cada produto, uma requisição adicional é feita para obter detalhes completos.

```python
response = requests.get(f"https://api.bling.com.br/v3/produtos?pagina={pular_pagina}&limite=100", headers=headers)
```

3️⃣ Armazenamento no Banco de Dados
Os dados são armazenados na tabela produtos_2 com controle de duplicidade.
```
INSERT INTO produtos_2 (id, nome, codigo, preco, precoCusto, saldoVirtualTotal, pesoLiquido, estoqueMinimo, altura, largura, profundidade, fornecedorNome, tipoEstoque, produto_id, quantidade)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE ...
```
4️⃣ Histórico de Preços
O código verifica alterações nos preços dos produtos e registra as mudanças em uma tabela de histórico.
```
INSERT INTO historico_precos (produto_sku, data_alteracao, preco)
VALUES (%s, %s, %s)
```

## 🗂️ Estrutura das Tabelas

### 📌 Tabela `produtos_2`
| Coluna             | Tipo      | Descrição                     |
|-------------------|---------|-----------------------------|
| `id`             | BIGINT   | ID do produto               |
| `nome`           | VARCHAR  | Nome do produto             |
| `codigo`         | VARCHAR  | Código do produto           |
| `preco`          | FLOAT    | Preço de venda              |
| `precoCusto`     | FLOAT    | Preço de custo              |
| `saldoVirtualTotal` | INT  | Saldo virtual total         |
| `pesoLiquido`    | FLOAT    | Peso líquido                |
| `estoqueMinimo`  | INT      | Estoque mínimo              |
| `altura`         | FLOAT    | Altura do produto           |
| `largura`        | FLOAT    | Largura do produto          |
| `profundidade`   | FLOAT    | Profundidade                |
| `fornecedorNome` | VARCHAR  | Nome do fornecedor          |
| `tipoEstoque`    | VARCHAR  | Tipo de estoque             |
| `produto_id`     | BIGINT   | ID do produto na estrutura  |
| `quantidade`     | INT      | Quantidade na estrutura     |

### 📌 Tabela `historico_precos`
| Coluna          | Tipo    | Descrição                    |
|---------------|--------|----------------------------|
| `produto_sku`  | VARCHAR | Código do produto          |
| `data_alteracao` | DATE  | Data da alteração          |
| `preco`        | FLOAT   | Preço do produto           |

---

## 🔧 Tecnologias Utilizadas

- **Python**: Linguagem principal para desenvolvimento do script.
- **MySQL**: Banco de dados relacional para armazenamento das informações.
- **API do Bling**: Fonte de dados para produtos.

### 📌 Bibliotecas Python:
- `requests`: Para realizar requisições HTTP.
- `mysql.connector`: Para conexão e manipulação do banco de dados.
- `json`: Para manipulação de dados JSON.
- `time`: Para controle de tempo entre requisições.

---

## 🛡️ Tratamento de Erros

### Erro `429` (Limite de Requisições)
- O código aguarda **1 segundo** antes de tentar novamente.

### Erro `401` (Token Expirado)
- O token é renovado automaticamente e a requisição é refeita.

### Erros de Conexão
- São realizadas **até 3 tentativas** antes de abortar a operação.

---

## 📈 Resultados
- **Automação Completa**: Busca e armazenamento de dados de produtos de forma automatizada.
- **Escalabilidade**: Suporte à paginação para processamento de grandes volumes de dados.
- **Confiabilidade**: Tratamento de erros para garantir a continuidade do processo.

---

## 📌 Como Executar

### Configurar o Banco de Dados
1. Crie as tabelas `produtos_2` e `historico_precos` no MySQL.
2. Certifique-se de que as colunas estão definidas corretamente.

### Configurar Tokens de Acesso
- Salve os tokens de acesso e renovação no arquivo `tokens.json`.

### Executar o Script
1. Certifique-se de que todas as dependências estão instaladas.
2. Execute o script Python.

### Verificar os Resultados
- Os dados serão armazenados na tabela `produtos_2`.
- O histórico de preços será atualizado automaticamente.

---

## 🌟 Destaques
- **Integração com API RESTful**: Demonstra como extrair APIs externas de forma eficiente.
- **Armazenamento Estruturado**: Uso do MySQL para organizar e persistir os dados.
- **Automação e Escalabilidade**: Processamento contínuo com suporte a grandes volumes de dados.

---

## 💡 Conclusão
Este projeto é um exemplo prático de como integrar APIs externas com bancos de dados para criar soluções inteligentes e escaláveis. Ele pode ser adaptado para diferentes cenários, como gestão de estoque, análise de produtos e muito mais.

Se você gostou deste projeto ou tem sugestões, deixe seu feedback! 🚀

