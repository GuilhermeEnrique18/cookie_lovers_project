# Projeto ETL e Análise de Dados - Cookie Sales

Este projeto realiza um processo completo de **ETL (Extract, Transform, Load)** em dados de vendas da empresa Cookie. Os dados são extraídos de um arquivo Excel, transformados com limpeza e enriquecimento em Python (pandas), e finalmente carregados em um banco de dados **PostgreSQL** para análises posteriores.

---

## Tecnologias Utilizadas

- Python 3.x
- pandas
- gender-guesser (utilizei a lib internacional, mas é recomendado a nacional se os nomes forem brasileiros.)
- SQLAlchemy
- openpyxl
- PostgreSQL (pgAdmin)
- PyCharm (ambientes de desenvolvimento)

---

## Estrutura do Projeto

```
PythonProject/
│
├── data/ # Planilhas de origem (.xlsx)
│ └── Base_de_vendas_COOKIE.xlsx
│
├── src/
│ ├── main.py # Script principal (ETL)
│ └── functions/
│ └── data_functions.py # Funções auxiliares para ETL
│
├── dados_tratados/ # CSVs intermediários ou de exportação
│
└── README.md # Documentação
```
