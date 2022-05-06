from email import header
import os
import csv
from pathlib import Path
import shutil

folder = './analyze_result'


gdata= {}


filename = f"backtest_data/all_history.csv"
with open(filename, 'w+') as f:
    f.close()


with open(filename, 'a') as f:  # save first input of series
    _path = './history'
    history_data = {}
    time_stamp_list = os.listdir(_path)

    for _time_stamp in time_stamp_list:
        # print(_time_stamp)
        real_path = _path + '/' + _time_stamp
        gdata = {}
        for file in os.listdir(real_path):
            if not file.endswith(".csv"):
                continue
            con_file = open(real_path + '/' + file, 'r')
            Lines = con_file.readlines()
            con_file.close()
            f.write('-2\n')
            for _item in Lines:
                # print(Lines)
                f.write(_item)
    
    f.close()
    