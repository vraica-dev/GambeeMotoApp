import pandas as pd
import sqlite3
from config import Config


class DataExporter:
    def __init__(self, active_user, query_type):
        self.active_user = active_user
        self.DB_ADDRESS = None
        self.data_df = None
        self.OUTPUT_PATH = f'application/temp_files/data_{query_type}.csv'

        self.connx = None
        self.query_sql = self.__getSQL(query_type)

        self.__read_db()

    def __read_db(self):
        try:
            self.DB_ADDRESS = 'application/tripsDB.sqlite3'
            self.connx = sqlite3.connect(self.DB_ADDRESS)
        except Exception as e:
            print(e.__doc__)

    def close_connx(self):
        if self.connx is not None:
            self.connx.close()

    def __getSQL(self, tb_name):
        sql_string = ''
        user_selected = self.active_user

        if self.active_user == Config.ADMIN_USER:
            user_selected = "%"

        if tb_name == 'trips':
            sql_string = 'SELECT * FROM TripRecords WHERE added_by LIKE "' + user_selected + '" '
        elif tb_name == 'events':
            sql_string = 'SELECT * FROM Mechanical_Tab WHERE event_owner LIKE "' + user_selected + '" '
        return sql_string

    def load_df(self):
        temp_df = pd.read_sql(self.query_sql, self.connx)
        if temp_df is not None:
            self.data_df = temp_df

    def export_df(self):
        self.data_df.to_csv(self.OUTPUT_PATH, index_label=False)


