from email import header
import os
import csv
from pathlib import Path
import shutil

folder = './analyze_result'
####################################
####      remove all folers     ####
#####vvvvvvvvvvvvvvvvvvvvvvvv#######
##
try:
    shutil.rmtree(folder)
except OSError as e:
    print("Error: %s : %s" % (folder, e.strerror))

Path(folder).mkdir(parents=True, exist_ok=True)
skip_titles = 'Triumph_French_Roulette , Football_French_Roulette, French_Roulette , Zero_test'
skip_list = skip_titles.replace(' ', '').split(',')

######^^^^^^^^^^^^^^^^^^^^^^#######

gdata = {}
max_limit_result = {}
MAX_LENGTH = 35
condition_list = {"Red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
                  "Black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
                  "Odd": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
                  "Parity": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
                  "Low": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                  "High": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],}
                #   "Dozen12": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                #   "Dozen13": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                #   "Dozen23": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                #   "Column12": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
                #   "Column13": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
                #   "Column23": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]}


def change_color_text(_list):
    _text = ""
    for dd in _list:
        if dd in condition_list["Red"]:
            _text += f'\033[91m {dd}  \033[0m'
        elif dd == 0:
            _text += '\033[92m0  \033[0m'
        elif dd == -1:
            _text += '\033[92mB  \033[0m'
        else:
            _text += str(dd)+'  '

    return _text


real_path = './backtest_data'
history_data = {}


gdata = {}
for file in os.listdir(real_path):
    if not file.endswith(".csv"):
        continue
    con_file = open(real_path + '/' + file, 'r')
    Lines = con_file.readlines()
    con_file.close()

    _game_title = file[:-4]
    if _game_title in skip_list:
        continue
    try:
        gdata[_game_title] = list(map(int, Lines))
    except:
        continue

# sort raw data to _cond_key data

adata = {}
cnt = {}

for _title in gdata.keys():

    series = gdata[_title]

    slen = len(series)

    for _cond_key in condition_list.keys():
        # print(_cond_key)
        st_pos = 0
        while st_pos < slen:
            if not series[st_pos] in condition_list[_cond_key]:
                st_pos += 1
                continue
            end_pos = st_pos + 1
            try:
                while series[end_pos] in condition_list[_cond_key]:
                    end_pos += 1
            except:
                break

            tlen = end_pos - st_pos
            ssp = st_pos # - 5
            eep = end_pos + 1
            if ssp < 0:
                ssp = 0
            st_pos = end_pos
            if tlen < 14:
                continue
            

            # print("Yes")
            try:
                adata[_title]
            except:
                adata[_title] = {}
                cnt[_title] = {}

            try:
                adata[_title][_cond_key]
            except:
                adata[_title][_cond_key] = {}
                cnt[_title][_cond_key] = {}

            try:
                cnt[_title][_cond_key][tlen]
            except:
                cnt[_title][_cond_key][tlen] = 0
                adata[_title][_cond_key][tlen] = {}
            # print(_title, _cond_key, tlen)
            adata[_title][_cond_key][tlen][cnt[_title][_cond_key][tlen]] = series[ssp: eep]

            cnt[_title][_cond_key][tlen] += 1

            


# print(cnt)
# quit()

for _title in adata.keys():
# _title = 'Age_Of_The_Gods_Bonus_Roulette'
    for _cond_key in adata[_title].keys():
        # _cond_key = "Red"
        for tlen in adata[_title][_cond_key].keys():
            # if tlen < 10 :
            #     continue
            for idx in adata[_title][_cond_key][tlen]:
                print('"'+ _title + '" :  ', _cond_key, tlen,' ------ :  ', change_color_text(adata[_title][_cond_key][tlen][idx]))

