import pandas as pd
import gender_guesser.detector as gender
from sqlalchemy import create_engine

pd.set_option("display.max_columns", 4)
pd.set_option("display.max_rows", None)

from functions.data_functions import *

# Configurações da conexão
user = "postgres"
password = "86183044"
host = "localhost"
port = "5432"
database = "cookiedb"

# Criação da engine de conexão
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

if __name__ == "__main__":
    # ETL: E:
    remove_unusable_tables("planilha")
    fix_table("tb_fonecedor", "tb_fornecedor")
    print("Tabelas: ", list(sheets.keys()))
    print()
    print(df_venda.dtypes)

    # T:

    def limpar_cnpj(cnpj):
        """Remove tudo que não é número do CNPJ e garante tamanho correto"""
        if pd.isna(cnpj):
            return None
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
        return cnpj_limpo if len(cnpj_limpo) == 14 else None


    def validar_uf(uf):
        """Deixa apenas UF com 2 caracteres, maiúscula"""
        if pd.isna(uf):
            return None
        uf_limpa = str(uf).strip().upper()
        return uf_limpa if len(uf_limpa) == 2 else None


    def validar_texto_max(t, max_len):
        """Trunca texto para tamanho máximo permitido"""
        if pd.isna(t):
            return None
        texto = str(t).strip()
        return texto[:max_len]


    def limpar_fornecedor(df_fornecedor):
        """Limpa e valida colunas do DataFrame fornecedor"""
        df_fornecedor['cnpj'] = df_fornecedor['cnpj'].apply(limpar_cnpj)
        df_fornecedor['uf'] = df_fornecedor['uf'].apply(validar_uf)
        df_fornecedor['razao_social'] = df_fornecedor['razao_social'].apply(lambda x: validar_texto_max(x, 50))
        df_fornecedor['nome_fantasia'] = df_fornecedor['nome_fantasia'].apply(lambda x: validar_texto_max(x, 18))
        df_fornecedor['cidade'] = df_fornecedor['cidade'].apply(lambda x: validar_texto_max(x, 20))

        df_fornecedor = df_fornecedor.dropna(
            subset=['cnpj', 'uf'])

        return df_fornecedor


    # limpando fornecedor:
    df_fornecedor = limpar_fornecedor(df_fornecedor)

    # Depois insere no banco
    df_fornecedor.to_sql("fornecedor", engine, if_exists="append", index=False)

    # Alteracao do tipo do campo data
    df_venda["data_venda"] = pd.to_datetime(df_venda["data_venda"], errors="coerce")
    df_produto.rename(columns={"preco_uniatrio": "preco_unitario"}, inplace=True)

    # Verificar tipos da tabela venda
    print(df_venda.dtypes)

    # Mescla os dados de venda com cliente e item_venda
    df_item_venda = extract_sale_itens(df_venda)
    print(df_item_venda)
    # Filtro produtos mais vendidos
    total_produtos_vendidos = (
        df_item_venda.groupby("nome_produto")["quantidade"]
        .sum()
        .sort_values(ascending=False)
    )
    print(f"Produtos mais vendidos: \n {total_produtos_vendidos}")

    print("df_produto.columns:", df_produto.columns)
    print("df_item_venda.columns:", df_item_venda.columns)

    # Adiciona coluna de mês, dia, semana etc
    df_venda_full = df_venda.merge(df_cliente, on="id_cliente").merge(
        df_item_venda, on="id_venda"
    )  # .merge(df_produto, on='nome_produto') nao é necessario pois ja é declarado em item venda

    df_venda_full["data_venda"] = pd.to_datetime(
        df_venda_full["data_venda"], errors="coerce"
    )

    df_venda_full["mes"] = df_venda_full["data_venda"].dt.month
    df_venda_full["dia_da_semana"] = df_venda_full["data_venda"].dt.day_name()
    df_venda_full["dia"] = df_venda_full["data_venda"].dt.date
    # quantidade total de itens vendidos por dia
    qtd_itens_mais_vendidos_por_dia = (
        df_venda_full.groupby("dia_da_semana")["quantidade"]
        .sum()
        .sort_values(ascending=False)
    )
    dias_mais_vendidos_df = qtd_itens_mais_vendidos_por_dia.reset_index(
        name="quantidade"
    )
    # quantidade total de vendas(transacoes) por dia
    vendas_por_dia = (
        df_venda_full.groupby("dia_da_semana")["id_venda"]
        .nunique()
        .sort_values(ascending=False)
    )
    print(vendas_por_dia)
    print(dias_mais_vendidos_df)
    print(df_venda_full.head())

    # sexo
    detector = gender.Detector()

    def identificar_genero(full_name):
        first_name = full_name.split()[0]
        result = detector.get_gender(first_name)

        if result in ["male", "mostly_male"]:
            return "M"
        elif result in ["female", "mostly_female"]:
            return "F"
        else:
            return "O"  # indefinido

    # Aplica ao DataFrame
    df_cliente["sexo"] = df_cliente["nome"].apply(identificar_genero)

    print(df_cliente.columns)
    print()
    print(df_cliente.head(5))
    df_total_customers_by_sex = (
        df_cliente["sexo"]
        .value_counts()
        .reset_index(name="quantidade")
        .rename(columns={"index": "sexo"})
    )
    df_woman_customers = df_cliente[df_cliente["sexo"] == "F"]
    df_man_customers = df_cliente[df_cliente["sexo"] == "M"]
    df_undefined_customers = df_cliente[df_cliente["sexo"] == "O"]
    print()
    print(df_total_customers_by_sex)
    print(df_woman_customers)
    print(df_man_customers)
    print(df_undefined_customers)


    # Limpar duplicatas com base na chave primária
    df_tipo_produto.drop_duplicates(subset="id_tipo_produto", inplace=True)
    df_produto.drop_duplicates(subset="id_produto", inplace=True)
    df_fornecedor.drop_duplicates(subset="id_fornecedor", inplace=True)
    df_ingredientes.drop_duplicates(subset="id_ingrediente", inplace=True)
    df_cliente.drop_duplicates(subset="id_cliente", inplace=True)
    df_venda.drop_duplicates(subset="id_venda", inplace=True)
    df_item_venda.drop_duplicates(subset=["id_venda", "nome_produto"], inplace=True)
    print(df_feedback_produto.columns)
    df_feedback_produto.drop_duplicates(subset="idvenda", inplace=True)
    
    # Insere nas tabelas já criadas -
    
    df_tipo_produto.to_sql("tipo_de_produto", engine, if_exists="replace", index=False)
    df_produto.to_sql("produto", engine, if_exists="replace", index=False)
    df_fornecedor.to_sql("fornecedor", engine, if_exists="replace", index=False)
    df_ingredientes.to_sql("ingrediente", engine, if_exists="replace", index=False)
    df_cliente.to_sql("cliente", engine, if_exists="replace", index=False)
    df_venda.to_sql("venda", engine, if_exists="replace", index=False)
    df_item_venda.to_sql("item_venda", engine, if_exists="replace", index=False)
    df_feedback_produto.to_sql("feedback_produto", engine, if_exists="replace", index=False)

    print("Todas as tabelas foram recriadas e os dados inseridos com sucesso no PostgreSQL.")

    print(df_total_customers_by_sex)
    print(df_cliente["sexo"].value_counts())
