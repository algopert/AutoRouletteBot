# import time
# start = time.time()

# time.sleep(10)  # or do something more productive

# done = time.time()
# elapsed = done - start
# print(elapsed)


# from datetime import datetime, date

# now = datetime.now()
# d = date(2022,3,24)
# now =now.date()
# if now > d:
#     print("Yes")
# else:
#     print("No")

# # Current date time in local system
# print(datetime.now())


# essen_list = ["Speed Auto Roulette", "Auto Roulette"]
# ttt ="Auto Roulette"

# print(ttt in essen_list)

# def list_test(a):
#     a.append(5)

# q= [1,2,4]
# print(q)
# list_test(q)
# print(q)

# def find_index_list(tgt, src):
#     tlen = len(tgt)
#     slen = len(src)
#     for i in range(tlen - slen+1):
#         if tgt[i:i+slen] == src:
#             return i
#     return -1

# def numbers_propagation(org_list, cur_list):
#     temps = org_list.copy()
#     temps.reverse()
#     sp = 7
#     fidx = find_index_list(temps, cur_list[sp:])
#     if fidx > sp or fidx < 0:
#         org_list = cur_list.copy()
#         org_list.reverse()
#         return -1

#     fidx = sp - fidx

#     for jj in range(fidx):
#         org_list.append(cur_list[fidx-jj-1])

#     while len(org_list) > 15:
#         org_list.pop(0)

#     return fidx


# org = [9, 10, 20, 33, 22, 29, 27, 5, 2, 19]
# cur = [26, 19, 2, 5, 27, 29, 22, 33, 20, 10]

# xx = numbers_propagation(org, cur)
# print(xx)
# print(org)


# import re
# new_string = 'Nomoney '
# new_result = re.findall('[0-9.]+', new_string)
# print(new_result[0])


# import csv

# header = ['name', 'area', 'country_code2', 'country_code3']
# data = ['Afghanistan', 652090, 'AF', 'AFG']

# with open('countries.csv', 'w', encoding='UTF8') as f:
#     writer = csv.writer(f)

#     # write the header
#     writer.writerow(header)

#     # write the data
#     writer.writerow(data)


#######################   delete file example ##################################
# import os
# folder = './analyze_result'
# for filename in os.listdir(folder):
#     file_path = os.path.join(folder, filename)
#     try:
#         if os.path.isfile(file_path) or os.path.islink(file_path):
#             os.unlink(file_path)
#     except:
#         print("error")


######################  number extract example #################################

# import re
# _chips_list = [None,
#                'chipsPanel.chip50',
#                'chipsPanel.chip100',
#                'chipsPanel.chip500',
#                'chipsPanel.chip1000',
#                'chipsPanel.chip2500',
#                'chipsPanel.chip10000',
#                'chipsPanel.chip50000',
#                'chipsPanel.chip100000',
#                None]
# for _chip in _chips_list:
#     if _chip == None:
#         xx=0
#     else:
#         xx = int(re.findall('[0-9]+', _chip)[0])
#     print(xx)
# from decimal import Decimal

# chip = [13, 18, 24, 24, 36, 15, 8, 23, 34, 24, 5000]
# A = ['$' + str(Decimal(str(x/100.0)).normalize()) for x in chip]
# print(A)




# print(round(1000.0,1))


# import sys
# from termcolor import colored, cprint
 
# text = colored('Hello, World!', 'red', attrs=['reverse', 'blink'])
# print(text)
# cprint('Hello, World!', 'green', 'on_red')
 
# print_red_on_cyan = lambda x: cprint(x, 'red', 'on_cyan')
# print_red_on_cyan('Hello, World!')
# print_red_on_cyan('Hello, Universe!')
 
# for i in range(10):
#     cprint(i, 'magenta', end=' ')
 
# cprint("Attention!", 'red', attrs=['bold'], file=sys.stderr)

import re

text = "  1, 3, 10, 30, 90, 270, 810 "
sr = [int(s) for s in re.findall(r'\b\d+\b', text)]
print(sr)
