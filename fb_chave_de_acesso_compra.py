import fdb
from datetime import datetime

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
DIR_DADOS = config['DIR_DADOS']
USUARIO_BD = config['USUARIO_BD']
SENHA_BD = config['SENHA_BD']
SERVER = config['SERVER']

# Conectar ao banco de dados
try:
    conn = fdb.connect(
        host=SERVER,
        database=DIR_DADOS,
        user=USUARIO_BD,
        password=SENHA_BD
    )
    c = conn.cursor()

    c.execute("""  
              --sql
        SELECT C.NFE_CHAVE_ACESSO, G.NOME_FORNECEDOR, C.DATA_COMPRA
        FROM COMPRA C
        LEFT JOIN GERFORNECEDOR G ON C.COD_FORNECEDOR = G.COD_FORNECEDOR
        WHERE C.MODELO_NF = '65'
        AND C.NFE_CHAVE_ACESSO IS NOT NULL
        ORDER BY C.DATA_COMPRA DESC
        ;
    """)

    # Obter todos os resultados
    results = c.fetchall()

    # Formatar os resultados
    formatted_results = []
    for row in results:
        formatted_date = row[2].strftime('%d/%m/%Y')
        formatted_row = f"{row[0]};{row[1]};{formatted_date}"
        formatted_results.append(formatted_row)

    # Exibir os resultados formatados
    for result in formatted_results:
        print(result)

finally:
    c.close()
    conn.close()
