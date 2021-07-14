import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

from paths import *
from scripts import io
from scripts import manipulate

import datetime


def upload_bigQuerry():

    ##DESPESA
    io.get_orcamento_executado()
    df = pd.read_csv("../data/orcamento/2020/executado/last_data.csv")

    df["atual_por_inicial"] = df["dotacao_atual"] / df["dotacao_inicial"]
    df["pago_por_dotacao_atual"] = df["pago"] / df["dotacao_atual"]

    io.to_gbq(df, "orcamento_2020", "orcamento", "gabinete-sv", if_exists="replace")
    print("\n")
    ##RECEITA
    io.get_orcamento_receita("previsto")
    io.get_orcamento_receita("arrecadado")

    previsto = pd.read_csv("../data/orcamento/2020/receita/previsto/last_data.csv")
    arrecadado = pd.read_csv("../data/orcamento/2020/receita/arrecadado//last_data.csv")

    io.to_gbq(
        previsto,
        "receita_previsto_2020",
        "orcamento",
        "gabinete-sv",
        if_exists="replace",
    )
    io.to_gbq(
        arrecadado,
        "receita_arrecadado_2020",
        "orcamento",
        "gabinete-sv",
        if_exists="replace",
    )

    previsto_x_arrecadado = pd.merge(
        arrecadado,
        previsto,
        on=[
            "orgao",
            "gestao",
            "unidade_gestora",
            "fonte_de_recursos",
            "receita",
            "date",
        ],
        how="outer",
    )
    previsto_x_arrecadado["arrecadado_perc"] = (
        previsto_x_arrecadado["arrecadado"] / previsto_x_arrecadado["previsto_do_ano"]
    )
    io.to_gbq(
        previsto_x_arrecadado,
        "receita_previsto_x_arrecadado_2020",
        "orcamento",
        "gabinete-sv",
        if_exists="replace",
    )


def main():
    from datetime import datetime

    today = datetime.today().strftime("%Y-%m-%d")

    equals = 10 * "="
    print(f"#####{equals}{today}{equals}#####\n")

    print("START")
    upload_bigQuerry()
    print(today)
    print("DONE!")

    print(f"#####{equals}{today}{equals}#####\n")


if __name__ == "__main__":
    main()
