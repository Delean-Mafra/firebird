import fdb
from decimal import Decimal

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

# Cursor para executar as queries
cur = conn.cursor()

# Parte 1: Identificar as compras com discrepância
cur.execute("""
--sql
SELECT 
    C.COD_COMPRA,
    C.VALOR_DESCONTO_TOTAL,
    SUM(CI.VALOR_DESCONTO_ITEM) AS SOMA_DESCONTO_ITENS,
    COUNT(*) AS QUANTIDADE_ITENS
FROM COMPRA C
JOIN COMPRA_ITEM CI ON C.COD_COMPRA = CI.COD_COMPRA
WHERE C.COD_NATUREZA_OPER IN (34, 36, 39, 40, 41, 42)
GROUP BY C.COD_COMPRA, C.VALOR_DESCONTO_TOTAL
HAVING ABS(C.VALOR_DESCONTO_TOTAL - SUM(CI.VALOR_DESCONTO_ITEM)) > 0.00;
""")

compras_com_discrepancia = cur.fetchall()

# Parte 2: Atualizar os valores de desconto dos itens
for compra in compras_com_discrepancia:
    cod_compra = compra[0]
    valor_desconto_total = compra[1]
    quantidade_itens = compra[3]
    desconto_por_item = valor_desconto_total / quantidade_itens

    cur.execute("""
    --sql
    UPDATE COMPRA_ITEM
    SET VALOR_DESCONTO_ITEM = ?
    WHERE COD_COMPRA = ?;
    """, (desconto_por_item, cod_compra))

# Commit the transaction
conn.commit()

# Fechar a conexão
cur.close()
conn.close()

print("Atualização concluída com sucesso.")
