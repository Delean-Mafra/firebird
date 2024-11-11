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

cod_compra = input('Digite o codigo da compra: ')
c = conn.cursor()

# Inserir itens da última compra antes da compra especificada
insert_query = f"""
--sql
INSERT INTO COMPRA_ITEM (
    COD_COMPRA,
    PERCENTUAL_ICMS_ITEM,
    VALOR_ICMS,
    VALOR_OT_DESP_ITEM_FECH_NF,
    PERC_SEGURO_ITEM_FECH_NF,
    VALOR_SEGURO_ITEM_FECH_NF,
    PERC_ICMS_RATEIO_FECH_NF,
    CST_SN,
    CST_DEVOLUCAO,
    COD_CST_PIS_COFINS,
    VALOR_BASE_PIS,
    VALOR_PIS,
    PERC_PIS,
    VALOR_BASE_COFINS,
    VALOR_COFINS,
    PERC_COFINS,
    VALOR_BASE_II,
    VALOR_II,
    NFEXML_QUANTIDADE,
    NFEXML_QUANT_POR_EMBALAGEM,
    NFEXML_COD_UNIDADE,
    VALOR_EPP_SIMPLES_ITEM,
    PERC_EPP_SIMPLES_ITEM,
    VALOR_BASE_EPP_SIMPLES_IT,
    DARE_VALOR_BASE_ICMS,
    DARE_PERC_ALIQUOTA,
    DARE_VALOR_ICMS,
    CST_ST,
    EDITAR_VALORES_ITEM,
    CTB_COD_CST_ICMS,
    COD_CST_IPI,
    VALOR_DESCONTO_REF_ICMS_ITEM,
    VALOR_OUTROS_ITEM,
    VALOR_THC_ITEM,
    PERC_MVA,
    PRECO_UNITARIO_ITEM_NF,
    PESO_TOTAL,
    VALOR_SISCOMEX_ITEM,
    VALOR_OT_ACRES_CALC,
    MAT_ACAB_COMP,
    QTDE_COMPOSICAO,
    SEQ_MAT_ACAB_COMP,
    CUSTO_COMPLEMENTAR,
    RATEIO_SELETIVO_ST,
    PERC_FCP_ST_RET,
    VALOR_FCP_ST_RET,
    VALOR_BC_FCP_ST_RET,
    COD_UNIDADE_SECUNDARIA,
    VALOR_VERBA,
    VALOR_BC_ST_RET,
    VALOR_ICMS_ST_RET,
    RASTRO,
    VALOR_FRETE_NAO_DESTACADO_NF,
    PERC_ST_RET,
    ORIG_PROD_XML,
    VICMSSUBSTITUTO,
    PERC_II,
    COD_MATERIAL,
    NUM_ITEM
)
SELECT
    {cod_compra},
    CI.PERCENTUAL_ICMS_ITEM,
    CI.VALOR_ICMS,
    CI.VALOR_OT_DESP_ITEM_FECH_NF,
    CI.PERC_SEGURO_ITEM_FECH_NF,
    CI.VALOR_SEGURO_ITEM_FECH_NF,
    CI.PERC_ICMS_RATEIO_FECH_NF,
    CI.CST_SN,
    CI.CST_DEVOLUCAO,
    CI.COD_CST_PIS_COFINS,
    CI.VALOR_BASE_PIS,
    CI.VALOR_PIS,
    CI.PERC_PIS,
    CI.VALOR_BASE_COFINS,
    CI.VALOR_COFINS,
    CI.PERC_COFINS,
    CI.VALOR_BASE_II,
    CI.VALOR_II, 
    CI.NFEXML_QUANTIDADE,
    CI.NFEXML_QUANT_POR_EMBALAGEM,
    CI.NFEXML_COD_UNIDADE,
    CI.VALOR_EPP_SIMPLES_ITEM,
    CI.PERC_EPP_SIMPLES_ITEM,
    CI.VALOR_BASE_EPP_SIMPLES_IT,
    CI.DARE_VALOR_BASE_ICMS,
    CI.DARE_PERC_ALIQUOTA,
    CI.DARE_VALOR_ICMS,
    CI.CST_ST,
    CI.EDITAR_VALORES_ITEM,
    CI.CTB_COD_CST_ICMS,
    CI.COD_CST_IPI,
    CI.VALOR_DESCONTO_REF_ICMS_ITEM,
    CI.VALOR_OUTROS_ITEM,
    CI.VALOR_THC_ITEM,
    CI.PERC_MVA,
    CI.PRECO_UNITARIO_ITEM_NF,
    CI.PESO_TOTAL,
    CI.VALOR_SISCOMEX_ITEM,
    CI.VALOR_OT_ACRES_CALC,
    CI.MAT_ACAB_COMP,
    CI.QTDE_COMPOSICAO,
    CI.SEQ_MAT_ACAB_COMP,
    CI.CUSTO_COMPLEMENTAR,
    CI.RATEIO_SELETIVO_ST,
    CI.PERC_FCP_ST_RET,
    CI.VALOR_FCP_ST_RET,
    CI.VALOR_BC_FCP_ST_RET,
    CI.COD_UNIDADE_SECUNDARIA,
    CI.VALOR_VERBA,
    CI.VALOR_BC_ST_RET,
    CI.VALOR_ICMS_ST_RET,
    CI.RASTRO,
    CI.VALOR_FRETE_NAO_DESTACADO_NF,
    CI.PERC_ST_RET,
    CI.ORIG_PROD_XML,
    CI.VICMSSUBSTITUTO,
    CI.PERC_II,
    CI.COD_MATERIAL,
    CI.NUM_ITEM
FROM COMPRA_ITEM CI
WHERE CI.COD_COMPRA IN (
    SELECT MAX(C.COD_COMPRA) AS ULTIMA_COMPRA
    FROM COMPRA_ITEM X
    INNER JOIN COMPRA C ON C.COD_COMPRA = X.COD_COMPRA
    WHERE C.COD_FORNECEDOR = 22
    AND X.COD_COMPRA < {cod_compra}
);
"""

c.execute(insert_query)
conn.commit()

# Perguntar se deseja executar a atualização do ICMS dos itens
atualizar_icms_itens = input('Deseja atualizar o ICMS dos itens? (S/N): ')
if atualizar_icms_itens.upper() == 'S':
    update_icms_itens_query = f"""
    --sql
    UPDATE COMPRA_ITEM CI
    SET CI.VALOR_ICMS = (CI.PERCENTUAL_ICMS_ITEM * CI.VALOR_TOTAL_ITEM) / 100
    WHERE CI.COD_COMPRA = {cod_compra};
    """
    c.execute(update_icms_itens_query)
    conn.commit()

# Perguntar se deseja atualizar as informações do ICMS no total da compra
atualizar_icms_total = input('Deseja atualizar as informações do ICMS no total da compra? (S/N): ')
if atualizar_icms_total.upper() == 'S':
    update_icms_total_query = f"""
    --sql
    UPDATE COMPRA C
    SET C.VALOR_ICMS_NF = (SELECT SUM(CI.PERCENTUAL_ICMS_ITEM * CI.VALOR_TOTAL_ITEM) / 100
                           FROM COMPRA_ITEM CI
                           WHERE CI.COD_COMPRA = {cod_compra}),
        C.VALOR_BASE_ICMS = (SELECT SUM(CI.VALOR_TOTAL_ITEM)
                             FROM COMPRA_ITEM CI
                             WHERE CI.COD_COMPRA = {cod_compra}
                             AND CI.VALOR_ICMS > 0.01)
    WHERE C.COD_COMPRA = {cod_compra};
    """
    c.execute(update_icms_total_query)
    conn.commit()

conn.close()
