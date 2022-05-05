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
skip_titles = 'Triumph_French_Roulette , Football_French_Roulette, French_Roulette , Who_Wants_To_Be_a_Millionaire_Roulette, Speed_Auto_Roulette, bet365_Dutch_Roulette, Mega_Fire_Blaze_Roulette_Live, Zero_test'
skip_list = skip_titles.replace(' ', '').split(',')

######^^^^^^^^^^^^^^^^^^^^^^#######

gdata= {}
max_limit_result = {}
MAX_LENGTH = 35
condition_list = {"Red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
                  "Black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
                  "Odd": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
                  "Parity": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
                  "Low": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                  "High": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                  "Dozen12": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                  "Dozen13": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                  "Dozen23": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                  "ColumnBtmMid": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
                  "ColumnBtmTop": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
                  "ColumnMidTop": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]}

#############################################################################
##### read the data from history folder and change it to pattern data #######
##### in the meantime, it analyze the maximum length of entire period #######
#############################################################################
## VVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
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
        _game_title = file[:-4]
        if _game_title in skip_list:
            continue
        try:
            gdata[_game_title] = list(map(int, Lines))
        except:
            continue
            
    if gdata =={}:
        print(_game_title, _time_stamp)
    
    #sort raw data to _cond_key data
    for _title in gdata.keys():
        series = gdata[_title]
        try:
            max_limit_result[_title]
        except:
            max_limit_result[_title] = {}
        try:
            history_data[_title]
        except:
            history_data[_title] = {}
        
        try:
            history_data[_title][_time_stamp]
        except:
            history_data[_title][_time_stamp] = {}
        
        for _cond_key in condition_list.keys():
            try:
                max_limit_result[_title][_cond_key]
            except:
                max_limit_result[_title][_cond_key] = 0
            cnt = [0] * MAX_LENGTH
            
            st_pos = 0
                    
            while st_pos<len(series):
                if not series[st_pos] in condition_list[_cond_key]: 
                    st_pos +=1
                    continue
                end_pos = st_pos + 1

                try:
                    while series[end_pos] in condition_list[_cond_key]:
                        end_pos += 1
                except:
                    break
                cnt[end_pos - st_pos] += 1
                st_pos = end_pos
                
            history_data[_title][_time_stamp][_cond_key]= cnt
            for i in range(MAX_LENGTH-1):
                if cnt[i+1]!=0 and i+1> max_limit_result[_title][_cond_key]:
                    max_limit_result[_title][_cond_key] = i+1
############## ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  ####################


#######################################################
##############  max limit analysis output #############
#######################################################
with open('./analyze_result/result_max_limit.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    header = ['Game Title']
    for cond_key in condition_list.keys():
        header.append(cond_key)
    writer.writerow(header)
    for title_key in max_limit_result.keys():
        _row = [title_key]
        for cond_key in condition_list.keys():
            _row.append(max_limit_result[title_key][cond_key])
        writer.writerow(_row)


###################################################    
##############    daily analysis   ################
###################################################
for _time_stamp in time_stamp_list:
    for _title in history_data.keys():    
        sub_folder = folder + '/daily/' + _time_stamp
        Path(sub_folder).mkdir(parents=True, exist_ok=True)
        with open(sub_folder+'/'+_title + '.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            _header = ['']
            for i in range(MAX_LENGTH-1):
                _header.append(str(i+1))
            writer.writerow(_header)
            for _cond_key in condition_list.keys():
                _row = [_cond_key]
                for i in range(MAX_LENGTH-1):
                    try:
                        _row.append(history_data[_title][_time_stamp][_cond_key][i+1])
                    except:
                        print("None exist",_title, _time_stamp, _cond_key)
                        quit()
                        break
                writer.writerow(_row)
                
##############################################################        
##########       total evaluation statistics     #############
##############################################################
sub_folder = folder + '/' + 'total_evalution'
Path(sub_folder).mkdir(parents=True, exist_ok=True)


# print(history_data[_title].keys())

for _title in history_data.keys():
    # print(_title)
    with open(sub_folder+'/'+_title + '.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        _header = ['']
        for i in range(MAX_LENGTH-1):
            _header.append(str(i+1))
        writer.writerow(_header)
        
        for _cond_key in condition_list.keys():
            cnt = [0] * MAX_LENGTH
            for _time_stamp in history_data[_title].keys():
                for i in range(MAX_LENGTH-1):
                    cnt[i+1] +=history_data[_title][_time_stamp][_cond_key][i+1]
            
            _row = [_cond_key]
            for i in range(MAX_LENGTH-1):
                try:
                    _row.append(cnt[i+1])
                except:
                    print("None exist",_title, _time_stamp, _cond_key)
                    quit()
                    
            writer.writerow(_row)
                    
##############################################################        
##########       total evaluation statistics     #############
##############################################################
sub_folder = folder + '/' + 'peak_per_history'
Path(sub_folder).mkdir(parents=True, exist_ok=True)

for _title in history_data.keys():
    with open(sub_folder+'/'+_title + '.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        _header = ['date']
        for _cond_key in condition_list.keys():
            _header.append(_cond_key)
        writer.writerow(_header)
        
        for _time_stamp in history_data[_title].keys():
            max_key = [_time_stamp]
            for _cond_key in condition_list.keys():
                for i in range(MAX_LENGTH-1):
                    if history_data[_title][_time_stamp][_cond_key][MAX_LENGTH - i - 1]!=0:
                        _max_value = MAX_LENGTH - i - 1
                        break
                max_key.append(str(_max_value))
            writer.writerow(max_key)
        
                
            
    
    
    
    
    
                        
                
    
    