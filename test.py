df["programa"] = generate_col(df, r"\bPrograma:\n")
df["orgao"] = generate_col(df, r"\bÓrgão:\n")
df["ind_programa"] = generate_col(df, r"\bINDICADORES DE RESULTADO DE PROGRAMA")
df["produto"] = generate_col(df, r"\bPRODUTO: ")
df["ind_produto"] = generate_col(df, r"\bINDICADOR DE PRODUTO")
df["acao"] = generate_col(df, r"\bAÇÃO\b")

df["root"] = (
    df["programa"].fillna("")
    + df["orgao"].fillna("")
    + df["ind_programa"].fillna("")
    + df["produto"].fillna("")
    + df["ind_produto"].fillna("")
    + df["acao"].fillna("")
)
df["root"] = np.where(df["root"] == "", np.nan, df["root"])
df["root"] = df["root"].fillna(method="ffill")


df["programa"] = fill_col(df, r"\bPrograma:\n")
df["orgao"] = fill_col(df, r"\bÓrgão:\n")
df["ind_programa"] = fill_col(df, r"\bINDICADORES DE RESULTADO DE PROGRAMA")
df["produto"] = fill_col(df, r"\bPRODUTO: ")
df["ind_produto"] = fill_col(df, r"\bINDICADOR DE PRODUTO")
df["acao"] = fill_col(df, r"\bAÇÃO\b")
df["acao"] = df[
    df["acao"].fillna("").str.contains(r"\b\d\d\d\d -", regex=True, case=True)
]["acao"]


finalidade_progama_mask = (
    df["programa"].fillna("").str.contains(r"\bPrograma:\n", regex=True, case=True)
)
df["finialidade_programa"] = df[~finalidade_progama_mask]["programa"]
df["programa"] = np.where(finalidade_progama_mask, df["programa"], np.nan)

finalidade_produto_mask = (
    df["produto"].fillna("").str.contains(r"\bPRODUTO: ", regex=True, case=True)
)
df["finialidade_produto"] = df[~finalidade_produto_mask]["produto"]
df["produto"] = np.where(finalidade_produto_mask, df["produto"], np.nan)

for col in df.columns[3:]:
    if col != "acao":
        df[col] = df[col].fillna(method="ffill")
    else:
        df[col] = df[col].fillna(method="bfill")


value_programa_mask = (
    df["root"]
    .fillna("")
    .str.contains(r"\bINDICADORES DE RESULTADO DE PROGRAMA", regex=True, case=True)
)
df["value_ind_programa"] = np.where(value_programa_mask, df[1], np.nan)
df["value_ind_programa"] = (
    df["value_ind_programa"].str.replace(".", "").str.replace(",", ".")
)
df["value_ind_programa"] = pd.to_numeric(df["value_ind_programa"], errors="coerce")


value_produto_mask = (
    df["root"].fillna("").str.contains(r"\bINDICADOR DE PRODUTO", regex=True, case=True)
)
df["value_ind_produto"] = np.where(value_produto_mask, df[1], np.nan)
df["value_ind_produto"] = (
    df["value_ind_produto"].str.replace(".", "").str.replace(",", ".")
)
df["value_ind_produto"] = pd.to_numeric(df["value_ind_produto"], errors="coerce")


df_programa = df[df["value_ind_programa"].notnull()]
cols = [
    "programa",
    "orgao",
    "ind_programa",
    "finialidade_programa",
    "value_ind_programa",
]
df_programa = df_programa[cols]

cols = [
    "programa",
    "orgao",
    "finialidade_programa",
    "produto",
    "finialidade_produto",
    "ind_produto",
    "acao",
    "value_ind_produto",
]
df_produto = df[df["value_ind_produto"].notnull()]
df_produto = df_produto[cols]
