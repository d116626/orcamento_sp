import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys

import pandas as pd
import numpy as np
from scripts.manipulate import normalize_cols, padronize_str
import re
import math


def generic_group(df, group_cols, numeric_cols, sort_cols):
    return (
        df[group_cols + numeric_cols]
        .groupby(by=group_cols, as_index=False)
        .sum()
        .sort_values(by=sort_cols, ascending=False)
    )


def get_despesas(files):
    df_cols = pd.DataFrame()
    df_despesa = pd.DataFrame()
    for file in files:
        ano = re.findall(r"\d\d\d\d", file)[0]
        print(ano)
        print(file)

        df = pd.read_csv(file, encoding="latin1", dtype=str, index_col=False)
        df.columns = normalize_cols(df.columns)
        df = df[df["orgao"].notnull()].copy()
        df["ano"] = int(ano)

        numeric_columns = [
            "dotacao_inicial",
            "dotacao_atual",
            "empenhado",
            "liquidado",
            "pago",
            "pago_restos",
        ]

        for col in numeric_columns:
            df[col] = df[col].str.replace(".", "").str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="float")

        str_cols = [
            "orgao",
            "uo",
            "unidade_gestora",
            "fonte_de_recursos",
            "funcao",
            "sub_funcao",
            "programa",
            "acao",
            "funcional_programatica",
            "elemento",
        ]
        for col in str_cols:
            df[col] = padronize_str(df[col])

        df_despesa = pd.concat([df_despesa, df])

        new_df = pd.DataFrame(df.columns.to_list(), columns=[ano])
        df_cols = pd.concat([df_cols, new_df], 1)

    df_despesa = df_despesa.drop(["unnamed:_16"], 1)

    return df_despesa, df_cols


def receita_origem(df_receita):
    ### Origem da receita
    df_receita["id_origem"] = df_receita["id_receita"].apply(lambda x: x[:2])
    origem_receita = {
        "11": "Receita Tributária",
        "12": "Receita de Contribuições",
        "13": "Receita Patrimonial",
        "14": "Receita Agropecuária",
        "15": "Receita Industrial",
        "16": "Receita de Serviços",
        "17": "Transferências Correntes",
        "19": "Outras Receitas Correntes",
        "21": "Operações de Crédito",
        "22": "Alienação de Bens",
        "23": "Amortização de Empréstimos",
        "24": "Traferência de Capital",
        "25": "Outras Receitas de Capital do Estado",
        "29": "Demais Receitas de Capital",
        "72": "Receitas de Contribuições - Intra-Orçamentárias",
        "74": "Receita Intra-Orçamentárias com Receitas de Agropecuaria",
        "76": "Receitas Intra-Orçamentárias com Receitas de Serviços",
        "77": "Receita de Transferencia Intra-Orçamentárias COVID",
        "79": "Receitas Intra-Orçamentárias com Outras Receitas Correntes",
        "82": "Alienação de Bens",
        "85": "Outras Receitas de Capital",
        "89": "Outras Receitas de Capital",
    }
    df_receita["origem"] = (
        df_receita["id_origem"] + " - " + df_receita["id_origem"].map(origem_receita)
    )

    return df_receita


def get_receita(files):
    ## CHECA SE ARQUIVOS SAO CONSISTENTES ENTRE OS ANOS
    df_cols = pd.DataFrame()
    df_receita = pd.DataFrame()
    for file in files:
        ano = re.findall(r"\d\d\d\d", file)[0]
        print(ano)
        print(file)

        df = pd.read_csv(file, encoding="latin1", dtype=str, index_col=False)
        df.columns = normalize_cols(df.columns)
        df = df[df["orgao"].notnull()].copy()
        df["ano"] = int(ano)

        numeric_columns = [
            "arrecadado_ate_16_04_2021",
        ]

        for col in numeric_columns:
            df[col] = df[col].str.replace(".", "").str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="float")

        str_cols = [
            "orgao",
            "gestao",
            "unidade_gestora",
            "fonte_de_recursos",
            "receita",
        ]
        for col in str_cols:
            df[col] = padronize_str(df[col])

        df_receita = pd.concat([df_receita, df])

        new_df = pd.DataFrame(df.columns.to_list(), columns=[ano])
        df_cols = pd.concat([df_cols, new_df], 1)

    df_receita = df_receita.drop(["unnamed:_6"], 1)

    df_receita["id_receita"] = df_receita["receita"].apply(
        lambda x: x.split("-")[0].strip()
    )

    ### Origem da receita
    df_receita = receita_origem(df_receita)
    return df_receita, df_cols
