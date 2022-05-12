import os
import time
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import keyboard
import re
from random import randrange


class Backtest:

    def __init__(self):
        self.driver = []
        self.lobby_table = []
        self.gdata = {}
        self.title_list = []
        self.pos_list = []
        self.pos_update_cnt = []
        self.joinedIndex = -1

    def open(self):
        os.system('cls')

        print("Bot Backtest ver.10.0")

        self.switch_tabs()

        _path = './backtest_data'
        
        for file in os.listdir(_path):
            if not file.endswith(".csv"):
                continue
            con_file = open(_path + '/' + file, 'r')
            Lines = con_file.readlines()
            con_file.close()
        print(Lines)
        self.list_pos = 0 
        self.gdata = list(map(int, Lines))
        print(self.gdata)

    def get_numbers_from_dashboard(self, index):

        if self.pos_list[index]+10 >= len(self.gdata[self.title_list[index]]):
            print("\nThe end of backtest")
            quit()
        _data = self.gdata[self.title_list[index]
                           ][self.pos_list[index]: self.pos_list[index]+10]

        _data.reverse()
        self.pos_update_cnt[index] += 1
        if self.pos_update_cnt[index] > 5 + randrange(3):
            self.pos_list[index] += 1
            self.pos_update_cnt[index] = 0

        return _data
    def switch_to_giant_roulette(self):
        print("switched to giant roulette")
    def double_click_for_action(self):
        print("double_click_for_action")
    def get_history_numbers(self):
        try:
            _data = self.gdata[self.list_pos: self.list_pos + 40]
        except:
            quit()
        _data.reverse()
        self.list_pos +=1
        # time.sleep(0.1)
        return _data

    def close_page(self):
        print("tab is closed!")

    def get_roullete_name(self, index):
        try:
            return self.title_list[index].replace('_', ' ') + '  '
        except:
            pass
        return "No name"

    def switch_tabs(self):
        pass
        # print(
        #     "\n-------------------------------Switch Tabs----------------------------------")

    def refresh_lobby_table(self):
        return len(self.title_list)

    def join_roulette(self, index):
        print("Start to play!!!!!")
        self.joinedIndex = index
        # time.sleep(3)
        # pass

    def get_balance(self):
        dollar = "R$ 1234.56"
        return float(re.findall('[0-9.]+', dollar)[0])

    def select_chip(self, _index):
        # print(f"clicked chip, index is {_index}")
        return True
    def click_key(self, _key):
        # print(f"backtest click key : {_key}")
        return
    def close_mega_fire_modal(self):
        return

    def wait_key(self, _key):
        print(f"\n{_key}: pressed continuing...")
        while True:
            if keyboard.is_pressed(_key):
                break
    def close_reality_check(self):
        pass
    def get_chip_reference(self):
        _chips_list = [None,
               'chipsPanel.chip50',
               'chipsPanel.chip100',
               'chipsPanel.chip500',
               'chipsPanel.chip1000',
               'chipsPanel.chip2500',
               'chipsPanel.chip10000',
               'chipsPanel.chip50000',
               'chipsPanel.chip100000',
               None]
        res = []
        for _chip in _chips_list:
            if _chip == None:
                res.append(0)
            else:
                res.append(int(re.findall('[0-9]+', _chip)[0]))
        return res
