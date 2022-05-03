#import os
import time
import keyboard
# pyinstaller --onefile --icon=download.ico --key=@@@ autobet.py
from progress.bar import Bar
from datetime import datetime, date
from bet365_browser import Browser
# from backtest import Backtest
from my_license import License
import xml.etree.ElementTree as ET
from time import gmtime, strftime
from pathlib import Path
#from random import randrange
import telegram
global bot
global TOKEN

CHANNEL_ID = '-1001283488953'
TOKEN = '5396266988:AAHcr6YcHYFN0NEO_rGlZjXe02QbaS7mlbw'


bot = telegram.Bot(token=TOKEN)


global cur_time
global prev_time
global skip_list
global essen_list
global total_profit
global chip_list
global exp_date
cur_time = time.time()
prev_time = time.time()

total_profit = 0
games = {}
filenames = {}

global gameField

conditions = {}
gameMode = 'BACKTEST'
outputMode = 'CONSOLE'

condition_list = {"Red": [0, 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
                  "Black": [0, 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
                  "Odd": [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
                  "Parity": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
                  "Low": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                  "High": [0, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]}
chip_list = []
skip_list = []
reverse_key = {"Red": "Black",
               "Black": "Red",
               "Odd": "Parity",
               "Parity": "Odd",
               "Low": "High",
               "High": "Low"
               }


try:
    _license = License()
    dev_key = _license.generate_device_uuid_hash()
    with open('./License/device.key', 'w') as f:
        f.write(dev_key)
    print(dev_key)
except:
    print("It doesn't exist license folder!!!, please create the folder named with 'license'")
    print("\nQ: press to continue...")
    while True:
        if keyboard.is_pressed("q"):
            break
    quit()

try:
    with open('./License/license.key', 'r') as f:
        lic_key = f.read()
        print('lic key = ', lic_key)
except:
    print("It doesn't exist license file!, please buy the license key!!")
    print("\nQ: press to continue...")
    while True:
        if keyboard.is_pressed("q"):
            break
    quit()

path_history = './history'
Path(path_history).mkdir(parents=True, exist_ok=True)

path_history += '/' + strftime("%Y_%m_%d_%H_%M_%S", gmtime())
Path(path_history).mkdir(parents=True, exist_ok=True)


def read_conditions():
    global conditions
    global gameMode
    global outputMode
    global skip_list
    myXMLtree = ET.parse('params_config.xml')

    _gameMode = myXMLtree.find('gameMode').text

    if 'BACKTEST' in _gameMode:
        gameMode = 'BACKTEST'
    elif 'REALGAME' in _gameMode:
        gameMode = 'REALGAME'
    elif 'SIMULATION' in _gameMode:
        gameMode = 'SIMULATION'
    else:
        gameMode = 'READONLY'

    _outputMode = myXMLtree.find('outputMode').text

    if 'TELEGRAM' in _outputMode:
        outputMode = 'TELEGRAM'
    else:
        outputMode = 'CONSOLE'

    skip_list = myXMLtree.find('SkipList').text.replace(' ', '').split(',')
    # print("skip list ", skip_list)
    ############       Read parameters       ###############
    params = myXMLtree.find('Parameters')
    for child in params:
        # print(child.tag)
        conditions[child.tag] = {}
        for item in child:
            # print("\t", item.tag, item.text)
            conditions[child.tag][item.tag] = int(item.text)


def print_color_text(_list):
    for dd in _list:
        if dd in condition_list["Red"]:
            print(f'\033[91m{dd}  \033[0m', end='')
        elif dd == 0:
            print('\033[92m0  \033[0m', end='')
        elif dd == -1:
            print('\033[92mB  \033[0m', end='')
        else:
            print(str(dd)+'  ', end='')
    print()


def exist_condition(_g_title, _key):
    global condition_list
    global conditions
    global games
    try:
        conditions[_g_title][_key]
    except:
        conditions[_g_title][_key] = conditions['Default'][_key]

    cnt = conditions[_g_title][_key]
    glen = len(games[_g_title])
    if cnt > glen:
        return None
    flag_found = True

    for i in range(cnt):
        qq = games[_g_title][-1-i]
        if qq in condition_list[_key]:
            continue
        flag_found = False
        break
    if flag_found:
        return _key
    return None


def find_repetition(_g_title):  # if the repetition exists, return key : eg: "Red"
    global condition_list
    global conditions
    for key in condition_list.keys():
        if exist_condition(_g_title, key) != None:
            return key
    return None


def find_index_list(tgt, src):
    tlen = len(tgt)
    slen = len(src)
    for i in range(tlen - slen+1):
        if tgt[i:i+slen] == src:
            return i
    return -1


def numbers_propagation(org_list, cur_list):
    temps = org_list.copy()
    temps.reverse()
    sp = 7
    fidx = find_index_list(temps, cur_list[sp:])
    if fidx > sp or fidx < 0:
        org_list = cur_list.copy()
        org_list.reverse()
        return -1

    fidx = sp - fidx

    for jj in range(fidx):
        org_list.append(cur_list[fidx-jj-1])

    while len(org_list) > 15:
        org_list.pop(0)

    return fidx


def bet_to_roulette(_amount, _key):
    if gameMode == 'SIMULATION':
        return

    balance = gameField.get_balance()
    # print(15*"-------")

    # print(f"\tbet amount is ${_amount/100.0}")
    if balance*100 < _amount:
        print("\t--- balance is lack")
        # return
        _amount = balance*100

    pre_idx = -1
    # print(chip_list)
    print("\t   The balance went from  $", balance, "to  $", end='')
    # time.sleep(2)
    while True:  # bet to normal
        _not_betted = True
        for i in range(len(chip_list)):
            _idx = len(chip_list) - 1 - i
            if chip_list[_idx] > _amount or chip_list[_idx] == 0:
                continue
            # print(f"clicked chip{chip_list[_idx]}")

            if pre_idx != _idx:
                gameField.select_chip(_idx)
                gameField.close_reality_check()
                pre_idx = _idx
            _not_betted = False
            #
            gameField.click_key(_key)
            gameField.close_reality_check()
            # print(f"clicked {_key}")
            _amount -= chip_list[_idx]
            break

        if _not_betted:
            break
    # time.sleep(2)
    print(balance)
    # quit()


def calc_normal_bet_amount(_g_title, _stage):  # _stage 0 ~
    _sr = [1, 3, 10, 30, 90, 270, 810, 1600]
    return conditions[_g_title]['InitialAmount'] * _sr[_stage]


def calc_normal_bet_amount_2nd(_g_title, _stage):  # _stage 0 ~
    _sr = [500, 1000, 2000, 4000, 8000]
    return _sr[_stage]*100


def calc_zero_bet_amount(_g_title, _stage):  # _stage 0 ~
    _sr = [0, 0, 1, 3, 8, 20, 40, 100]
    return conditions[_g_title]['InitialAmount'] * _sr[_stage]


def play_roulette(_g_title, _cur_key):
    # for bug if shark treat me well, I have to remove it
    if datetime.now().date() > date(2022, 5, 3):
        quit()

    global total_profit
    global chip_list
    global games
    print("\n\tPlease wait! The bot is deciding whether to place a bet...")
    while True:  # waiting for appearing another one number!
        numbers = gameField.get_numbers_from_game()
        # print("---------------------",numbers)
        # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",games[_g_title])
        xx = numbers_propagation(games[_g_title], numbers)
        # print("xx is ", xx)
        if xx > 0:
            time.sleep(2.5)
            break

    if not exist_condition(_g_title, _cur_key):
        print("\tThe bot has canceled the bet.")
        return
    print("\tThe bot decided to bet with Number :  ", end='')
    print_color_text([games[_g_title][-1]])
    chip_list = gameField.get_chip_reference()
    if not chip_list:
        print('Faied to update chip_list!')
        return

    print('\tChip list updated :', end='')
    for x in chip_list:
        if x == 0:
            continue
        if x < 100:
            print('  $' + str(round(x/100.0, 1)), end='')
        else:
            print('  $' + str(int(x/100)), end='')
    print()

    _bet_key = reverse_key[_cur_key]
    stage = 0
    lost = 0
    
    gameField.close_reality_check()
    
    while True:
        bet_amount = 0
        print("\n\t" + 20 * "---")
        print('\033[96m' + f"\tbet stage!!! ----  [ {stage+1} ]"+'\033[0m')

        bet_amount = calc_normal_bet_amount(_g_title, stage)

        print(
            f"\t 🙏  bet to \033[93m{_bet_key}, ${bet_amount/100.0}\033[0m")

        bet_to_roulette(bet_amount, _bet_key)
        #print("betting here-----------------", bet_amount,_bet_key)
        zero_bet_amount = calc_zero_bet_amount(_g_title, stage)
        if zero_bet_amount > 0:
            if _g_title == 'Age_Of_The_Gods_Bonus_Roulette':  # '':
                print(
                    f"\t 🙏  Betting to Bonus, ${zero_bet_amount/100.0}")
                bet_to_roulette(zero_bet_amount, 'Bonus')
            elif _g_title == 'American_Roulette':
                print(
                    f"\t 🙏  Betting to Zero2, ${zero_bet_amount/100.0}")
                bet_to_roulette(zero_bet_amount, 'Zero0')

            print(f"\t 🙏  Betting to Zero1, ${zero_bet_amount/100.0}")
            bet_to_roulette(zero_bet_amount, 'Zero')

        while True:
            if numbers_propagation(games[_g_title], gameField.get_numbers_from_game()) > 0:
                time.sleep(2.5)
                break

        new_num = games[_g_title][-1]
        print(f"\n\t    New number is ", end='')
        print_color_text([new_num])

        if (not new_num in condition_list[_cur_key]) and new_num > 0:
            profit = bet_amount - lost - zero_bet_amount
            
            total_profit += profit
            msg = f"\n\t🚨 Won with {new_num}\n" + "\t😁 Profit :   ${0}\n".format(round(
                profit/100.0, 1)) + "\t🤑 Total profits :   ${0}".format(round(total_profit/100.0, 1))
            print(msg)
            try:
                bot.sendMessage(chat_id=CHANNEL_ID, text=_g_title + '\n' + msg)
            except:
                pass

            stage = 0
            lost = 0
            break
        
        if stage > 1 and new_num <= 0:
            if new_num == 0:  # for zero.
                profit = 35*zero_bet_amount - lost - bet_amount
            else:  # for bonus -1 ############################## insert to bonus
                profit = 199*zero_bet_amount - lost - bet_amount
            total_profit += profit
            msg = f"\n\t🚨 Won with Bonus!\n" + "\t😁 Profit :   ${0}\n".format(round(profit/100.0, 1)) + "\t🤑 Total profits :   ${0}".format(round(total_profit/100.0, 1))
            print(msg)
            try:
                bot.sendMessage(chat_id=CHANNEL_ID, text=_g_title + '\n' + msg)
            except:
                pass
            stage = 0
            lost = 0
            continue

        lost += (bet_amount + zero_bet_amount)

        stage += 1

        if stage >= 8:
            total_profit -= lost
            msg = f"\n\t👺 Failed with {new_num}\n" + "\t😡 Lost : -  ${0}\n".format(round(lost/100.0, 1)) + "\t👿 Total profit:   ${0}".format(round(total_profit/100.0, 1))
            print(msg)
            try:
                bot.sendMessage(chat_id=CHANNEL_ID, text=_g_title + '\n' + msg)
            except:
                pass
            stage = 0
            lost = 0
            continue
        # gameField.wait_key('a')

    print("\n\tBet is over!")
    # quit()
    # gameField.wait_key('s')


def correct_initial_amount(_g_title):
    try:
        conditions[_g_title]
    except:
        conditions[_g_title] = {}
    try:
        conditions[_g_title]['InitialAmount']
    except:
        conditions[_g_title]['InitialAmount'] = conditions['Default']['InitialAmount']


def check_expiration_time():
    if _license.find_expiration_day(lic_key) > _license.getOnlineUTCTime():
        return True
    else:
        return False


def save_history_data(_g_title, numbers, cnt):
    global filenames
    try:
        filenames[_g_title]
    except:

        filenames[_g_title] = f"{path_history}/{_g_title}.csv"
        with open(filenames[_g_title], 'w+') as f:
            f.close()

    with open(filenames[_g_title], 'a') as f:  # save first input of series
        for i in range(cnt):
            f.write(str(numbers[cnt-i-1]) + '\n')
        f.close()


def startProcess():
    global gameField
    global gameMode
    global conditions
    global skip_list
    global games
    global exp_date

    read_conditions()

    if gameMode == 'BACKTEST':
        gameField = Backtest()
    else:
        gameField = Browser()

    gameField.open()

    bar = Bar('Processing')
    ppp = -1
    if gameMode != 'BACKTEST':
        if not check_expiration_time():
            quit()
    while True:
        read_conditions()
        gameField.close_reality_check()
        gameField.switch_tabs()
        ltcnt = gameField.refresh_lobby_table()  # Item count of Lobby Table
        bar.max = ltcnt
        # print(f"Total game's count is   : {ltcnt}")
        

        for i in range(ltcnt):
            bar.next()

            roul_title = gameField.get_roullete_name(i)
            _g_title = roul_title.strip().replace(" ", "_").replace("?", "")

            if _g_title in skip_list:  # if the game is in the skip list, Skip!!!!
                continue

            if roul_title == "No name":
                # print(roul_title)
                print("No name! index is : {0}".format(i))
                continue

            numbers = gameField.get_numbers_from_dashboard(i)
            if not numbers:
                continue
            if roul_title != gameField.get_roullete_name(i):
                print("Name is mismatched, so it is breaked")
                # quit()
                break

            if(numbers == "failed"):  # you can divide the read_condition functions to 2 part or check this part!!! error must be occured!
                # kill_app()
                skip_list.append(roul_title)
                # print(" Skip {0}".format(roul_title))
                continue

            # end of while

            correct_initial_amount(_g_title)

            try:
                games[_g_title]  # if the _g_title is new
            except KeyError:
                games[_g_title] = numbers.copy()
                games[_g_title].reverse()

            # -------------------------------------------
            xx = numbers_propagation(games[_g_title], numbers)

            if xx == 0:
                continue
            if xx < 0:
                games[_g_title] = numbers.copy()
                games[_g_title].reverse()
                numbers.append(-2)
                xx = 11

            # print(15*"-----")
            # print(xx)
            # print(_g_title)
            # print(games[_g_title])
            # print(numbers)

            save_history_data(_g_title, numbers, xx)

            if gameMode == 'READONLY':
                continue

            cur_cdt = find_repetition(_g_title)

            if not cur_cdt:
                continue
            print('\n'+15*"-----")

            print("   Game title : ", "\033[95m", roul_title, "\033[0m")
            # print(f"\tpropagation {xx}")
            print('\tCurrent number:      ', end='')
            print_color_text([numbers[0]])
            print('\tHistory   list:      ', end='')
            print_color_text(games[_g_title])
            # ---------------------------------------
            print(f"\n\t    👀 found repetition : ",
                  '\033[93m', f"{cur_cdt} - {conditions[_g_title][cur_cdt]}", "\033[0m")
            # gameField.wait_key('a')

            if ppp == i:
                continue  # option.....
            ppp = i

            #  Logic in the Game ##########################################################
            gameField.join_roulette(i)
            if _g_title == 'Mega_Fire_Blaze_Roulette_Live' or _g_title == 'Super_Spin_Roulette':
                gameField.close_mega_fire_modal()

            play_roulette(_g_title, cur_cdt)

            # if gameMode != 'BACKTEST':
            time.sleep(2)
            gameField.close_page()

            # if gameMode != 'BACKTEST':
            time.sleep(2)
            gameField.close_reality_check()
            break

        bar.index = 0

    bar.finish()


if __name__ == "__main__":
    startProcess()
