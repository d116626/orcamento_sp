from selenium import webdriver
from selenium.webdriver.support.ui import Select
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

def get_orcamento():
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    years = [str(i) for i in range(2020,2021)]

    for year in years:
        
        path=os.getcwd()
        path = path.split('notebooks')[0] + f'data/orcamento/{year}'

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.dir",path);
        profile.set_preference("browser.download.folderList",2);
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream");
        profile.set_preference("browser.download.manager.showWhenStarting",False);
        profile.set_preference("browser.helperApps.neverAsk.openFile","application/csv,application/excel,application/vnd.msexcel,application/vnd.ms-excel,text/anytext,text/comma-separated-values,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream");
        profile.set_preference("browser.helperApps.alwaysAsk.force", False);
        profile.set_preference("browser.download.manager.useWindow", False);
        profile.set_preference("browser.download.manager.focusWhenStarting", False);
        profile.set_preference("browser.download.manager.alertOnEXEOpen", False);
        profile.set_preference("browser.download.manager.showAlertOnComplete", False);
        profile.set_preference("browser.download.manager.closeWhenDone", True);
        profile.set_preference("pdfjs.disabled", True);
        
        
        
        firefox = webdriver.Firefox(firefox_profile=profile)
        url = 'https://www.fazenda.sp.gov.br/SigeoLei131/Paginas/FlexConsDespesa.aspx'

        firefox.get(url)
        # firefox.request('POST', url,)


        ano = Select(firefox.find_element_by_name('ctl00$ContentPlaceHolder1$ddlAno'))
        ano.select_by_value(year)

        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$0").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$1").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$2").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$3").click()
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$cblFase$4").click()

        options = {
            'ctl00$ContentPlaceHolder1$ddlOrgao':"",
            'ctl00$ContentPlaceHolder1$ddlCategoria':""	,
            'ctl00$ContentPlaceHolder1$ddlUo':"",
            'ctl00$ContentPlaceHolder1$ddlGrupo':"",
            'ctl00$ContentPlaceHolder1$ddlUge':"",
            'ctl00$ContentPlaceHolder1$ddlModalidade':"",
            'ctl00$ContentPlaceHolder1$ddlFonteRecursos':"",
            'ctl00$ContentPlaceHolder1$ddlElemento':"",
            'ctl00$ContentPlaceHolder1$ddlFuncao':"",
            'ctl00$ContentPlaceHolder1$ddlSubFuncao':"",
            'ctl00$ContentPlaceHolder1$ddlPrograma':"",
            'ctl00$ContentPlaceHolder1$ddlAcao':"",
            'ctl00$ContentPlaceHolder1$ddlProgramaTrabalho':"",
        }

        for op in options.keys():
            selected = Select(firefox.find_element_by_name(op))
            selected.select_by_value(options[op])
            time.sleep(0.2)

        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$btnPesquisar").click()

        time.sleep(15)
        firefox.find_element_by_name("ctl00$ContentPlaceHolder1$btnExcel").click()
        time.sleep(15)

        
        firefox.quit()
        
        os.rename(path+'/gdvDespesasExcel.csv', path+'/{}_orcamento_{}.csv'.format(today, year))
        
        df = pd.read_csv(path+'/{}_orcamento_{}.csv'.format(today, year), encoding='windows-1254')
        
        df = df[df['Órgão'].notnull()]
        
        df['date'] = today
        
        df.columns = manipulate.normalize_cols(df.columns)
        
        cols = ['dotacao_inicial','dotacao_atual','empenhado','liquidado','pago','pago_restos']


        for col in cols:
            df[col] = df[col].str.replace('.','').str.replace(',','.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
        df = df.loc[:, df.isnull().mean() < .98]
    
        
        df.to_csv(path+'/last_data.csv', encoding='utf-8', index=False)
        
        df.to_csv(path+'/{}_orcamento_{}.csv'.format(today, year),  encoding='utf-8', index=False)

        
        return df






def _get_credentials_gbq():

    SCOPES = [
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/drive',
    ]

    credentials = pydata_google_auth.get_user_credentials(
        SCOPES,
        # Set auth_local_webserver to True to have a slightly more convienient
        # authorization flow. Note, this doesn't work if you're running from a
        # notebook on a remote sever, such as over SSH or with Google Colab.
        auth_local_webserver=True,
    )

    return credentials


def to_gbq(df, 
        table_name, 
        schema_name = 'simula_corona',
        project_id  = 'robusta-lab',
        **kwargs):
    """
    write a dataframe in Google BigQuery
    """

    destination_table = f'{schema_name}.{table_name}'

    pandas_gbq.to_gbq(
        df,
        destination_table,
        project_id,
        credentials = _get_credentials_gbq(),
        **kwargs
    )

def read_gbq(query, 
        project_id='robusta-lab', 
        **kwargs):
    """
    write a dataframe in Google BigQuery
    """

    return pandas_gbq.read_gbq(
        query,
        project_id,
        credentials=_get_credentials_gbq(),
        **kwargs)




def to_storage(bucket,bucket_folder,file_name,path_to_file):

    client = storage.Client(project='gavinete-sv')
    bucket = client.get_bucket(f'{bucket}')
    blob   = bucket.blob(f'{bucket_folder}/{file_name}')
    blob.upload_from_filename(f'{path_to_file}')

    print('Done!')



def read_sheets(sheet_name, workSheet=0):


    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('../../credentials/gabinete-sv-9aed310629e5.json', scope)
    gc          = gspread.authorize(credentials)
    if workSheet==0:
        wks         = gc.open(sheet_name).sheet1
    else:
        wks = gc.open(sheet_name).worksheet(workSheet)
        
    data        = wks.get_all_values()
    headers     = data.pop(0)

    return pd.DataFrame(data, columns=headers)







