import pandas as pd
import numpy as np

from scripts import manipulate


def tables_to_df(dd):
    df_all = pd.DataFrame()
    for i in range(len(dd)):
        df_all = pd.concat([df_all, dd[i].df], axis=0)
    df_all.columns = df_all.head(1).values.tolist()[0]

    return df_all.reset_index(drop=True)


def put_in_order(df):
    df = df.copy()
    outros_cols = [
        "parlamentar",
        "entidade_beneficiada",
        "municipio",
        "cnpj",
        "orgao",
        "objeto",
        "valor",
    ]
    saude_cols = [
        "parlamentar",
        "entidade_beneficiada",
        "municipio",
        "cnpj",
        "objeto",
        "valor",
    ]
    return df[outros_cols] if "orgao" in df.columns.tolist() else df[saude_cols]


def manipulate_padronize_df(df, columns_df):
    df = df.copy()
    df.columns = columns_df

    first_row = df.head(1).values.tolist()[0]
    first_row = [element for element in first_row if element is not np.nan]
    for col, element in zip(columns_df[: len(first_row)], first_row):
        mask = df[col] != element
        df = df[mask]

    df["valor"] = df["valor"].str.replace(".", "")

    for col in df.columns[:-1]:
        df[col] = df[col].str.replace("\n", " ").str.replace("  ", " ").str.strip()

    for col in df.columns:
        df[f"{col}_shifted"] = df[f"{col}"].shift(-1)

    for col in columns_df:
        df[col] = np.where(
            df["valor_shifted"] == "", df[col] + " " + df[f"{col}_shifted"], df[col]
        )
    for col in df.columns:
        df[col] = df[col].str.upper().str.strip()

    mask = df["valor"] != ""
    df = df[columns_df][mask]
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df["parlamentar"] = np.where(df["parlamentar"] == "", np.nan, df["parlamentar"])
    df["parlamentar"] = df["parlamentar"].fillna(method="ffill")
    # df["parlamentar"] = df["parlamentar"].apply(lambda name: nome_duplicado_fix(name))

    df["parlamentar"] = manipulate.normalize_names(df["parlamentar"])
    df = put_in_order(df)
    return df