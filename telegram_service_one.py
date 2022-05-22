import time

from progress.bar import Bar

from bet365_browser import Browser
from backtest import Backtest
import xml.etree.ElementTree as ET
from time import gmtime, strftime
from pathlib import Path
import telegram

global skip_list

CHANNEL_ID = {}
CHANNEL_ID['gold'] = '-1001640416979'
CHANNEL_ID['silver'] = '-1001627327757'
CHANNEL_ID['bronze'] = '-1001628795108'
TOKEN = '5363359521:AAG4p79YyooiqFgQnlxgcu73tFqUse8eH1k'

bot = telegram.Bot(token=TOKEN)

total_profit = 0
games = {}
filenames = {}

global gameField
global path_history
path_history = ''
conditions = {}
gameMode = 'BACKTEST'
outputMode = 'CONSOLE'

delta_level_val={"gold": 0, "silver": 3, "broze": 3}

condition_list = {"Red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
                  "Black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
                  "Odd": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
                  "Even": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
                  "Low": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                  "High": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                  "Dozen12": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                  "Dozen13": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                  "Dozen23": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                  "Column12": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
                  "Column13": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
                  "Column23": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]}


skip_list = []
reverse_key = {"Red": "Black",
               "Black": "Red",
               "Odd": "Even",
               "Even": "Odd",
               "Low": "High",
               "High": "Low",
               "Dozen12": "3rd-Dozen",
               "Dozen13": "2nd-Dozen",
               "Dozen23": "1st-Dozen",
               "Column12": "Top-Column",
               "Column13": "Middle-Column",
               "Column23": "Bottom-Column"
               }
text_key = {"Red": "RED",
            "Black": "BLACK",
            "Odd": "ODD",
            "Even": "EVEN",
            "High": "HIGH(19-36)",
            "Low": "LOW(1-18)",
            "Dozen12": "Dozen-1&2",
            "Dozen13": "Dozen-1&3",
            "Dozen23": "Dozen-2&3",
            "Column12": "Col-Mid&Btm",
            "Column13": "Col-Top&Btm",
            "Column23": "Col-Top&Mid"
            }


flag_save = False

length_view = 10

play_status = {}
riskLevel = 0
cdt_delta = {"D2": -2, "D1": -1, "MID": 0, "P1": 1, "P2": 2 , "P3": 3 }

def read_conditions():
    global conditions
    global gameMode
    global outputMode
    global skip_list
    global riskLevel
    myXMLtree = ET.parse('tele_params.xml')

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
    riskLevel = myXMLtree.find('riskLevel').text.replace(' ', '')
    skip_list = myXMLtree.find('SkipList').text.replace(' ', '').split(',')
    # print("skip list ", skip_list)
    ############       Read parameters       ###############
    params = myXMLtree.find('Parameters')
    for child in params:
        # print(child.tag)
        conditions[child.tag] = {}

        for item in child:
            # print("\t", item.tag, item.text)
            conditions[child.tag][item.tag] = {}
            conditions[child.tag][item.tag]['gold'] = int(item.text) - delta_level_val["gold"]
            conditions[child.tag][item.tag]['silver'] = int(item.text) - delta_level_val["silver"]
            conditions[child.tag][item.tag]['bronze'] = int(item.text) - delta_level_val["broze"]


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


def exist_condition(_g_title, _key, _level):
    global condition_list
    global conditions
    global games
    try:
        conditions[_g_title]
    except:
        conditions[_g_title] = {}
    try:
        conditions[_g_title][_key]
    except:
        conditions[_g_title][_key] = {}
        conditions[_g_title][_key]['gold'] = conditions['Default'][_key]['gold']
        conditions[_g_title][_key]['silver'] = conditions['Default'][_key]['silver']
        conditions[_g_title][_key]['bronze'] = conditions['Default'][_key]['bronze']

    try:
        play_status[_g_title]
    except:
        play_status[_g_title] = {}
        play_status[_g_title]["flag"] = {}
        play_status[_g_title]["flag"]['gold'] = False
        play_status[_g_title]["flag"]['silver'] = False
        play_status[_g_title]["flag"]['bronze'] = False
        play_status[_g_title]["condition"] = {}
        play_status[_g_title]["condition"]['gold'] = None
        play_status[_g_title]["condition"]['silver'] = None
        play_status[_g_title]["condition"]['bronze'] = None

        play_status[_g_title]["stage"] = {}
        play_status[_g_title]["stage"]['gold'] = 0
        play_status[_g_title]["stage"]['silver'] = 0
        play_status[_g_title]["stage"]['bronze'] = 0
        play_status[_g_title]["series"] = {}
        play_status[_g_title]["series"]['gold'] = []
        play_status[_g_title]["series"]['silver'] = []
        play_status[_g_title]["series"]['bronze'] = []

    cnt = conditions[_g_title][_key][_level] + cdt_delta[riskLevel]
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


# if the repetition exists, return key : eg: "Red"
def find_repetition(_g_title, _level):
    global condition_list
    global conditions
    for key in condition_list.keys():
        if exist_condition(_g_title, key, _level) != None:
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
    sp = 3
    fidx = find_index_list(temps, cur_list[sp:])
    if fidx > sp or fidx < 0:
        org_list = cur_list.copy()
        org_list.reverse()
        return -1

    fidx = sp - fidx

    for jj in range(fidx):
        org_list.append(cur_list[fidx-jj-1])

    while len(org_list) > 50:
        org_list.pop(0)

    return fidx


def save_history_data(_g_title, numbers, cnt):
    if gameMode == 'BACKTEST':
        return
    global flag_save
    global path_history
    if not flag_save:
        path_history = './history'
        Path(path_history).mkdir(parents=True, exist_ok=True)

        path_history += '/' + strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        Path(path_history).mkdir(parents=True, exist_ok=True)
        flag_save = True
        
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


def send_first_message(_g_title, _cur_cdt, _level):
    _cur_series = str(games[_g_title][-length_view:]).strip("[]")
    _cur_series = _cur_series.replace('-1,', 'B,')
    _title = _g_title.replace('_', ' ')
    txt = f"🚨 Room Title: {_title}\n📊 Current Series : {_cur_series}\n👀 Repetition found: {text_key[_cur_cdt]} - {conditions[_g_title][_cur_cdt][_level] + cdt_delta[riskLevel]}\n🙏 Let's join and Bet on: {reverse_key[_cur_cdt]}  !!!"
    if gameMode == "REALGAME":
        try:
            bot.sendMessage(chat_id=CHANNEL_ID[_level], text=txt)
        except:
            print("try again(request telegram1)")
    print(f"----------->  {_level}")
    print(txt)
    time.sleep(0.5)


def send_second_message(_g_title, _cur_cdt, _level):
    _moves = str(play_status[_g_title]["series"][_level]).strip("[]")
    _moves = _moves.replace('-1', 'B')
    _cur_series = str(games[_g_title][-length_view:]).strip("[]")
    _cur_series = _cur_series.replace('-1', 'B')
    _title = _g_title.replace('_', ' ')
    txt = f"🏁 Finished - {_title}\n📊 Current Series : {_cur_series}\n👀 Repetition was: {text_key[_cur_cdt]}\n⚡️ Moves: {_moves}\n🤑 We won with the number: {games[_g_title][-1]}"
    if gameMode == "REALGAME":
        try:
            bot.sendMessage(chat_id=CHANNEL_ID[_level], text=txt)
        except:
            print("try again(request telegram1)")
    print(f"----------->  {_level}")
    print(txt)
    time.sleep(0.5)


def send_middle_message(_g_title, _cur_cdt, _level):
    _moves = str(play_status[_g_title]["series"][_level]).strip("[]")
    _moves = _moves.replace('-1', 'B')
    _cur_series = str(games[_g_title][-length_view:]).strip("[]")
    _cur_series = _cur_series.replace('-1', 'B')
    _title = _g_title.replace('_', ' ')
    if games[_g_title][-1] < 0:
        _hit = 'B'
    else:
        _hit = '0'
    print(f"----------->  {_level}")
    txt = f"👉 - {_title}\n🤑 Wow, You are Lucky! Ball landed in the {_hit}\n📊 Current Series : {_cur_series}\n👀 Repetition is: {text_key[_cur_cdt]}\n⚡️ Moves: {_moves}\n❗ Quit with or without the profit!"
    if gameMode == 'REALGAME':
        try:
            bot.sendMessage(chat_id=CHANNEL_ID[_level], text=txt)
        except:
            print("try again(request telegram1)")
    print(txt)
    time.sleep(0.5)


def startProcess():
    global gameField
    global gameMode
    global conditions
    global skip_list
    global games

    read_conditions()

    if gameMode == 'BACKTEST':
        gameField = Backtest()
    else:
        gameField = Browser()

    gameField.open()

    bar = Bar('Processing')

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
                skip_list.append(roul_title)
                continue

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

            new_num = games[_g_title][-1]
            if gameMode == 'REALGAME':
                save_history_data(_g_title, numbers, xx)

            levels = ['gold'] #[, 'silver', 'bronze']
            #levels = ['silver']
            for my_level in levels:
                cur_cdt = find_repetition(_g_title, my_level)

                if cur_cdt and not play_status[_g_title]["flag"][my_level]:
                    play_status[_g_title]["flag"][my_level] = True
                    play_status[_g_title]["stage"][my_level] = 0
                    play_status[_g_title]["series"][my_level] = []
                    play_status[_g_title]["condition"][my_level] = cur_cdt

                    print('\n'+15*"-----")
                    send_first_message(_g_title, cur_cdt, my_level)
                    print('\n'+15*"-----")
                    continue

                if play_status[_g_title]["flag"][my_level]:
                    pre_cdt = play_status[_g_title]["condition"][my_level]
                    play_status[_g_title]["series"][my_level].append(new_num)
                    play_status[_g_title]["stage"][my_level] += 1

                    if new_num in condition_list[pre_cdt]:
                        continue

                    if new_num > 0:
                        print('\n'+15*"-----")
                        send_second_message(
                            _g_title, play_status[_g_title]["condition"][my_level], my_level)

                        play_status[_g_title]["flag"][my_level] = False
                        play_status[_g_title]["stage"][my_level] = 0
                        play_status[_g_title]["series"][my_level] = []
                        play_status[_g_title]["condition"][my_level] = None
                    elif new_num < 1:
                        print('\n'+15*"-----")
                        send_middle_message(
                            _g_title, play_status[_g_title]["condition"][my_level], my_level)

                        play_status[_g_title]["flag"][my_level] = False
                        play_status[_g_title]["stage"][my_level] = 0
                        play_status[_g_title]["series"][my_level] = []
                        play_status[_g_title]["condition"][my_level] = None

        bar.index = 0

    bar.finish()


if __name__ == "__main__":
    startProcess()
