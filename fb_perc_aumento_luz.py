import fdb

print("Copyright ©2024 | Delean Mafra, todos os direitos reservados.")

# Função para ler o arquivo de configuração
def ler_configuracao(caminho_arquivo):
    configuracoes = {}
    chaves_necessarias = {'USUARIO_BD', 'SENHA_BD', 'DIR_DADOS', 'SERVER'}
    with open(caminho_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if (linha.startswith('I ') or linha.startswith('//I ')):
                chave_valor = linha[2:].strip() if linha.startswith('I ') else linha[4:].strip()
                chave, valor = chave_valor.split('=')
                if chave in chaves_necessarias:
                    configuracoes[chave] = valor
    return configuracoes

print("Copyright ©2024 | Delean Mafra, todos os direitos reservados.")


# Caminho do arquivo de configuração
caminho_config = input('Digite o caminho do seu arquivo de configuração: ') #.conf

# Ler configurações do arquivo
config = ler_configuracao(caminho_config)

# Configurações do banco de dados
DATABASE = config['DIR_DADOS']
USER = config['USUARIO_BD']
PASSWORD = config['SENHA_BD']
HOST = config['SERVER']

# Conectar ao banco de dados
conn = fdb.connect(
    host=HOST,
    database=DATABASE,
    user=USER,
    password=PASSWORD
)
c = conn.cursor()

# Execute sua consulta original
c.execute("""
--sql
SELECT 
    Z.DATA_PAGAMENTO,
    Z.VALOR_PAGO,
    (Z.VALOR_PAGO - (
        SELECT FIRST 1 Z2.VALOR_PAGO
        FROM LANC_FINANCEIRO Z2
        LEFT JOIN GERFORNECEDOR GER2 ON Z2.COD_FORNECEDOR = GER2.COD_FORNECEDOR
        WHERE GER2.NOME_FORNECEDOR LIKE '%CELESC%'
        AND Z2.DATA_PAGAMENTO > '2023-12-01'
        ORDER BY Z2.DATA_PAGAMENTO
    )) AS AUMENTO_RS,
    CASE 
        WHEN (
            SELECT FIRST 1 Z2.VALOR_PAGO
            FROM LANC_FINANCEIRO Z2
            LEFT JOIN GERFORNECEDOR GER2 ON Z2.COD_FORNECEDOR = GER2.COD_FORNECEDOR
            WHERE GER2.NOME_FORNECEDOR LIKE '%CELESC%'
            AND Z2.DATA_PAGAMENTO > '2023-12-01'
            ORDER BY Z2.DATA_PAGAMENTO
        ) > 0 THEN
            CAST(
                ROUND(((Z.VALOR_PAGO - (
                    SELECT FIRST 1 Z2.VALOR_PAGO
                    FROM LANC_FINANCEIRO Z2
                    LEFT JOIN GERFORNECEDOR GER2 ON Z2.COD_FORNECEDOR = GER2.COD_FORNECEDOR
                    WHERE GER2.NOME_FORNECEDOR LIKE '%CELESC%'
                    AND Z2.DATA_PAGAMENTO > '2023-12-01'
                    ORDER BY Z2.DATA_PAGAMENTO
                )) / (
                    SELECT FIRST 1 Z2.VALOR_PAGO
                    FROM LANC_FINANCEIRO Z2
                    LEFT JOIN GERFORNECEDOR GER2 ON Z2.COD_FORNECEDOR = GER2.COD_FORNECEDOR
                    WHERE GER2.NOME_FORNECEDOR LIKE '%CELESC%'
                    AND Z2.DATA_PAGAMENTO > '2023-12-01'
                    ORDER BY Z2.DATA_PAGAMENTO
                )) * 100, 2) AS DECIMAL(18, 2)) || '%' -- Arredondando o percentual para duas casas decimais antes de adicionar o símbolo de percentual
        ELSE '0%'
    END AS PERCENTUAL
FROM 
    LANC_FINANCEIRO Z
LEFT JOIN 
    GERFORNECEDOR GER ON Z.COD_FORNECEDOR = GER.COD_FORNECEDOR
WHERE 
    GER.NOME_FORNECEDOR LIKE '%CELESC%'
    AND Z.DATA_PAGAMENTO > '2023-12-01';
"""
)
rows = c.fetchall()

# Calcule o aumento em R$ e o aumento percentual
dezembro_valor = rows[0][1]
for i in range(1, len(rows)):
    aumento_rs = rows[i][1] - dezembro_valor
    aumento_percentual = (aumento_rs / dezembro_valor) * 100
    aumento_percentual_formatado = "{:.2f}%".format(aumento_percentual)
    data_pagamento_formatada = rows[i][0].strftime("%d/%m/%Y")
    print(f"Data pag: {data_pagamento_formatada}, Valor: {rows[i][1]}, Aumento R$: {aumento_rs}, Percentual de Aumento: {aumento_percentual_formatado}")

# Fechar a conexão com o banco de dados
conn.close()
