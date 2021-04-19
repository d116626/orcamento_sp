import re
import pandas as pd


def padronize_str(df):
    return (
        df.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.upper()
    )


def normalize_cols(df):
    return (
        df.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace("$", "")
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace("-", "")
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("__", "_")
        .str.replace("___", "_")
        .str.lower()
        .str.replace(".", "")
    )


def normalize_names(df):
    return (
        df.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )


def manipulate_ldo_2021(text):
    # select only the pages of interest
    first_page_text = "\nANEXO III\nMETAS E PRIORIDADES"
    first_page_position = re.search(first_page_text, text).end()

    ldo_data = text[first_page_position:]

    # select only the pages of interest
    first_page_text = "\nANEXO III\nMETAS E PRIORIDADES"
    first_page_position = re.search(first_page_text, text).end()

    ldo_data = text[first_page_position:]

    # first clean
    clear_lines = [
        "",
        "Governo do Estado de São Paulo",
        "\x0c002458969185137",
        "\x0cProjeto de Lei de Diretrizes Orçamentárias 2021",
        "META 2021",
    ]
    ldo_lines = [line for line in ldo_data.split("\n") if line not in clear_lines]

    ldo_lines_clean = []
    for i in range(len(ldo_lines)):

        if i < len(ldo_lines) - 1:
            if ldo_lines[i + 1] == "002458969185137":
                pass
            else:
                ldo_lines_clean.append(ldo_lines[i])
        else:
            ldo_lines_clean.append(ldo_lines[i])

    ldo_lines_clean = [
        line for line in ldo_lines_clean if line not in ["002458969185137"]
    ]

    # clean and aggregate using some patterns
    ldo_clean = []
    for i in range(len(ldo_lines_clean)):
        # orgao
        if re.search("Órgão:", ldo_lines_clean[i - 1]) != None:
            ldo_clean.append(ldo_lines_clean[i - 1] + " | " + ldo_lines_clean[i])
            ldo_clean.remove(ldo_lines_clean[i - 1])
        elif re.search("Programa:", ldo_lines_clean[i - 1]) != None:
            ldo_clean.append(ldo_lines_clean[i - 1] + " | " + ldo_lines_clean[i])
            ldo_clean.remove(ldo_lines_clean[i - 1])
        elif re.search("PRODUTO:", ldo_lines_clean[i - 1]) != None:
            ldo_clean.append(ldo_lines_clean[i - 1] + " | " + ldo_lines_clean[i])
            ldo_clean.remove(ldo_lines_clean[i - 1])

        else:
            ldo_clean.append(ldo_lines_clean[i])

    # clean and aggregate using other patterns
    trash_lines = ["", "", "", ""]
    ldo_clean = ldo_clean + trash_lines
    ldo_cleaned = []
    lines_to_remove = []
    for i in range(len(ldo_clean)):

        if i < len(ldo_clean) - 3:
            if ldo_clean[i] == "AÇÃO":
                ldo_cleaned.append(
                    ldo_clean[i] + " | " + ldo_clean[i + 1] + " | " + ldo_clean[i + 2]
                )
                lines_to_remove.append(ldo_clean[i + 1])
                lines_to_remove.append(ldo_clean[i + 2])
            else:
                ldo_cleaned.append(ldo_clean[i])
        else:
            ldo_cleaned.append(ldo_clean[i])

    ldo_cleaned = [
        line for line in ldo_cleaned if line not in lines_to_remove + trash_lines
    ]

    return ldo_cleaned