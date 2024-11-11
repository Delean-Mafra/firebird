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

saida_consumo = input('Digite o codigo da saida para consumo: ')
c = conn.cursor()

# Definindo a consulta de atualização
update_query = f"""
--sql
UPDATE SAIDA_CONSUMO_ITEM SCI
SET SCI.QUANTIDADE = (
    SELECT A.SALDO_ATUAL
    FROM ALMMATERIAL A
    WHERE A.COD_MATERIAL = SCI.COD_MATERIAL
)
WHERE SCI.COD_SAIDA_CONSUMO = {saida_consumo};
"""

# Executando a consulta de atualização
c.execute(update_query)

# Confirmando as alterações
conn.commit()

print("Atualização concluída com sucesso!")
