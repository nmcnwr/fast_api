from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.engine import create_engine
import pandas as pd
import numpy as np
from fastapi.staticfiles import StaticFiles
import re
from fastapi.responses import StreamingResponse, FileResponse
import io

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class QuerySubscriber(BaseModel):
    msisdn: int
    db: str


def db_connect(db):

    DIALECT = 'oracle'
    SQL_DRIVER = 'cx_oracle'
    USERNAME = 'SMASTER'
    PASSWORD = 'SMASTER'
    HOST = '10.246.16.203'
    PORT = 1521

    list_192_168_17_91 = ['i459s7']
    list_10_246_16_203 = ['i460s10', 'i460s1']
    if db in list_192_168_17_91:
        HOST = '192.168.17.91'
    if db in list_10_246_16_203:
        HOST = '10.246.16.203'

    ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME \
                           + ':' + PASSWORD + '@' + HOST \
                           + ':' + str(PORT) + '/?service_name=' + db
    return ENGINE_PATH_WIN_AUTH


@app.get("/")
def msisdn_form(request: Request):
    return templates.TemplateResponse(
        "msisdn_form.html",
        {"request": request})


@app.get("/get_csv")
async def get_csv():

    dict_ = {'key 1': 'value 1', 'key 2': 'value 2', 'key 3': 'value 3'}
    df33 = pd.DataFrame([dict_])
    stream = io.StringIO()
    df33.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv"
                                 )
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response


@app.get("/get_xls", response_class=FileResponse)
async def main():
    # some_file_path = 'xls_log/pandas_df111.xlsx'
    # return some_file_path
    return FileResponse(path='xls_log/sql_list.csv', filename='xls_log/sql_list.csv', media_type='text/csv')


@app.get("/msisdn_print/")
async def get_msisdn(request: Request, msisdn: int, db: str):

    engine = create_engine(db_connect(db))

    content = '%s %s %s' % (request.method, request.url.path, request.client.host)


    # .format(**locals() меняет все локальные шаблоны на переменные msisdn=msisdn
    # sql_query = f"""select * from subs_list_view where msisdn='{msisdn}'"""

    newline = '\n'  # Avoids SyntaxError: f-string expr cannot include a backslash
    sql = ''
    with open('sql/subs1005.sql', 'r') as file:
        for line in file:
            line = line.partition('--')[0]
            line = line.rstrip()
            sql += line + ' '
            sql_query5 = sql.format(**locals())

    df1005 = pd.read_sql_query(sql_query5, engine)
    print(df1005.head())
    if not df1005.empty:
        trpl_id = df1005.at[0, 'trpl_id']
    else:
        return templates.TemplateResponse("not_found.html",
                                          {"request": request,
                                           "msisdn": msisdn,
                                           "db": db
                                           })

    sql = ''
    with open('sql/subs1006.sql', 'r') as file:
        for line in file:
            line = line.partition('--')[0]
            line = line.rstrip()
            sql += line + ' '
            sql_query6 = sql.format(**locals())

    df1006 = pd.read_sql_query(sql_query6, engine)
    print(df1006.head())
    scenario_list = df1006['scenario_id'].tolist()
    scenario_id_list = ','.join([str(i) for i in scenario_list])

    sql = ''
    with open('sql/subs1002.sql', 'r') as file:
        # sql_query2 = f"{file.read().replace(newline, ' ')}".format(**locals())
        for line in file:
            line = line.partition('--')[0]
            line = line.rstrip()
            sql += line + ' '
            sql_query2 = sql.format(**locals())

    df111 = pd.read_sql_query(sql_query2, engine)
    df111 = df111.replace(np.nan, '', regex=True)

    # Write to XLSX
    excel_file_name = f'static/xls/{db}_{msisdn}.xlsx'

    writer = pd.ExcelWriter(excel_file_name)
    df111.to_excel(writer, sheet_name='main')
    df1006.to_excel(writer, sheet_name='scenario')

    writer.save()

    df111 = df111.replace(to_replace='(.*)((?i)Блокирова)(.*)', value='<font color="red">'+r"\1\2\3"+'</font>', regex=True)
    df111 = df111.replace(to_replace='(.*)((?i)active)(.*)', value='<font color="green">'+r"\1\2\3"+'</font>', regex=True)
    if 'trpl_serv' in df111.columns:
        df111.trpl_serv.replace(r'(.*)(Включить|Активна)(.*)', '<font color="green">'+r"\1\2\3"+'</font>', inplace=True, regex=True)
    df111.tname.replace(r'\_', ' ', inplace=True, regex=True)

    headings = list(df111.columns.values)
    data = list(df111.itertuples(index=False))

    return templates.TemplateResponse("msisdn_print.html",
                                      {"request": request,
                                       "msisdn": msisdn,
                                       "db": db,
                                       "headings": headings,
                                       "data": data
                                       })
# DONE: SQL вынести в отдельную папку и файл(ы)
# TODO: подключить sqlalchemy + basemodel
# DONE: head + foot
# DONE: большой селект
# TODO: remove comments from SQL test_reading
# TODO: open sql in new window
# TODO: sql - add TRPL_ID before trpl_ID
# TODO: sql - add SERV_ID before serv_id
# TODO: open TRPL route from trpl_id link
# TODO: open SERVICE route from serv_id link
# TODO: sql - check ORDER time
# TODO: sql - check DBs list
# TODO: sql - select DBs list to Jinja2 template


