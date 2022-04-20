
from doctest import IGNORE_EXCEPTION_DETAIL
import os
from queue import Empty
import time
import keyboard
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tzlocal import get_localzone_name
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import telegram
from progress.bar import Bar
from datetime import datetime, date
import chromedriver_autoinstaller

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

driver = webdriver.Chrome(
    chromedriver_autoinstaller.install(), options=options)
# driver.maximize_window()
driver.get('https://casino.bet365.com/Play/LiveRoulette')
find = driver.find_element
finds = driver.find_elements
games = {}

def get_balance():
    try:
        dollar = find(
            By.XPATH, f'(//div[@class="account-panel__section account-panel__balance-section"]/div[1]/div[2]/div/div)').text
    except:
        dollar = "R$ -1"

    return float(dollar[3:])


def test_select_chip():
    try:
        # find(By.XPATH, f'(//div[@class="controls-panel__chip-panel"])').find_elements(
        #     By.TAG_NAME, "svg")[_index].click()
        ppp = find(By.XPATH, f'(//div[@class="controls-panel__chip-panel"])').find_elements(By.TAG_NAME, "svg")
        
        for item in ppp:
            print(item)
            val = item.get_attribute('data-automation-locator')
            print(val)
            
        
        
    except Exception as e:
        return False
    time.sleep(0.3)
    return True


def test_bet_items():
    _cls_name = {
                 "LOW": "roulette-table-cell_side-low",
                 "HGH": "roulette-table-cell_side-high",
                 "ODD": "roulette-table-cell_side-odd",
                 "PAR": "roulette-table-cell_side-even",
                 "RED": "roulette-table-cell_side-red",
                 "BLK": "roulette-table-cell_side-black",
                 "ZRO": "roulette-table-cell_straight-0",
                 "ZRO1": "roulette-table-cell_straight-00"
                 }
    print(20*'-----------')
    for key in _cls_name.keys():
        try:
            item = find(By.XPATH, f'(//div[@class="roulette-game-area__main-digital-table"])').find_element(By.CLASS_NAME, _cls_name[key])
            print(f"key is {key}")
            print(item)
        except Exception as e:
            print(f"{key} is failed")
            print(e)
    print(20*'-----------')
            
    

def bet_to_roulette(_amount, _key):
    balance = get_balance()
    print("\t Balance is $",balance)
    if balance*10 < _amount:
        print("\t--- balance is lack")
        return
    
    _chip_sr = [25, 50, 250, 500, 1250, 5000, 25000, 50000]
    
    while True: # bet to normal
        for _idx in range(len(_chip_sr)):
            if _chip_sr[_idx]>_amount:
                break
        _idx -= 1
        if _idx>=0:
            select_chip(_idx)
            bet_item(_key, 0)
            print("\t -- bet ${:.1f} ".format(_chip_sr[_idx]/10.0) + "to " + _key)
            _amount -= _chip_sr[_idx]
        else:
            break
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
def join_roulette(index):
    # lobby_table = finds(By.XPATH, '//div[@class="lobby-table__container"]')
    # print('item comunt is ', len(lobby_table))
    # lobby_table[index].find_element(By.XPATH, './../../..').click()
    # while True:
        
    try:
        element = finds(By.XPATH, '//div[@class="lobby-table__container"]')[index].find_element(By.XPATH, './../../..')
        
        driver.execute_script('arguments[0].scrollIntoView(true);', element)
        # driver.execute_script("window.scrollBy(0,0)","")
        html = find(by=By.TAG_NAME, value='html')
        html.send_keys(Keys.PAGE_UP)
        element.click()
        
    except Exception as e:
        print(e)
        print(f"Failed to join in Roulette {index}, Try again")
        
    time.sleep(1)    
      
def close_page():
    find(By.XPATH, '//div[@class="close-button header__close-button"]').click()
  
def startProcess(u):
    os.system('cls')
    print("\033[95m" + "=== INFO ===" + "\033[0m")
    print("\033[95m" +
            "After you login, Press 'Passkey' to continue" + "\033[0m")
    print("\033[95m" + "=== Betnomi ===" + "\033[0m")

    print("\nQ: pressed continuing...")
    while True:
        if keyboard.is_pressed("Q"):
            break
    print("Click test")
    driver.implicitly_wait(1)
    open("results.html", "w", encoding="utf8").write(driver.page_source)
    frame1 = find(
        By.XPATH, '//iframe[@class="inline-games-page-component__game-frame "]')
    driver.switch_to.frame(frame1)
    frame = find(By.XPATH, '//iframe[@id="gamecontent"]')
    driver.switch_to.frame(frame)
    time.sleep(2)

    
    try:
        close = find(
            By.XPATH, '//div[@class="close-button header__close-button"]')
        close.click()
    except NoSuchElementException:
        pass
    time.sleep(2)
    try:
        select_routte = find(
            By.XPATH, '//div[@class="lobby-category-item__name"][text()="Roulette"]')
        select_routte.click()
    except Exception as e:
        print(e)
        
    #get title    
    
    

    switch_kk = True
    while True:
        
        switch_kk = not switch_kk
        # if switch_kk:
        print("\nW: pressed continuing...")
        while True:
            if keyboard.is_pressed("w"):
                break
        join_roulette(13)
        # else:
        print("\nZ: pressed continuing...")
        while True:
            if keyboard.is_pressed("z"):
                break
        close_page()
        # _title = find(By.XPATH, f'(//div[@class="game-table__header"])').find_elements(By.TAG_NAME, "span")[0].text
        # print(_title)
                
        # test_bet_items()
        # test_select_chip()

    

    
        


    #     bar.index = 0

    #     kill_app()


    # bar.finish()
if __name__ == "__main__":
    startProcess('https://casino.bet365.com/Play/LiveRoulette')
