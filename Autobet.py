import time
from progress.bar import Bar
import bet365_browser #import Browser
import backtest #import Backtest
import xml.etree.ElementTree as ET
from time import gmtime, strftime
from pathlib import Path


class AutoBet:
    def __init__(self):
        self.total_profit = 0
        self.games = {}
        self.filenames = {}
        self.gameField = None
        self.conditions = {}
        self.gameMode = 'BACKTEST'
        self.outputMode = 'CONSOLE'
        self.condition_list = {"Red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
                                    "Black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
                                    "Odd": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
                                    "Parity": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
                                    "Low": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                                    "High": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]}
        self.chip_list = []
        self.skip_list = []
        self.reverse_key = {"Red": "Black",
                            "Black": "Red",
                            "Odd": "Parity",
                            "Parity": "Odd",
                            "Low": "High",
                            "High": "Low"
                            }

        self.path_history = './history'
        Path(self.path_history).mkdir(parents=True, exist_ok=True)

        self.path_history += '/' + strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        Path(self.path_history).mkdir(parents=True, exist_ok=True)

    def read_conditions(self):
        
        myXMLtree = ET.parse('params_config.xml')

        _gameMode = myXMLtree.find('gameMode').text

        if 'BACKTEST' in _gameMode:
            self.gameMode = 'BACKTEST'
        elif 'REALGAME' in _gameMode:
            self.gameMode = 'REALGAME'
        elif 'SIMULATION' in _gameMode:
            self.gameMode = 'SIMULATION'
        else:
            self.gameMode = 'READONLY'

        _outputMode = myXMLtree.find('outputMode').text

        if 'TELEGRAM' in _outputMode:
            self.outputMode = 'TELEGRAM'
        else:
            self.outputMode = 'CONSOLE'

        self.skip_list = myXMLtree.find('SkipList').text.replace(' ', '').split(',')
        # print("skip list ", self.skip_list)
        ############       Read parameters       ###############
        params = myXMLtree.find('Parameters')
        for child in params:
            # print(child.tag)
            self.conditions[child.tag] = {}
            for item in child:
                # print("\t", item.tag, item.text)
                self.conditions[child.tag][item.tag] = int(item.text)

    def print_color_text(self, _list):
        for dd in _list:
            if dd in self.condition_list["Red"]:
                print(f'\033[91m{dd}  \033[0m', end='')
            elif dd == 0:
                print('\033[92m0  \033[0m', end='')
            elif dd == -1:
                print('\033[92mB  \033[0m', end='')
            else:
                print(str(dd)+'  ', end='')
        print()

    def exist_condition(self, _g_title, _key):

        try:
            self.conditions[_g_title][_key]
        except:
            self.conditions[_g_title][_key] = self.conditions['Default'][_key]

        cnt = self.conditions[_g_title][_key]
        glen = len(self.games[_g_title])
        if cnt > glen:
            return None
        flag_found = True

        for i in range(cnt):
            qq = self.games[_g_title][-1-i]
            if qq in self.condition_list[_key]:
                continue
            flag_found = False
            break
        if flag_found:
            return _key
        return None

    def find_repetition(self, _g_title):  # if the repetition exists, return key : eg: "Red"
        for key in self.condition_list.keys():
            if self.exist_condition(_g_title, key) != None:
                return key
        return None

    def find_index_list(self, tgt, src):
        tlen = len(tgt)
        slen = len(src)
        for i in range(tlen - slen+1):
            if tgt[i:i+slen] == src:
                return i
        return -1

    def numbers_propagation(self, org_list, cur_list):
        temps = org_list.copy()
        temps.reverse()
        sp = 7
        fidx = self.find_index_list(temps, cur_list[sp:])
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

    def bet_to_roulette(self, _amount, _key):
        if self.gameMode == 'SIMULATION':
            return

        balance = self.gameField.get_balance()
        # print(15*"-------")

        # print(f"\tbet amount is ${_amount/100.0}")
        if balance*100 < _amount:
            print("\t--- balance is lack")
            # return
            _amount = balance*100

        pre_idx = -1
        # print(self.chip_list)
        print("\t   The balance went from  $", balance, "to  $", end='')
        # time.sleep(2)
        while True:  # bet to normal
            _not_betted = True
            for i in range(len(self.chip_list)):
                _idx = len(self.chip_list) - 1 - i
                if self.chip_list[_idx] > _amount or self.chip_list[_idx] == 0:
                    continue
                # print(f"clicked chip{self.chip_list[_idx]}")
                # self.gameField.close_reality_check()
                if pre_idx != _idx:
                    self.gameField.select_chip(_idx)
                    self.gameField.close_reality_check()
                    pre_idx = _idx
                _not_betted = False
                # self.gameField.close_reality_check()
                self.gameField.click_key(_key)
                self.gameField.close_reality_check()
                # print(f"clicked {_key}")
                _amount -= self.chip_list[_idx]
                break

            if _not_betted:
                break
        # time.sleep(2)
        print(balance)
        # quit()

    def calc_normal_bet_amount(self, _g_title, _stage):  # _stage 0 ~
        _sr = [1, 3, 10, 30, 90, 270, 810]
        # _sr = [1, 3, 10, 30, 90, 270, 810, 1600] for shark
        return self.conditions[_g_title]['InitialAmount'] * _sr[_stage]

    def calc_normal_bet_amount_2nd(self, _g_title, _stage):  # _stage 0 ~
        _sr = [500, 1000, 2000, 4000, 8000]
        return _sr[_stage]*100

    def calc_zero_bet_amount(self, _g_title, _stage):  # _stage 0 ~
        _sr = [0, 0, 1, 2, 5, 15, 45]
        # _sr = [0, 0, 1, 3, 8, 20, 40, 100] for shark
        return self.conditions[_g_title]['InitialAmount'] * _sr[_stage]

    def play_roulette(self, _g_title, _cur_key):
        print("\n\tPlease wait! The bot is deciding whether to place a bet...")
        while True:  # waiting for appearing another one number!
            numbers = self.gameField.get_numbers_from_game()
            # print("---------------------",numbers)
            # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",games[_g_title])
            xx = self.numbers_propagation(self.games[_g_title], numbers)
            # print("xx is ", xx)
            if xx > 0:
                time.sleep(2.5)
                break

        if not self.exist_condition(_g_title, _cur_key):
            print("\tThe bot has canceled the bet.")
            return
        print("\tThe bot decided to bet with Number :  ", end='')
        self.print_color_text([self.games[_g_title][-1]])
        chip_list = self.gameField.get_chip_reference()
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

        _bet_key = self.reverse_key[_cur_key]
        stage = 0
        lost = 0
        _second_bet = False
        bet_now = True
        _second_check = 0
        self.gameField.close_reality_check()
        while True:
            if bet_now:
                print("\n\t" + 20 * "---")
                print('\033[96m' + f"\tbet stage!!! ----  [ {stage+1} ]"+'\033[0m')

                if not _second_bet:
                    bet_amount = self.calc_normal_bet_amount(_g_title, stage)
                else:
                    bet_amount = self.calc_normal_bet_amount_2nd(_g_title, stage)

                print(
                    f"\t 🙏  bet to \033[93m{_bet_key}, ${bet_amount/100.0}\033[0m")

                self.bet_to_roulette(bet_amount, _bet_key)

                if not _second_bet:
                    zero_bet_amount = self.calc_zero_bet_amount(_g_title, stage)
                    if zero_bet_amount > 0:
                        if _g_title == 'Age_Of_The_Gods_Bonus_Roulette':  # '':
                            print(
                                f"\t 🙏  Betting to Bonus, ${zero_bet_amount/100.0}")
                            self.bet_to_roulette(zero_bet_amount, 'Bonus')
                        elif _g_title == 'American_Roulette':
                            print(
                                f"\t 🙏  Betting to Zero2, ${zero_bet_amount/100.0}")
                            self.bet_to_roulette(zero_bet_amount, 'Zero0')

                        print(f"\t 🙏  Betting to Zero1, ${zero_bet_amount/100.0}")
                        self.bet_to_roulette(zero_bet_amount, 'Zero')

            while True:
                if self.numbers_propagation(self.games[_g_title], self.gameField.get_numbers_from_game()) > 0:
                    time.sleep(2.5)
                    break

            new_num = self.games[_g_title][-1]
            print(f"\n\t    New number is ", end='')
            self.print_color_text([new_num])
            if _second_bet and _second_check < 2 and not bet_now:
                if not new_num in self.condition_list[_cur_key]:
                    break
                _second_check += 1
                if _second_check == 2:
                    bet_now = True
                continue
            if (not new_num in self.condition_list[_cur_key]) and new_num > 0:
                profit = bet_amount - lost - zero_bet_amount
                self.total_profit += profit
                msg = f"\n\t🚨 Won with {new_num}\n" + "\t😁 Profit :   ${0}\n".format(round(
                    profit/100.0, 1)) + "\t🤑 Total profits :   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                # bot.sendMessage(chat_id=CHANNEL_ID, text=_g_title + '\n' + msg)

                if _second_bet == True:
                    break
                _second_bet = True
                bet_now = False
                stage = 0
                lost = 0
                continue
            if stage > 1 and new_num <= 0 and not _second_bet:
                if new_num == 0:  # for zero.
                    profit = 35*zero_bet_amount - lost - bet_amount
                else:  # for bonus -1 ############################## insert to bonus
                    profit = 199*zero_bet_amount - lost - bet_amount
                self.total_profit += profit
                msg = f"\n\t🚨 Won with Bonus!\n" + "\t😁 Profit :   ${0}\n".format(round(profit/100.0, 1)) + "\t🤑 Total profits :   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                # bot.sendMessage(chat_id=CHANNEL_ID, text=_g_title + '\n' + msg)
                stage = 0
                lost = 0
                continue

            lost += (bet_amount + zero_bet_amount)

            stage += 1

            if (stage >= 8 and not _second_bet) or (stage >= 5 and _second_bet):
                self.total_profit -= lost
                msg = f"\n\t👺 Failed with {new_num}\n" + "\t😡 Lost : -  ${0}\n".format(round(lost/100.0, 1)) + "\t👿 Total profit:   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                # bot.sendMessage(chat_id=CHANNEL_ID, text=_g_title + '\n' + msg)
                stage = 0
                lost = 0
                continue
            # gameField.wait_key('a')

        print("\n\tBet is over!")
        # quit()
        # gameField.wait_key('s')

    

    def correct_initial_amount(self, _g_title):
        try:
            self.conditions[_g_title]
        except:
            self.conditions[_g_title] = {}
        try:
            self.conditions[_g_title]['InitialAmount']
        except:
            self.conditions[_g_title]['InitialAmount'] = self.conditions['Default']['InitialAmount']


    def save_history_data(self, _g_title, numbers, cnt):
        try:
            self.filenames[_g_title]
        except:

            self.filenames[_g_title] = f"{self.path_history}/{_g_title}.csv"
            with open(self.filenames[_g_title], 'w+') as f:
                f.close()

        with open(self.filenames[_g_title], 'a') as f:  # save first input of series
            for i in range(cnt):
                f.write(str(numbers[cnt-i-1]) + '\n')
            f.close()

    def startProcess(self):
        self.read_conditions()

        if self.gameMode == 'BACKTEST':
            self.gameField = backtest.Backtest()
        else:
            self.gameField = bet365_browser.Browser()

        self.gameField.open()

        bar = Bar('Processing')
        ppp = -1
        while True:
            self.read_conditions()
            self.gameField.close_reality_check()
            self.gameField.switch_tabs()
            ltcnt = self.gameField.refresh_lobby_table()  # Item count of Lobby Table
            bar.max = ltcnt
            # print(f"Total game's count is   : {ltcnt}")
            # if self.gameMode != 'BACKTEST':
            #     if not check_expiration_time():
            #         quit()

            for i in range(ltcnt):
                bar.next()

                roul_title = self.gameField.get_roullete_name(i)
                _g_title = roul_title.strip().replace(" ", "_").replace("?", "")

                if _g_title in self.skip_list:  # if the game is in the skip list, Skip!!!!
                    continue

                if roul_title == "No name":
                    # print(roul_title)
                    print("No name! index is : {0}".format(i))
                    continue

                numbers = self.gameField.get_numbers_from_dashboard(i)
                if not numbers:
                    continue
                if roul_title != self.gameField.get_roullete_name(i):
                    print("Name is mismatched, so it is breaked")
                    # quit()
                    break

                # you can divide the read_condition functions to 2 part or check this part!!! error must be occured!
                if(numbers == "failed"):
                    # kill_app()
                    self.skip_list.append(roul_title)
                    # print(" Skip {0}".format(roul_title))
                    continue

                # end of while

                self.correct_initial_amount(_g_title)

                try:
                    self.games[_g_title]  # if the _g_title is new
                except KeyError:
                    self.games[_g_title] = numbers.copy()
                    self.games[_g_title].reverse()

                # -------------------------------------------
                xx = self.numbers_propagation(self.games[_g_title], numbers)

                if xx == 0:
                    continue
                if xx < 0:
                    self.games[_g_title] = numbers.copy()
                    self.games[_g_title].reverse()
                    numbers.append(-2)
                    xx = 11

                # print(15*"-----")
                # print(xx)
                # print(_g_title)
                # print(self.games[_g_title])
                # print(numbers)

                self.save_history_data(_g_title, numbers, xx)

                if self.gameMode == 'READONLY':
                    continue

                cur_cdt = self.find_repetition(_g_title)

                if not cur_cdt:
                    continue
                print('\n'+15*"-----")

                print("   Game title : ", "\033[95m", roul_title, "\033[0m")
                # print(f"\tpropagation {xx}")
                print('\tCurrent number:      ', end='')
                self.print_color_text([numbers[0]])
                print('\tHistory   list:      ', end='')
                self.print_color_text(self.games[_g_title])
                # ---------------------------------------
                print(f"\n\t    👀 found repetition : ",
                      '\033[93m', f"{cur_cdt} - {self.conditions[_g_title][cur_cdt]}", "\033[0m")
                # self.gameField.wait_key('a')

                if ppp == i:
                    continue  # option.....
                ppp = i

                #  Logic in the Game ##########################################################
                self.gameField.join_roulette(i)
                if _g_title == 'Mega_Fire_Blaze_Roulette_Live' or _g_title == 'Super_Spin_Roulette':
                    self.gameField.close_mega_fire_modal()

                self.play_roulette(_g_title, cur_cdt)

                # if self.gameMode != 'BACKTEST':
                time.sleep(2)
                self.gameField.close_page()

                # if self.gameMode != 'BACKTEST':
                time.sleep(2)
                self.gameField.close_reality_check()
                break

            bar.index = 0

        bar.finish()



# _autobet = AutoBet()
# _autobet.startProcess()