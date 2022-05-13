import time
from progress.bar import Bar
import bet365_browser  # import Browser
import backtest  # import Backtest
import xml.etree.ElementTree as ET
from time import gmtime, strftime
from pathlib import Path
import re


import telegram


class AutoBet:
    def __init__(self):
        self.total_profit = 0
        self.gnlist = []
        self.filenames = {}
        self.gameField = None
        self.conditions = {}
        self.gameMode = 'BACKTEST'
        self.outputMode = 'CONSOLE'
        self.condition_list = {"None2": [1, 5, 10, 20, 40, -2, -7],
                               "None1": [2, 5, 10, 20, 40, -2, -7],
                               "Odd": [1, 5, -2, -7],
                               "Even": [2, 10, 20, 40, -2, -7],

                               }
        self.chip_list = []
        self.skip_list = []
        self.reverse_key = {"None2": "Num2",
                            "None1": "Num1",
                            "Odd": "Even",
                            "Even": "Odd"
                            }
        self.ratio = {"Even": 1.25, "Odd": 0.75, "Num2": 2, "Num1": 1}

        self.bet_flag = {"Odd": 0, "Even": 0, "None2": 0, "None1": 0}
        self.bet_stage = {"Odd": 0, "Even": 0, "None2": 0, "None1": 0}
        self.bet_lost = {"Odd": 0, "Even": 0, "None2": 0, "None1": 0}

        self.cdt_delta = {"D2": -2, "D1": -1,
                          "MID": 0, "P1": 1, "P2": 2, "P3": 3}

        self.chip_pre_idx = -1

        self.read_conditions()
        if self.gameMode != 'BACKTEST':
            self.path_history = './giant_history'
            Path(self.path_history).mkdir(parents=True, exist_ok=True)

            self.filename = self.path_history + '/' + \
                strftime("%Y_%m_%d_%H_%M_%S", gmtime()) + '.csv'

            with open(self.filename, 'w+') as f:
                f.close()

        self.CHANNEL_ID = '-1001531528873'
        self.telegram_bot = telegram.Bot(
            token='5363359521:AAG4p79YyooiqFgQnlxgcu73tFqUse8eH1k')

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

        self.dangerLevel = myXMLtree.find('dangerLevel').text.replace(' ', '')

        self.conditions["Odd"] = int(
            myXMLtree.find('Odd').text.replace(' ', ''))
        self.conditions["Even"] = int(
            myXMLtree.find('Even').text.replace(' ', ''))
        self.conditions["None2"] = int(
            myXMLtree.find('None2').text.replace(' ', ''))
        self.conditions["None1"] = int(
            myXMLtree.find('None1').text.replace(' ', ''))

        self.series1 = [int(s) for s in re.findall(
            r'\b\d+\b', myXMLtree.find('series1').text)]
        self.series2 = [int(s) for s in re.findall(
            r'\b\d+\b', myXMLtree.find('series2').text)]

        self.initial_amount = int(myXMLtree.find(
            'initialAmount').text.replace(' ', ''))

        _outputMode = myXMLtree.find('outputMode').text

        if 'TELEGRAM' in _outputMode:
            self.outputMode = 'TELEGRAM'
        else:
            self.outputMode = 'CONSOLE'

        # print(self.bet_normal_amount_1st)
        # print(self.bet_zero_amount_1st)
        # print(self.bet_normal_amount_2nd)
        # print(self.bet_zero_amount_2nd)

        # print(self.skip_cnt_2nd_stage)
        # quit()

    def change_color_text(self, _list):
        _text = ""
        for dd in _list:
            if dd in self.condition_list["Red"]:
                _text += f'\033[91m {dd}  \033[0m'
            elif dd == 0:
                _text += '\033[92m0  \033[0m'
            elif dd == -1:
                _text += '\033[92mB  \033[0m'
            else:
                _text += str(dd)+'  '

        return _text

    def exist_condition(self, _key):

        cnt = self.conditions[_key] + self.cdt_delta[self.dangerLevel]
        glen = len(self.gnlist)
        if cnt > glen:
            return None

        flag_found = True

        for i in range(cnt):
            qq = self.gnlist[-1-i]
            if qq in self.condition_list[_key]:
                continue
            flag_found = False
            break
        if flag_found:
            return _key
        return None

    # if the repetition exists, return key : eg: "Red"
    def find_repetition(self):
        _rep = []
        for key in self.condition_list.keys():
            if self.exist_condition(key) != None:
                _rep.append(key)

        return _rep

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
        sp = 3
        try:
            fidx = self.find_index_list(temps, cur_list[sp:])
        except:
            print("for debugging numbders propagarion", temps, cur_list)
            pass
        if fidx > sp or fidx < 0:
            org_list = cur_list.copy()
            org_list.reverse()
            return -1

        fidx = sp - fidx

        for jj in range(fidx):
            try:
                org_list.append(cur_list[fidx-jj-1])
            except:
                print("End of backtest")
                quit()

        while len(org_list) > 100:
            org_list.pop(0)

        return fidx

    def bet_to_roulette(self, _amount, _key):

        print("bet to [", _key, "],  amount is :",
              '  $' + str(round(_amount/100, 1)))

        if self.gameMode == 'SIMULATION':
            return
        balance = self.gameField.get_balance()
        # print(15*"-------")

        # print(f"\tbet amount is ${_amount/100.0}")
        if balance*100 < _amount:
            print("\t--- balance is lack")
            # return
            _amount = balance*100

        # print(self.chip_list)

        print("\t   The balance is \033[93m$" + str(balance) + '\033[0m')
        # print(, end='')
        # time.sleep(2)
        while True:  # bet to normal
            _not_betted = True
            self.gameField.close_reality_check()
            for i in range(len(self.chip_list)):
                _idx = len(self.chip_list) - 1 - i
                if self.chip_list[_idx] > _amount or self.chip_list[_idx] == 0 or self.chip_list[_idx] == 25:
                    continue

                # self.gameField.close_reality_check()
                if self.chip_pre_idx < 0:
                    self.chip_pre_idx = _idx
                    self.gameField.select_chip(self.chip_pre_idx)
                elif self.chip_pre_idx != _idx:

                    while True:
                        if _idx > self.chip_pre_idx+2:
                            self.chip_pre_idx += 2
                            self.gameField.select_chip(self.chip_pre_idx)
                        elif _idx < self.chip_pre_idx-2:
                            self.chip_pre_idx -= 2
                            self.gameField.select_chip(self.chip_pre_idx)
                        else:
                            break
                    if self.chip_pre_idx != _idx:
                        self.chip_pre_idx = _idx
                        self.gameField.select_chip(self.chip_pre_idx)

                    print(
                        f"clicked chip{self.chip_list[_idx]}, index is {_idx}")
                    self.gameField.close_reality_check()

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

        # quit()

    def calc_normal_bet_amount_1st(self, _g_title, _stage):  # _stage 0 ~
        return self.conditions[_g_title]['InitialAmount'] * self.bet_normal_amount_1st[_stage]

    def calc_normal_bet_amount_2nd(self, _g_title, _stage):  # _stage 0 ~
        return self.conditions[_g_title]['InitialAmount'] * self.bet_normal_amount_2nd[_stage]

    def calc_zero_bet_amount_1st(self, _g_title, _stage):  # _stage 0 ~
        return self.conditions[_g_title]['InitialZeroAmount'] * self.bet_zero_amount_1st[_stage]

    def calc_zero_bet_amount_2nd(self, _g_title, _stage):  # _stage 0 ~
        return self.conditions[_g_title]['InitialZeroAmount'] * self.bet_zero_amount_2nd[_stage]

    def play_roulette(self, _g_title, _cur_key):
        print("\n\tPlease wait! The bot is deciding whether to place a bet...")
        while True:  # waiting for appearing another one number!
            numbers = self.gameField.get_numbers_from_game()
            if not numbers:
                print("Error for getting numners from game")
                time.sleep(1)
                continue
            # print("---------------------",numbers)
            # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",gnlist[_g_title])
            xx = self.numbers_propagation(self.gnlist[_g_title], numbers, 2)
            # print("xx is ", xx)
            if xx > 0:
                time.sleep(2.5)

                self.save_history_data(_g_title, numbers, xx)
                break

        if not self.exist_condition(_g_title, _cur_key):
            print("\tThe bot has canceled the bet.")
            return

        print("\tThe bot decided to bet with Number :  " +
              self.change_color_text([self.gnlist[_g_title][-1]]))

        self.chip_list = self.gameField.get_chip_reference()
        if not self.chip_list:
            print('Faied to update chip_list!')
            return

        _txt = '\tChip list updated :'
        for x in self.chip_list:
            if x == 0:
                continue
            if x < 100:
                _txt += '  $' + str(round(x/100.0, 1))
            else:
                _txt += '  $' + str(int(x/100))
        print(_txt)

        _bet_key = self.reverse_key[_cur_key]
        stage = 0
        lost = 0

        if _cur_key in ["Dozen12", "Dozen13", "Dozen23",  "Column12", "Column13",  "Column23"]:
            _second_bet = True
        else:
            _second_bet = False

        self.gameField.close_reality_check()
        while True:
            print("\n\t" + 20 * "---")
            print('\033[96m' +
                  f"\tbet stage!!! ----  [ {stage+1} ]"+'\033[0m')

            if not _second_bet:
                bet_amount = self.calc_normal_bet_amount_1st(_g_title, stage)
                zero_bet_amount = self.calc_zero_bet_amount_1st(
                    _g_title, stage)
            else:
                bet_amount = self.calc_normal_bet_amount_2nd(_g_title, stage)
                zero_bet_amount = self.calc_zero_bet_amount_2nd(
                    _g_title, stage)

            print(
                f"\t 🙏  bet to \033[93m{_bet_key}, ${bet_amount/100.0}\033[0m")

            self.bet_to_roulette(bet_amount, _bet_key)

            if zero_bet_amount > 0:
                if _g_title == 'Age_Of_The_Gods_Bonus_Roulette':  # '':
                    print(
                        f"\t 🙏  Betting to \033[93m$Bonus, {zero_bet_amount/100.0}\033[0m")
                    lost += zero_bet_amount
                    self.bet_to_roulette(zero_bet_amount, 'Bonus')
                elif _g_title == 'American_Roulette':
                    print(
                        f"\t 🙏  Betting to \033[93mZero2, ${zero_bet_amount/100.0}\033[0m")
                    lost += zero_bet_amount
                    self.bet_to_roulette(zero_bet_amount, 'Zero0')

                print(
                    f"\t 🙏  Betting to \033[93mZero1, ${zero_bet_amount/100.0}\033[0m")
                self.bet_to_roulette(zero_bet_amount, 'Zero')

            while True:
                numbers = self.gameField.get_numbers_from_game()
                self.gameField.close_reality_check()
                xx = self.numbers_propagation(
                    self.gnlist[_g_title], numbers, 2)
                if xx > 0:
                    time.sleep(2.5)

                    self.save_history_data(_g_title, numbers, xx)
                    break

            new_num = self.gnlist[_g_title][-1]
            print(f"\n\t    New number is " +
                  self.change_color_text([new_num]))

            if (not new_num in self.condition_list[_cur_key]) and new_num > 0:
                if _second_bet:
                    profit = 2 * bet_amount - lost - zero_bet_amount
                else:
                    profit = bet_amount - lost - zero_bet_amount
                self.total_profit += profit
                msg = f"\n\t🚨 Won with {new_num}\n" + "\t😁 Profit :   ${0}\n".format(round(
                    profit/100.0, 1)) + "\t🤑 Total profits :   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                msg += f"\nParam: {_cur_key} - {self.conditions[_g_title][_cur_key]} stage: {stage+1}"
                try:
                    if self.gameMode != 'BACKTEST':
                        self.telegram_bot.sendMessage(
                            chat_id=self.CHANNEL_ID, text=_g_title + '\n' + msg)
                except:
                    print("telegram error!")
                break

            if (zero_bet_amount > 0 and new_num <= 0) and not (_g_title == 'Age_Of_The_Gods_Bonus_Roulette' and new_num == -1):

                profit = 35*zero_bet_amount - lost - bet_amount
                self.total_profit += profit
                msg = f"\n\t🚨 Won with Zero!\n" + "\t😁 Profit :   ${0}\n".format(round(
                    profit/100.0, 1)) + "\t🤑 Total profits :   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                msg += f"\nParam: {_cur_key} - {self.conditions[_g_title][_cur_key]} stage: {stage+1}"
                try:
                    if self.gameMode != 'BACKTEST':
                        self.telegram_bot.sendMessage(
                            chat_id=self.CHANNEL_ID, text=_g_title + '\n' + msg)
                except:
                    print("telegram error!")
                stage = 0
                lost = 0
                break

            lost += (bet_amount + zero_bet_amount)

            if zero_bet_amount == 0 and new_num <= 0:
                self.total_profit -= lost
                msg = f"\n\t😩 The bot gives up with Zero\n" + "\t🔥 Lost : -  ${0}\n".format(round(
                    lost/100.0, 1)) + "\t☘️ Total profit:   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                msg += f"\nParam: {_cur_key} - {self.conditions[_g_title][_cur_key]} stage: {stage+1}"
                try:
                    self.telegram_bot.sendMessage(
                        chat_id=self.CHANNEL_ID, text=_g_title + '\n' + msg)
                except:
                    print("telegram error!")
                break
            stage += 1
            # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            # print(_second_bet, self.max_round_2nd, stage)
            if (stage >= self.max_round_1st and not _second_bet) or (stage >= self.max_round_2nd and _second_bet):
                self.total_profit -= lost
                msg = f"\n\t👺 Failed with {new_num}\n" + "\t😡 Lost : -  ${0}\n".format(round(
                    lost/100.0, 1)) + "\t👿 Total profit:   ${0}".format(round(self.total_profit/100.0, 1))
                print(msg)
                msg += f"\nParam: {_cur_key} - {self.conditions[_g_title][_cur_key]} stage: {stage+1}"
                try:
                    self.telegram_bot.sendMessage(
                        chat_id=self.CHANNEL_ID, text=_g_title + '\n' + msg)
                except:
                    print("telegram error!")
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
            self.conditions[_g_title]['InitialZeroAmount']
        except:
            self.conditions[_g_title]['InitialAmount'] = self.conditions['Default']['InitialAmount']
            self.conditions[_g_title]['InitialZeroAmount'] = self.conditions['Default']['InitialZeroAmount']

    def save_history_data(self, numbers, cnt):
        if self.gameMode == 'BACKTEST':
            return

        with open(self.filename, 'a') as f:  # save first input of series
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

        self.gameField.switch_to_giant_roulette()
        print("end")

        self.total_profit = 0
        _temp_multiplier = 1

        self.chip_list = self.gameField.get_chip_reference()
        if not self.chip_list:
            print('Faied to update chip_list!')
            return

        _txt = '\tChip list updated :'
        for x in self.chip_list:
            if x == 0:
                continue
            if x < 100:
                _txt += '  $' + str(round(x/100.0, 2))
            else:
                _txt += '  $' + str(int(x/100))
        print(_txt)

        while True:
            self.read_conditions()
            self.gameField.close_reality_check()

            numbers = self.gameField.get_history_numbers()
            # -------------------------------------------
            if not len(self.gnlist):
                self.gnlist = numbers.copy()
                self.gnlist.reverse()
                self.save_history_data(numbers, 40)

            xx = self.numbers_propagation(self.gnlist, numbers)
            if xx == 0:
                continue
            self.gameField.double_click_for_action()
            print(15*"-----")
            new_num = self.gnlist[-1]
            print("new number is  : ", new_num)

            self.save_history_data(numbers, xx)

            if self.gameMode == 'READONLY':
                continue

            if new_num == -2 or new_num == -7:
                _temp_multiplier *= abs(new_num)
                continue

            cur_cdt = self.find_repetition()
            print(cur_cdt)
            for _cdt in self.condition_list.keys():
                _bet_key = self.reverse_key[_cdt]
                if _bet_key == 'Odd' or _bet_key == 'Num1':
                    _series = self.series1
                else:
                    _series = self.series2

                # self.condition_list = {"Odd": [1, 5, -2, -7],
                #                "Even": [2, 10, 20, 40, -2, -7],
                #                "None2": [1, 5, 10, 20, 40, -2, -7],
                #                "None1": [2, 5, 10, 20, 40, -2, -7],
                #                }
                if self.bet_flag[_cdt] and not new_num in self.condition_list[_cdt]:
                    print("bet is completed : ", _bet_key)

                    _profit = _series[self.bet_stage[_bet_key]] * self.ratio[_bet_key] * \
                        _temp_multiplier*self.initial_amount - \
                        self.bet_lost[_bet_key]

                    print("Profit is : ------     $" +
                          str(round(_profit/100, 3)))
                    self.total_profit += _profit
                    self.bet_stage[_bet_key] = 0
                    self.bet_flag[_cdt] = False
                    if _bet_key == "Even" and self.bet_flag['None2'] and new_num != 2:
                        self.bet_flag['Odd'] = True
                        self.bet_lost["Even"] = 0
                        self.bet_stage["Even"] = self.bet_stage['Num2']
                        _bet_amount = _series[self.bet_stage[_bet_key]
                                              ] * self.initial_amount
                        self.bet_to_roulette(_bet_amount, _bet_key)

                    if _bet_key == "Odd" and self.bet_flag['None1'] and new_num != 2:
                        self.bet_flag['Even'] = True
                        self.bet_lost["Odd"] = 0
                        self.bet_stage["Odd"] = self.bet_stage['Num1']
                        _bet_amount = _series[self.bet_stage[_bet_key]
                                              ] * self.initial_amount
                        self.bet_to_roulette(_bet_amount, _bet_key)

                    print(">>  Total Profit is :   $" +
                          str(round(self.total_profit/100, 3)))
                elif self.bet_flag[_cdt] and new_num in self.condition_list[_cdt]:
                    self.bet_lost[_bet_key] += _series[self.bet_stage[_bet_key]
                                                       ] * self.initial_amount
                    print("lost is : in ", _bet_key, ",  amount is :  $" +
                          str(round(self.bet_lost[_bet_key]/100, 1)))

                    print("bet again")
                    self.bet_stage[_bet_key] += 1
                    _bet_amount = _series[self.bet_stage[_bet_key]
                                          ] * self.initial_amount
                    self.bet_to_roulette(_bet_amount, _bet_key)

            for _cdt in cur_cdt:
                if not self.bet_flag[_cdt]:
                    self.bet_flag[_cdt] = True
                    _bet_key = self.reverse_key[_cdt]
                    self.bet_stage[_bet_key] = 0
                    self.bet_lost[_bet_key] = 0
                    print(f"\n\t    👀 found repetition : " +
                          '\033[93m' + f"{_cdt} - {self.conditions[_cdt]}  , Delta : {self.cdt_delta[self.dangerLevel]} " + "\033[0m")

                    if _bet_key == 'Odd' or _bet_key == 'Num1':
                        _series = self.series1
                    else:
                        _series = self.series2

                    _bet_amount = _series[self.bet_stage[_bet_key]
                                          ] * self.initial_amount
                    self.bet_to_roulette(_bet_amount, _bet_key)

                    if _bet_key == 'Num2' and not self.bet_flag['Odd']:
                        self.bet_flag['Odd'] = True
                        _bet_key = self.reverse_key['Odd']
                        self.bet_stage[_bet_key] = 0
                        self.bet_lost[_bet_key] = 0
                        _bet_amount = _series[self.bet_stage[_bet_key]
                                              ] * self.initial_amount
                        self.bet_to_roulette(_bet_amount, _bet_key)

                    if _bet_key == 'Num1' and not self.bet_flag['Even']:
                        self.bet_flag['Even'] = True
                        _bet_key = self.reverse_key['Even']
                        self.bet_stage[_bet_key] = 0
                        self.bet_lost[_bet_key] = 0
                        _bet_amount = _series[self.bet_stage[_bet_key]
                                              ] * self.initial_amount
                        self.bet_to_roulette(_bet_amount, _bet_key)

            # if _temp_multiplier!=1:
            #     time.sleep(20)
            _temp_multiplier = 1
