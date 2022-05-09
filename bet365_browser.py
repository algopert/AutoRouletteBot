import os
import time
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import keyboard
import re


class Browser:

    def __init__(self):
        self.driver = []
        self.lobby_table = []

    def open(self):
        dirr = os.path.abspath(os.curdir).rsplit("\\", 1)[0] + "\\userdata"
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-gpu")
        options.add_argument("excludeSwitches")
        options.add_argument(r"user-data-dir={}".format(dirr))
        options.add_experimental_option(
            "excludeSwitches", ['enable-automation', 'enable-logging'])
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--remote-debugging-port=9222")
        # options.add_experimental_option("debuggerAddress", "127.0.0.1:9230")

        self.driver = webdriver.Chrome(
            chromedriver_autoinstaller.install(), options=options)
        # driver.maximize_window()

        self.driver.get('https://casino.bet365.com/Play/LiveRoulette')
        time.sleep(5)

        os.system('cls')

        print("\033[95m" + "=== INFO ===" + "\033[0m")
        print("\033[95m" + "After you login, Press 'Q' to continue" + "\033[0m")
        print("\033[95m" + "=== Bet365 ===" + "\033[0m")

        print("\nQ: pressed continuing...")
        while True:
            if keyboard.is_pressed("q"):
                break
        print("Robyurii Bet365 bot ver.10.0")
        self.driver.implicitly_wait(0)
        open("results.html", "w", encoding="utf8").write(
            self.driver.page_source)
        frame1 = self.single_item(
            '//iframe[@class="inline-games-page-component__game-frame "]')
        self.driver.switch_to.frame(frame1)
        frame = self.single_item('//iframe[@id="gamecontent"]')
        self.driver.switch_to.frame(frame)
        time.sleep(2)
        # self.click_item('//div[@class="close-button header__close-button"]')
        self.close_page()
        time.sleep(2)

        self.switch_tabs()
        # self.click_item('//div[@class="lobby-category-item__name"][text()="Roulette"]')

    def single_item(self, xpath):
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except:
            # print("Item doesn't exist :", xpath)
            return None

    def multi_items(self, xpath):
        try:
            return self.driver.find_elements(By.XPATH, xpath)
        except:
            print("Item doesn't exist :", xpath)
        return None

    def click_item(self, xpath):
        try:
            self.single_item(xpath).click()
        except:
            #print("None clickable :", xpath)
            print("None clickable #1")

    def sub_item(self, item, xpath):
        return item.find_element(By.XPATH, xpath)
    
    def get_history_numbers(self, xpath, cnt):  ########### modify the number and symbol
        ii = 0
        _series_que = [[], []]
        while True:
            _series_que[ii].clear()
            for kp in range(cnt):
                try:
                    _item = self.single_item(xpath + f'/div[{kp+1}]/div/div').text
                except:
                    return None
                        
                        
                if _item.isdigit():
                    _series_que[ii].append(int(_item))
                else:
                    try:
                        _item = self.single_item(xpath + f'/div[{kp+1}]/div[2]/div').text
                        # print("------------------ covered number----------------")
                        if _item.isdigit():
                            _series_que[ii].append(int(_item))
                        else:
                            _series_que[ii].append(-1)
                    except:
                        _series_que[ii].append(-1)
                    

            ii = (ii+1) % 2
            if _series_que[0] == _series_que[1]:
                return _series_que[0].copy()

        
        

    def get_numbers_from_dashboard(self, index):
        return self.get_history_numbers(f'(//div[@class="lobby-table__container"])[position() = {index + 1}]//div[contains(@class,"roulette-history")]', 10)
    
    def get_numbers_from_game(self):
        while True:
            xx = self.get_history_numbers('//div[@class="roulette-game-area__history-line"]/div', 10)
            if not xx:
                print("get numnber from game error occurred!")
                time.sleep(0.2)
                continue
            break
        return xx
            

    def close_page(self):
        self.click_item('//div[@class="close-button header__close-button"]')

    def get_roullete_name(self, index):
        try:
            return self.single_item(f'(//div[@class="lobby-table__container"])[position() = {index + 1}]//div/div[@class="lobby-table__name-container"]').text
        except:
            pass
        return "No name"
    def switch_to_giant_roulette(self):
        self.click_item('//div[@class="lobby-category-item__name"][text()="GAME SHOWS"]')
        time.sleep(0.5)
        ltcnt = self.refresh_lobby_table()  # Item count of Lobby Table
        for i in range(ltcnt):
            roul_title = self.get_roullete_name(i)
            _g_title = roul_title.strip().replace(" ", "_").replace("?", "")
            print(_g_title)
            if _g_title == "Spin_a_Win":
                self.join_roulette(i)
                time.sleep(5)
                return
        # Spin a Win
        
        
    def switch_tabs(self):
        # print("-------------------------------switch ----------------------------------")
        # skip_list.clear()
        sr_str = ["bet365 Exclusive",  "Roulette"]  # "Poker", "GAME SHOWS",

        for item_txt in sr_str:
            # .format(item_txt))
            self.click_item(
                f'//div[@class="lobby-category-item__name"][text()="{item_txt}"]')
            time.sleep(0.5)
        time.sleep(2)

    def refresh_lobby_table(self):
        self.lobby_table = self.multi_items('//div[@class="lobby-table__container"]')
        return len(self.lobby_table)

    def join_roulette(self, index):
        self.close_reality_check()
        try:
            element = self.multi_items('//div[@class="lobby-table__container"]')[index].find_element(By.XPATH, './../../..')
            
            self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
            # driver.execute_script("window.scrollBy(0,0)","")
            html = self.driver.find_element(by=By.TAG_NAME, value='html')
            html.send_keys(Keys.PAGE_UP)
            html.send_keys(Keys.PAGE_UP)
            element.click()
        except Exception as e:
            print(e)
            print(f"Failed to join in Roulette {index}, Try again")
        time.sleep(3)
            # pass
    def close_mega_fire_modal(self):
        try:
            time.sleep(0.3)
            self.single_item('(//div[@class="modal-body"])').find_elements(By.TAG_NAME, "use")[0].click()
            time.sleep(0.5)
            # print(close)
            # close.click()
        except Exception as e:
            print("Error to close the modal of mega fire blaze roulette live!")
            pass
    def get_chip_reference(self):
        # _chips_list = [None,
        #        'chipsPanel.chip50',
        #        'chipsPanel.chip100',
        #        'chipsPanel.chip500',
        #        'chipsPanel.chip1000',
        #        'chipsPanel.chip2500',
        #        'chipsPanel.chip10000',
        #        'chipsPanel.chip50000',
        #        'chipsPanel.chip100000',
        #        None]
        
        try:
        # find(By.XPATH, f'(//div[@class="controls-panel__chip-panel"])').find_elements(
        #     By.TAG_NAME, "svg")[_index].click()
            ppp = self.single_item('(//div[@class="controls-panel__chip-panel"])').find_elements(By.TAG_NAME, "svg")
            _chips_list = []
            for item in ppp:
                # print(item)
                val = item.get_attribute('data-automation-locator')
                # print(val)
                _chips_list.append(val)
        except Exception as e:
            return None
        time.sleep(0.1)
        
        res = []
        for _chip in _chips_list:
            if _chip == None:
                res.append(0)
            else:
                res.append(int(re.findall('[0-9]+', _chip)[0]))
        return res
        
    def get_balance(self):
        try:
            dollar = self.single_item('(//div[@class="account-panel__section account-panel__balance-section"]/div[1]/div[2]/div/div)').text
        except:
            dollar = "Money 0.00"
        return float(re.findall('[0-9.]+', dollar.replace(',',''))[0])
    
    def select_chip(self, _index):
        try:
            self.single_item(f'(//div[@class="controls-panel__chip-panel"])').find_elements(By.TAG_NAME, "svg")[_index].click()
        except Exception as e:
            return False
        # print("select chip ok")
        time.sleep(0.3)
        return True
    def close_reality_check(self):
        while True:
            flag_close = False
            try:
                time_limit_modal = self.single_item('(//div[@class="session-modals"])')
                time_limit_modal.find_elements(By.TAG_NAME, "button")[1].click()
                # time.sleep(0.3)
                print(">>>>>>>>>>>>>>>   Reality check modal is closed")
                flag_close = True
            except:
                pass
            
            
            try:
                inactivity = self.single_item('(//div[@class="game-modals"])')
                inactivity.find_elements(By.TAG_NAME, "button")[0].click()
                # time.sleep(0.3)
                print(">>>>>>>>>>>>>>>   Inactivity modal is closed")
                flag_close = True
            except:
                pass
            
            try:
                inactivity = self.single_item('(//div[@class="toaster-modals"])')
                inactivity.find_elements(By.TAG_NAME, "button")[0].click()
                # time.sleep(0.3)
                print(">>>>>>>>>>>>>>>   Toaster modal is closed")
                flag_close = True
            except:
                pass
            if flag_close:
                time.sleep(1)
                continue
            break
        
        
        
    def click_key(self, _key):
        # return
        _cls_name = {
                 "Low": "roulette-table-cell_side-low",
                 "High": "roulette-table-cell_side-high",
                 "Odd": "roulette-table-cell_side-odd",
                 "Parity": "roulette-table-cell_side-even",
                 "Red": "roulette-table-cell_side-red",
                 "Black": "roulette-table-cell_side-black",
                 "Zero": "roulette-table-cell_straight-0",
                 "Zero0": "roulette-table-cell_straight-00",
                 "Bonus": "roulette-table-cell_straight-bonus",
                 "1st_Dozen" : "roulette-table-cell_side-first-dozen",
                 "2nd_Dozen" : "roulette-table-cell_side-second-dozen",
                 "3rd_Dozen" : "roulette-table-cell_side-third-dozen",
                 "Bottom_Column" : "roulette-table-cell_side-bottom-column",
                 "Middle_Column" : "roulette-table-cell_side-middle-column",
                 "Top_Column" : "roulette-table-cell_side-top-column"
                 }
        # print(20*'-----------')
        # for key in _cls_name.keys():
        try:
            self.single_item('(//div[@class="roulette-game-area__main-digital-table"])').find_element(By.CLASS_NAME, _cls_name[_key]).click()
            time.sleep(0.3)
            # print(f"click {_key}")
            # print(item)
        except Exception as e:
            print(f"error for clicking the key {_key}")
            print(e)
        # print(20*'-----------')
        


# browser = Browser()
# browser.open('https://casino.bet365.com/Play/LiveRoulette')
