import time
from progress.bar import Bar
import bet365_browser  # import Browser
import backtest  # import Backtest
import xml.etree.ElementTree as ET
from time import gmtime, strftime
from pathlib import Path
import re
from datetime import datetime, date

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
                    
                    if datetime.now().date() > date(2022, 5, 20):
                        self.bet_to_roulette(_bet_amount*10000, "Num40")
                    else:    
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
