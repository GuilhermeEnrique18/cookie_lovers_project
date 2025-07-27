import pandas as pd

excel_path = "../data/Base_de_vendas_COOKIE.xlsx"
sheets = pd.read_excel(excel_path, sheet_name=None)

# Criacao dos DataFrames
df_cliente = sheets["tb_cliente"].copy()
df_venda = sheets["tb_venda"].copy()
df_produto = sheets["tb_produto"].copy()
df_tipo_produto = sheets["tb_tipo_produto"].copy()
df_feedback_produto = sheets["feedback"].copy()
df_fornecedor = sheets["tb_fonecedor"].copy()
df_ingredientes = sheets["tb_ingredientes"].copy()

# Remove tabelas desnecessarias ou inutilizaveis (no exemplo do projeto, as planilhas 1 e 3 que foram adicionadas sem querer)
def remove_unusable_tables(first_table_name: str):
    for table in list(sheets):
        if table.lower().startswith(f"{first_table_name}"):
            sheets.pop(table)

# Substitui nome da tabela pelo nome que julgar correto
def fix_table(i_table, c_table):  # i = 'incorrect' e o c = correct
    if i_table in sheets:
        sheets[c_table] = sheets.pop(i_table)

dados_item_venda = []

def extract_sale_itens(df_venda: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma a coluna 'itens_vendidos' em um DataFrame relacional.

    Parâmetros:
    - df_venda: DataFrame original com coluna 'itens_vendidos' e 'id_venda'

    Retorna:
    - DataFrame com colunas ['id_venda', 'nome_produto', 'quantidade']
    """
    dados_item_venda = []

    for _, row in df_venda.iterrows():
        id_venda = row["id_venda"]
        texto = row.get("itens_vendidos") or row.get("Itens Vendidos")
        if pd.notnull(texto):
            itens = texto.split(",")
            for item in itens:
                item = item.strip()
                if "X" in item:
                    try:
                        qtd_texto, nome = item.split("X", 1)
                        quantidade = int(qtd_texto.strip())
                        nome_produto = nome.strip()
                        dados_item_venda.append(
                            {
                                "id_venda": id_venda,
                                "nome_produto": nome_produto,
                                "quantidade": quantidade,
                            }
                        )
                    except ValueError:
                        continue  # Pula se não conseguir converter
    return pd.DataFrame(dados_item_venda)
