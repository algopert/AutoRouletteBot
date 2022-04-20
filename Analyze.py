import os
import csv

folder = './analyze_result'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    except:
        print("error")
        

gdata= {}
result = {}
MAX_LENGTH = 20
condition_list = {"Red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
                  "Black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
                  "Odd": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
                  "Parity": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
                  "Low": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                  "High": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]}

_path = './history'
for sub_dir in os.listdir(_path):
    # print(sub_dir)
    real_path = _path + '/' + sub_dir
    gdata = {}
    for file in os.listdir(real_path):
        if not file.endswith(".csv"):
            continue
        con_file = open(real_path + '/' + file, 'r')
        Lines = con_file.readlines()
        con_file.close()
        _key = file[:-4]
        gdata[_key] = list(map(int, Lines))
        
    with open('./analyze_result/'+sub_dir + '.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        header = ['Game Title']
        for key in condition_list.keys():
            for i in range(MAX_LENGTH-1):
                _item = key + str(i+1)
                header.append(_item)
        writer.writerow(header)
        
        for _title in gdata.keys():
            # 
            my_row = []
            my_row.append(_title)
            series = gdata[_title]
            try:
                result[_title]
            except:
                result[_title] = {}

            for key in condition_list.keys():
                try:
                    result[_title][key]
                except:
                    result[_title][key] = 0
                cnt = [0] * MAX_LENGTH
                
                st_pos = 0
                        
                while st_pos<len(series):
                    if not series[st_pos] in condition_list[key]: 
                        st_pos +=1
                        continue
                    end_pos = st_pos + 1

                    try:
                        while series[end_pos] in condition_list[key]:
                            end_pos += 1
                    except:
                        break
                    cnt[end_pos - st_pos] += 1
                    st_pos = end_pos
                for i in range(MAX_LENGTH-1):
                    my_row.append(cnt[i+1])
                    if cnt[i+1]!=0 and i+1> result[_title][key]:
                        result[_title][key] = i+1
                    # print (f"\t{key} {i}  -> {cnt[i]}")
                    
                # break
            
            writer.writerow(my_row)
                    
                # print(f"{_title}")
                # print(len(gdata[_title]))
            
print(result)

with open('./analyze_result/result.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    header = ['Game Title']
    for cond_key in condition_list.keys():
        header.append(cond_key)
    writer.writerow(header)
    for title_key in result.keys():
        _row = [title_key]
        for cond_key in condition_list.keys():
            _row.append(result[title_key][cond_key])
        writer.writerow(_row)
    