import fdb
import pandas as pd
from dateutil import parser
import warnings

# Suprimir avisos de FutureWarning e UserWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Filtrar especificamente os avisos do openpyxl
def custom_warning_filter(message, category, filename, lineno, file=None, line=None):
    if 'openpyxl' in filename:
        return
    else:
        return warnings.showwarning(message, category, filename, lineno, file, line)

warnings.showwarning = custom_warning_filter

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
        data = parser.parse(str(data_str), dayfirst=True)
        return data.strftime('%d/%m/%Y')
    except:
        return str(data_str)

# Lendo o arquivo .xlsx
df_xlsx = pd.read_excel('Extrato_conta_bb.xlsx')

# Convertendo a coluna "Valor" para números
df_xlsx['Valor'] = df_xlsx['Valor'].str.replace('.', '').str.replace(',', '.').astype(float)

# Ajustando os valores do DataFrame do XLSX
df_xlsx['Valor'] = df_xlsx.apply(
    lambda row: -row['Valor'] if row['Tipo Lançamento'] == 'Saída' else row['Valor'],
    axis=1
)

# Removendo datas inválidas e convertendo as datas
df_xlsx = df_xlsx[df_xlsx['Data'] != '00/00/0000']
df_xlsx['Data'] = df_xlsx['Data'].apply(converter_data)

def verificar_registro(data, valor, tipo):
    # Ignorando registros com datas inválidas
    if pd.isna(data) or pd.isna(valor):
        return True
    
    valor_abs = abs(valor)
    tipo_lancamento = 'D' if valor < 0 else 'C'
    
    query = """
    --sql
    SELECT *
    FROM LANC_CONTA_FIN LCF
    WHERE LCF.DATA_DISPONIVEL = ?
    AND LCF.COD_CONTA_FINANCEIRA = 25
    AND LCF.VALOR_LANCAMENTO_CONTA = ?
    AND LCF.TIPO_LANCAMENTO_CONTA IN ('D','C')
    """
    
    data_formato_db = parser.parse(data, dayfirst=True).strftime('%d.%m.%Y')
    cur.execute(query, (data_formato_db, valor_abs, tipo_lancamento))
    result = cur.fetchone()
    
    return result is not None

# Verificando os registros que não coincidem
nao_conciliados = df_xlsx[~df_xlsx.apply(lambda row: verificar_registro(row['Data'], row['Valor'], row['Tipo Lançamento']), axis=1)]

# Formatando os valores
nao_conciliados.loc[:, 'Valor'] = nao_conciliados['Valor'].apply(lambda x: f"{abs(x):,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))

# Exibindo os resultados
print("Registros não conciliados:")
print(nao_conciliados[['Data', 'Valor', 'Tipo Lançamento']])

# Verificando os registros conciliados
conciliados = df_xlsx[df_xlsx.apply(lambda row: verificar_registro(row['Data'], row['Valor'], row['Tipo Lançamento']), axis=1)]

# Formatando os valores para os conciliados
conciliados.loc[:, 'Valor'] = conciliados['Valor'].apply(lambda x: f"{abs(x):,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))

print("\nRegistros conciliados:")
print(conciliados[['Data', 'Valor', 'Tipo Lançamento']])

# Fechar a conexão com o banco de dados
conn.close()
