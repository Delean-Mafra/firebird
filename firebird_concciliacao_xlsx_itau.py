import fdb
import pandas as pd
from dateutil import parser
import warnings
import os

# Suprimir avisos de FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

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

# Conectando ao banco de dados
conn = fdb.connect(
    host=HOST,
    database=DATABASE,
    user=USER,
    password=PASSWORD
)

# Cursor para executar as queries
cur = conn.cursor()

# Função para converter a data
def converter_data(data_str):
    if pd.isna(data_str):
        return pd.NaT
    try:
        # Considerando o formato correto mês/dia/ano
        data = parser.parse(str(data_str), dayfirst=False)
        return data.strftime('%d/%m/%Y')
    except:
        return str(data_str)

# Verificar o caminho do arquivo
arquivo_excel = 'Extrato_conta_itau.xlsx'
if not os.path.exists(arquivo_excel):
    print(f"Arquivo '{arquivo_excel}' não encontrado.")
    print("Diretório atual:", os.getcwd())
    arquivo_excel = input("Por favor, insira o caminho completo do arquivo Excel: ")

# Lendo o arquivo .xlsx
df_xlsx = pd.read_excel(arquivo_excel)

# Convertendo a coluna "Valor" para números (float), mantendo o sinal negativo para saídas
df_xlsx['Valor'] = df_xlsx.apply(
    lambda row: -float(row['Valor']) if row['Tipo Lançamento'] == 'Saida' else float(row['Valor']),
    axis=1
)

# Removendo datas inválidas e convertendo as datas
df_xlsx = df_xlsx[df_xlsx['Data'] != '00/00/0000']
df_xlsx['Data'] = df_xlsx['Data'].apply(converter_data)

def verificar_registro(data, valor, tipo):
    if pd.isna(data) or pd.isna(valor):
        return False, "Data ou valor inválido"
    
    valor_abs = abs(valor)
    tipo_lancamento = 'D' if tipo == 'Saida' else 'C'
    
    query = """--sql
    SELECT *
    FROM LANC_CONTA_FIN LCF
    WHERE LCF.DATA_DISPONIVEL = ?
    AND LCF.COD_CONTA_FINANCEIRA = 30
    AND LCF.VALOR_LANCAMENTO_CONTA = ?
    AND LCF.TIPO_LANCAMENTO_CONTA = ?;
    """
    
    # Corrigindo o formato de data para o banco de dados
    data_formato_db = parser.parse(data, dayfirst=False).strftime('%m.%d.%Y')
    cur.execute(query, (data_formato_db, valor_abs, tipo_lancamento))
    result = cur.fetchone()
    
    if result:
        return True, "Registro encontrado"
    else:
        return False, f"Não encontrado: Data={data_formato_db}, Valor={valor_abs}, Tipo={tipo_lancamento}"

# Função para formatar o valor (sem pontos de milhar)
def formatar_valor(valor):
    return f"{abs(valor):.2f}".replace('.', ',')

# Verificando os registros
resultados = df_xlsx.apply(lambda row: verificar_registro(row['Data'], row['Valor'], row['Tipo Lançamento']), axis=1)
df_xlsx['Conciliado'], df_xlsx['Motivo'] = zip(*resultados)

# Formatando os valores
df_xlsx['Valor Formatado'] = df_xlsx['Valor'].apply(formatar_valor)

# Exibindo os resultados não conciliados
nao_conciliados = df_xlsx[~df_xlsx['Conciliado']]
print("Registros não conciliados:")
print(nao_conciliados[['Data', 'Valor Formatado', 'Tipo Lançamento', 'Motivo']])

# Exibindo os resultados conciliados
conciliados = df_xlsx[df_xlsx['Conciliado']]
print("\nRegistros conciliados:")
print(conciliados[['Data', 'Valor Formatado', 'Tipo Lançamento']])

# Fechar a conexão com o banco de dados
conn.close()
