import fdb
from datetime import datetime
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

# Função para calcular a data de competência correta
def calcular_data_competencia(data_vencimento):
    if data_vencimento is None:
        return None
    # Converte a data de vencimento para string no formato esperado
    data_vencimento_str = data_vencimento.strftime('%d.%m.%Y %H:%M')
    data_vencimento = datetime.strptime(data_vencimento_str, '%d.%m.%Y %H:%M')
    mes_anterior = data_vencimento.month - 1 if data_vencimento.month > 1 else 12
    ano = data_vencimento.year if mes_anterior != 12 else data_vencimento.year - 1
    return f"{mes_anterior:02d}/{ano}"

# Conectar ao banco de dados
try:
    conn = fdb.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )
    c = conn.cursor()

    # Selecionar todos os registros da tabela LANC_FINANCEIRO
    c.execute("""  --sql
        SELECT COD_FIN, DATA_VENCIMENTO, DATA_COMPETENCIA 
        FROM LANC_FINANCEIRO
        WHERE ATV_LANC_FINANCEIRO = 'V'
        ;
    """)
    import pyperclip

    # Iterar sobre os registros e verificar se a data de competência está correta
    for row in c.fetchall():
        cod_fin, data_vencimento, data_competencia = row
        data_competencia_correta = calcular_data_competencia(data_vencimento)

        if data_competencia_correta is None:
            print(f"Registro {cod_fin} tem data de vencimento nula.")
        elif data_competencia != data_competencia_correta:
            #print(f"Registro {cod_fin} tem data de competência incorreta. Atual: {data_competencia}, Correta: {data_competencia_correta}")
            print(f"{cod_fin},")

finally:
    # Fechar a conexão
    c.close()
    conn.close()

print("Verificação concluída com sucesso!")
