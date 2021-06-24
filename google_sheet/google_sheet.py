from concurrent.futures import ThreadPoolExecutor, as_completed
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import os
import yaml
import pandas as pd
import numpy as np
import logging

class GoogleSheet:
    
    local_folder = os.path.dirname( __file__)
    config_name = "config.yaml"
    config_path = os.path.join(local_folder, config_name)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    keys = config["sheet_keys"]["telegram_bot"]
    
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    
    creds_name = "creds.json"
    creds_path = os.path.join(local_folder, creds_name)
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    
    def __init__(self, name):
        self.name = name
        
    @property
    def sheet(self) -> gspread.models.Worksheet:
        """
        Return sheet
        """
        try:
            return self._sheet
        except AttributeError:
            self._sheet = self.get_sheet()
            return self._sheet        
    
    def get_sheet(self) -> gspread.models.Worksheet:
        """
        Return sheet
        """
        key = self.keys.get(self.name)
        if key:
            return self.client.open_by_key(key).sheet1
        
    def get_df(self) -> pd.DataFrame:
        """
        Return df
        """
        return pd.DataFrame(self.sheet.get_all_records(default_blank=np.nan))
    
    def thread_run(self, func, values):
        res = {}
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(func, value):value for value in values}
            for future in as_completed(futures):
                res[futures[future]] = future.result()
        return res
    
    def get_df_by_range_names(self, range_names) -> pd.DataFrame:
        """
        Return df that columns match with range_names

        Args:
            range_names: List of wanted columns names
                         e.g. ['payment_receive_date', 'applied_time']
        """
        def get_data(col):
            return self.sheet.get(col)
        
        datas = self.thread_run(get_data, range_names)
        df = pd.concat((pd.DataFrame(datas[key], columns=[key]) for key in datas), axis=1)
        
        col_names = df.iloc[0].to_list()
        col_nums = self.get_col_nums(col_names)        
        df.iloc[0] = [col_nums[col_name] for col_name in col_names]
        
        return df[range_names]
    
    def get_col_nums(self, col_names) -> dict:
        """
        Return dictionary {column name: column number} that columns match with col_names

        Args:
            range_names: List of wanted columns names
                         e.g. ['payment_receive_date', 'applied_time']
        """
        sheet = self.sheet
        
        def get_col_num(col_name):
            row1 = sheet.row_values(1)
            col = row1.index(col_name) + 1
            return col
        
        return self.thread_run(get_col_num, col_names)
    
    def catch_api_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                logging.info(e)
            return
        return wrapper
        
    @catch_api_error
    def update_by_col_num(self, row, col_num, value) -> None:
        """
        Update spreadsheet value by inputing column number and row

        Args:
            row: row number
            col_num: column number
            value: value that you want to update
        """
        self.sheet.update_cell(row, col_num, value)
            
    @catch_api_error
    def update_by_col_name(self, row, col_name, value) -> None:
        """
        Update spreadsheet value by inputing column name and row

        Args:
            row: row number
            col_name: column name
            value: value that you want to update
        """
        sheet = self.sheet
        row1 = sheet.row_values(1)
        col = row1.index(col_name) + 1
        sheet.update_cell(row, col, value)
        
    # cell_values = [[row, col, value],]
    def gen_cells(self, cell_values):
        for row, col, value in cell_values:
            yield gspread.models.Cell(row, col, value)
    
    @catch_api_error
    def update_by_cells(self, cell_values) -> None:
        """
        Update spreadsheet cells(can multiple) by inputing row num, col num and value

        Args:
            cell_values: [[row number, col number, value],[row number, col number, value]]
        """
        cells = list(self.gen_cells(cell_values))
        self.sheet.update_cells(cells)
        
if __name__ == "__main__":
    # from google_sheet.google_sheet import GoogleSheet
    # g1 = GoogleSheet("register")
    # g2 = GoogleSheet("register_money_tab")
    import time
    g1 = GoogleSheet("Fixyou")
    while True:
        print(g1.get_df()['tg bot id'])
        print(g1.get_df_by_range_names(["tg_bot_id"]))
        print()
        time.sleep(5)
    # g1.update_by_col_name(3,"Email", "testing")
    # tg_arr = g1.get_df_by_range_names(["tg_bot_id"])
    # tg_arr = tg_arr.drop([0])
    # tg_arr = tg_arr["tg_bot_id"].to_list()
    # print(tg_arr)
    
    
    
    
    
    
    
    
    
    