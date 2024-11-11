from decimal import Decimal
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

# Caminho do arquivo de configuração
caminho_config = 'D:\\G3\\Cliente\\Servidor.conf'

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

# Seleciona os registros que atendem às condições especificadas
cur.execute(""" --sql
    SELECT COD_FIN, VALOR_A_AMORTIZAR FROM LANC_FINANCEIRO
    WHERE COD_PLANO_CONTA = 122 AND COD_FORNECEDOR = 15 AND 
    ATV_LANC_FINANCEIRO = 'V' AND COD_SITUACAO_TITULO = 1 AND 
    COD_FIN < 2393 AND COD_FIN > 1156 ORDER BY COD_FIN;
""")

# Lista para armazenar os registros
registros = cur.fetchall()

# Verifica se existem registros e realiza o update
if registros:
    valor_anterior = registros[0][1] # Valor do primeiro registro

    for registro in registros[1:]: # Começa do segundo registro
        novo_valor = valor_anterior + Decimal('0.50')  # Converte 0.50 para Decimal
        cur.execute(""" --sql
            UPDATE LANC_FINANCEIRO 
            SET VALOR_A_AMORTIZAR = ?
            WHERE COD_FIN = ?;
        """, (novo_valor, registro[0]))
        valor_anterior = novo_valor

    # Commit das alterações
    conn.commit()

# Fecha as conexões
cur.close()
conn.close()
