from email import header
import os
import csv
from pathlib import Path
import shutil



folder = './backtest_data'
####################################
####      remove all folers     ####
#####vvvvvvvvvvvvvvvvvvvvvvvv#######
##
try:
    shutil.rmtree(folder)
except OSError as e:
    print("Error: %s : %s" % (folder, e.strerror))

Path(folder).mkdir(parents=True, exist_ok=True)   


# with open(filename, 'a') as f:  # save first input of series

_path = './history'
history_data = {}
time_stamp_list = os.listdir(_path)

filenames = {}
for _time_stamp in time_stamp_list:
    # print(_time_stamp)
    real_path = _path + '/' + _time_stamp
    gdata = {}
    for _title in os.listdir(real_path):
        if not _title.endswith(".csv"):
            continue
        con_file = open(real_path + '/' + _title, 'r')
        Lines = con_file.readlines()
        con_file.close()
        
        if _title=='':
            continue
        
        try:
            filenames[_title]
        except:
            filenames[_title] = 'backtest_data/'+ _title
            with open(filenames[_title], 'w+') as f:
                f.close()

        with open(filenames[_title], 'a') as f:  # save first input of series
            f.write('-2\n')
            for _item in Lines:
                # print(Lines)
                    f.write(_item)
            f.close()
