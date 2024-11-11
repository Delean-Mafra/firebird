import re
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

# Lendo o arquivo de texto
with open('holerite.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

def get_update_statements(lines, cod_fin):
    updates = []
    for line in lines:
        data = re.split(r'\s+', line.strip())  # divide a linha em campos
        if len(data) > 1 and data[0] == '2':
            if data[1] == 'DESC.MENSALIDADE PLANO' and len(data) >= 5:
                updates.append(f"UPDATE RETENCAO_TITULO SET VALOR_RETIDO = {data[4].replace(',', '.')}, VALOR_BASE = {data[4].replace(',', '.')} WHERE COD_FIN = {cod_fin} AND COD_IMPOSTO = 25")
            elif data[1] == 'INSS' and len(data) >= 5:
                valor_base_lines = [re.split(r'\s+', line.strip())[1] for line in lines if line.startswith('BASE INSS')]
                if valor_base_lines:  # verifica se a lista não está vazia
                    valor_base = valor_base_lines[0].replace(',', '.')
                    updates.append(f"UPDATE RETENCAO_TITULO SET COD_FIN = {cod_fin}, VALOR_RETIDO = {data[4].replace(',', '.')}, VALOR_BASE = {valor_base} WHERE COD_FIN = {cod_fin} AND COD_IMPOSTO = 7")
            elif data[1] == 'IRRF' and len(data) >= 5:
                valor_base_lines = [re.split(r'\s+', line.strip())[1] for line in lines if line.startswith('BASE IRRF')]
                if valor_base_lines:  # verifica se a lista não está vazia
                    valor_base = valor_base_lines[0].replace(',', '.')
                    updates.append(f"UPDATE RETENCAO_TITULO SET VALOR_RETIDO = {data[4].replace(',', '.')}, VALOR_BASE = {valor_base}, COD_IMPOSTO = 4 WHERE COD_FIN = {cod_fin} AND COD_IMPOSTO = 4")
    return updates

# Solicitando o número do título ao usuário
numero_titulo = input("Digite o número do título que deseja atualizar: ")

# Obtendo os statements de update
update_statements = get_update_statements(lines, numero_titulo)

# Executando os updates no banco de dados
for query in update_statements:
    c.execute(f"\n{query}")

# Confirmando as transações
conn.commit()
conn.close()

print("Updates realizados com sucesso!")
