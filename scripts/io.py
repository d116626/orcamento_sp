from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

import time
import os
import pandas as pd
import datetime
import numpy as np
import pandas_gbq
import pydata_google_auth
import gspread
from gcloud import storage
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import manipulate
import glob


def get_orcamento_executado():
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    ano = int(datetime.datetime.today().strftime("%Y"))
    years = [str(i) for i in range(ano, ano + 1)]

    for year in years:

        path = os.getcwd()

        year_path = path.split("notebooks")[0] + f"data/orcamento/{year}"
        if not os.path.exists(year_path):
            os.mkdir(year_path)
            os.mkdir(year_path + "/executado")
            os.mkdir(year_path + "/receita")
            os.mkdir(year_path + "/receita/arrecadado")
            os.mkdir(year_path + "/receita/previsto")

        path = path.split("notebooks")[0] + f"data/orcamento/{year}/executado"

        files_before = glob.glob(f"{path}/*")

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.dir", path)
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream",
        )
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference(
            "browser.helperApps.neverAsk.openFile",
            "application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream",
        )
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("browser.download.manager.useWindow", False)
        profile.set_preference("browser.download.manager.focusWhenStarting", False)
        profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
        profile.set_preference("browser.download.manager.showAlertOnComplete", False)
        profile.set_preference("browser.download.manager.closeWhenDone", True)
        profile.set_preference("pdfjs.disabled", True)

        options = Options()
        ### run quiet
        options.headless = True

        firefox = webdriver.Firefox(
            options=options,
            firefox_profile=profile,
            executable_path=GeckoDriverManager().install(),
        )
        url = "https://www.fazenda.sp.gov.br/SigeoLei131/Paginas/FlexConsDespesa.aspx"

        firefox.get(url)
        # firefox.request('POST', url,)

        ano = Select(firefox.find_element_by_name("ctl00$ContentPlaceHolder1$ddlAno"))
        ano.select_by_value(year)

        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$0").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$1").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$2").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$3").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$4").click()

        options = {
            "ctl00$ContentPlaceHolder1$ddlOrgao": "",
            "ctl00$ContentPlaceHolder1$ddlCategoria": "",
            "ctl00$ContentPlaceHolder1$ddlUo": "",
            "ctl00$ContentPlaceHolder1$ddlGrupo": "",
            "ctl00$ContentPlaceHolder1$ddlUge": "",
            "ctl00$ContentPlaceHolder1$ddlModalidade": "",
            "ctl00$ContentPlaceHolder1$ddlFonteRecursos": "",
            "ctl00$ContentPlaceHolder1$ddlElemento": "",
            "ctl00$ContentPlaceHolder1$ddlFuncao": "",
            "ctl00$ContentPlaceHolder1$ddlSubFuncao": "",
            "ctl00$ContentPlaceHolder1$ddlPrograma": "",
            "ctl00$ContentPlaceHolder1$ddlAcao": "",
            "ctl00$ContentPlaceHolder1$ddlProgramaTrabalho": "",
        }

        for op in options.keys():
            selected = Select(firefox.find_element_by_name(op))
            selected.select_by_value(options[op])
            time.sleep(0.2)

        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$btnPesquisar").click()

        time.sleep(60)
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$btnExcel").click()
        time.sleep(60)

        firefox.quit()

        files_after = glob.glob(f"{path}/*")

        file_now = [file for file in files_after if file not in files_before][0]

        os.rename(
            file_now,
            path + "/{}_orcamento_{}.csv".format(today, year),
        )

        df = pd.read_csv(
            path + "/{}_orcamento_{}.csv".format(today, year), encoding="windows-1254"
        )

        df = df[df["Órgão"].notnull()]

        df["date"] = today

        df.columns = manipulate.normalize_cols(df.columns)

        cols = [
            "dotacao_inicial",
            "dotacao_atual",
            "empenhado",
            "liquidado",
            "pago",
            "pago_restos",
        ]

        for col in cols:
            df[col] = df[col].str.replace(".", "").str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.loc[:, df.isnull().mean() < 0.98]

        df.to_csv(path + "/last_data.csv", encoding="utf-8", index=False)

        df.to_csv(
            path + "/{}_orcamento_{}.csv".format(today, year),
            encoding="utf-8",
            index=False,
        )

        return df


def get_orcamento_receita(tipo):
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    ano = int(datetime.datetime.today().strftime("%Y"))
    years = [str(i) for i in range(ano, ano + 1)]

    i = 0 if tipo == "previsto" else 1
    # firefox = webdriver.Firefox()
    url = "https://www.fazenda.sp.gov.br/SigeoLei131/Paginas/FlexConsReceita.aspx"

    for year in years:

        path = os.getcwd()

        year_path = path.split("notebooks")[0] + f"data/orcamento/{year}"
        if not os.path.exists(year_path):
            os.mkdir(year_path)
            os.mkdir(year_path + "/executado")
            os.mkdir(year_path + "/receita")
            os.mkdir(year_path + "/receita/arrecadado")
            os.mkdir(year_path + "/receita/previsto")

        if i == 0:

            path = (
                path.split("notebooks")[0] + f"data/orcamento/{year}/receita/previsto"
            )

        else:
            path = (
                path.split("notebooks")[0] + f"data/orcamento/{year}/receita/arrecadado"
            )

        files_before = glob.glob(f"{path}/*")

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.dir", path)
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream",
        )
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference(
            "browser.helperApps.neverAsk.openFile",
            "application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream",
        )
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("browser.download.manager.useWindow", False)
        profile.set_preference("browser.download.manager.focusWhenStarting", False)
        profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
        profile.set_preference("browser.download.manager.showAlertOnComplete", False)
        profile.set_preference("browser.download.manager.closeWhenDone", True)
        profile.set_preference("pdfjs.disabled", True)

        # year = '2019'

        options = Options()
        options.headless = True

        firefox = webdriver.Firefox(
            options=options,
            firefox_profile=profile,
            executable_path=GeckoDriverManager().install(),
        )
        firefox.get(url)
        # firefox.request('POST', url,)

        ano = Select(firefox.find_element_by_name("ctl00$ContentPlaceHolder1$ddlAno"))
        ano.select_by_value(year)

        firefox.find_element_by_id(
            "ctl00_ContentPlaceHolder1_rblFase_{}".format(i)
        ).click()

        options = {
            "ctl00$ContentPlaceHolder1$ddlOrgao": "",
            # 'ctl00$ContentPlaceHolder1$ddlCategoria:'',
            "ctl00$ContentPlaceHolder1$ddlGestao": "",
            # 'ctl00$ContentPlaceHolder1$ddlOrigem: '',
            "ctl00$ContentPlaceHolder1$ddlUge": "",
            # 'ctl00$ContentPlaceHolder1$ddlEspecie':'',
            "ctl00$ContentPlaceHolder1$ddlFonteRecursos": "",
            # 'ctl00$ContentPlaceHolder1$ddlRubrica':'',
            # 'ctl00$ContentPlaceHolder1$ddlAlinea':'',
            # 'ctl00$ContentPlaceHolder1$rblFase':'',
            "ctl00$ContentPlaceHolder1$ddlSubAlinea": "",
        }

        for op in options:
            selected = Select(firefox.find_element_by_name(op))
            selected.select_by_value(options[op])
            time.sleep(0.2)

        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$btnPesquisar").click()
        time.sleep(60)
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$btnExcel").click()
        time.sleep(60)

        firefox.quit()

        files_after = glob.glob(f"{path}/*")
        file_now = [file for file in files_after if file not in files_before][0]

        os.rename(
            file_now,
            path + "/{}_orcamento_{}.csv".format(today, year),
        )

        df = pd.read_csv(
            path + "/{}_orcamento_{}.csv".format(today, year), encoding="windows-1254"
        )

        df = df[df["Órgão"].notnull()]

        df["date"] = today

        df.columns = manipulate.normalize_cols(df.columns)

        if i == 0:
            cols = ["previsto_do_ano"]
        else:
            l = df.columns.to_list()
            cols = [x for x in l if "arrecadado_ate" in x]
            df = df.rename(columns={cols[0]: "arrecadado"})
            cols = ["arrecadado"]

        for col in cols:
            df[col] = df[col].str.replace(".", "").str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.loc[:, df.isnull().mean() < 0.98]

        df.to_csv(path + "/last_data.csv", encoding="utf-8", index=False)

        df.to_csv(
            path + "/{}_orcamento_{}.csv".format(today, year),
            encoding="utf-8",
            index=False,
        )

    return df


def _get_credentials_gbq():

    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = pydata_google_auth.get_user_credentials(
        SCOPES,
        # Set auth_local_webserver to True to have a slightly more convienient
        # authorization flow. Note, this doesn't work if you're running from a
        # notebook on a remote sever, such as over SSH or with Google Colab.
        auth_local_webserver=True,
    )

    return credentials


def to_gbq(
    df, table_name, schema_name="simula_corona", project_id="robusta-lab", **kwargs
):
    """
    write a dataframe in Google BigQuery
    """

    destination_table = f"{schema_name}.{table_name}"

    pandas_gbq.to_gbq(
        df, destination_table, project_id, credentials=_get_credentials_gbq(), **kwargs
    )


def read_gbq(query, project_id="robusta-lab", **kwargs):
    """
    write a dataframe in Google BigQuery
    """

    return pandas_gbq.read_gbq(
        query, project_id, credentials=_get_credentials_gbq(), **kwargs
    )


def to_storage(bucket, bucket_folder, file_name, path_to_file):

    client = storage.Client(project="gavinete-sv")
    bucket = client.get_bucket(f"{bucket}")
    blob = bucket.blob(f"{bucket_folder}/{file_name}")
    blob.upload_from_filename(f"{path_to_file}")

    print("Done!")


def read_sheets(sheet_name, workSheet=0):

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "../../credentials/gabinete-sv-9aed310629e5.json", scope
    )
    gc = gspread.authorize(credentials)
    if workSheet == 0:
        wks = gc.open(sheet_name).sheet1
    else:
        wks = gc.open(sheet_name).worksheet(workSheet)

    data = wks.get_all_values()
    headers = data.pop(0)

    return pd.DataFrame(data, columns=headers)
