import os
import time
import keyboard
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import telegram
from progress.bar import Bar
from datetime import datetime, date

global bot
global TOKEN
global CHANNEL_ID
global cur_time
global prev_time
global SHARK_TELEGRAM_ID
global skip_list
CHANNEL_ID = '-1001780647070'
TOKEN = '5159944284:AAGi7KKEs4IUYR1GbAQo6PXpom5SxgQu7pY'
SHARK_TELEGRAM_ID = '1863767894'
skip_list = []


# if datetime.now().date() > date(2022, 5, 2):
#     quit()
    
bot = telegram.Bot(token=TOKEN)
cur_time = time.time()
prev_time = time.time()

dirr = os.path.abspath(os.curdir).rsplit("\\", 1)[0] + "\\userdata"

options = Options()
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features")
options.add_argument("excludeSwitches")
options.add_argument(r"user-data-dir={}".format(dirr))
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--remote-debugging-port=9222")
print("\033[95m" + "=== INFO ===" + "\033[0m")
print("\033[95m" + "After you login please, press q to continue" + "\033[0m")
print("\033[95m" + "=== Bet365 ===" + "\033[0m")
# options.add_experimental_option("debuggerAddress", "127.0.0.1:9230")
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
# driver.maximize_window()
find = driver.find_element
finds = driver.find_elements

games = {}


def send_1st_msg_if_any(g_title, _detail, _opp_detail,  tgt, glist, cnt):
    glen = len(glist)
    if cnt > glen:
        return

    for i in range(cnt):
        qq = glist[-1-i]
        if qq in tgt:
            continue
        return

    if(cnt != glen):
        if glist[-1-cnt] in tgt:
            return

    txt = "🚨 REPETITION IN ROULETTE : {0}\n📊 REPEAT: {1}\n!! Bet on: {2}!!!".format(
        g_title, _detail, _opp_detail)

    try:
        bot.sendMessage(chat_id=CHANNEL_ID, text=txt)
    except:
        print("try again(request telegram1)")
    # print(txt)
    time.sleep(0.5)


def send_2nd_msg_if_any(g_title, _detail, tgt, glist, cnt):
    glen = len(glist)

    if cnt+1 > glen or glist[-1] < 0 or glist[-1] in tgt:
        return
    pp = 0
    for i in range(glen):
        if i >= glen-1:
            break
        if glist[-2-i] < 0:
            break
        qq = glist[-2-i]
        if qq in tgt:
            pp += 1
            continue
        break
    if pp < cnt:
        return
    pp -= cnt

    txt = "🏁Turn finished, roulette: {0}\n\n📊Repetition of {1}\n\n⚠️ MOVES: {2}\n🤑 We won with  the number: {3}".format(
        g_title, _detail, str(glist[-pp-1:len(glist)-1]).strip("[]"), glist[-1])

    try:
        bot.sendMessage(chat_id=CHANNEL_ID, text=txt)
    except:
        print("try again(request telegram2)")
    # print
    # (txt)
    time.sleep(.5)


def read_conditions():
    con_file = open('conditions.txt', 'r')
    Lines = con_file.readlines()
    result = []
    for line in Lines:
        result.append(line)
    con_file.close()
    return result


def find_repetition(glist, condt, g_title):
    red = [0, 1, 3, 5, 7, 9, 12, 14, 16, 18,
           19, 21, 23, 25, 27, 30, 32, 34, 36]
    black = [0, 2, 4, 6, 8, 10, 11, 13, 15, 17,
             20, 22, 24, 26, 28, 29, 31, 33, 35]
    col1 = [0, 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
    col2 = [0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
    col3 = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
    doz1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    doz2 = [0, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    doz3 = [0, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    odd = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17,
           19, 21, 23, 25, 27, 29, 31, 33, 35]
    parity = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
              20, 22, 24, 26, 28, 30, 32, 34, 36]
    low = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    high = [0, 19, 20, 21, 22, 23, 24, 25, 26,
            27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    IDS = condt[:3]
    cnt = int(condt[3:])

    _que = [red, black, col1, col2, col3, doz1,
            doz2, doz3, odd, parity, low, high]
    _key = ["RED", "BLK", "COL", "COL", "COL", "DOZ",
            "DOZ", "DOZ", "ODD", "PAR", "LOW", "HGH"]

    _detail = ["RED COLOR", "BLACK COLOR", "1ST COLUMN", "2nd COLUMN", "3rd COLUMN", "1ST DOZEN", "2ND DOZEN", "3RD DOZEN", "ODD NUMBER", "EVEN NUMBER", "LOW NUMBERS", "HIGH NUMBERS"]
    _opp_detail =  ["BLACK COLOR", "RED COLOR", "2nd, 3rd COLUMN", "1st, 3rd COLUMN", "1st, 2nd COLUMN", "2nd, 3rd DOZEN", "1st, 3rd DOZEN", "1st, 2nd DOZEN" , "EVEN NUMBER", "ODD NUMBER", "HIGH NUMBERS", "LOW NUMBERS"]
    for i in range(12):
        if IDS == _key[i]:
            send_1st_msg_if_any(g_title, _detail[i], _opp_detail[i], _que[i], glist, cnt)
            send_2nd_msg_if_any(g_title, _detail[i], _que[i], glist, cnt)


def find_index_list(tgt, src):
    tlen = len(tgt)
    slen = len(src)
    for i in range(tlen - slen+1):
        if tgt[i:i+slen] == src:
            return i
    return -1


def find_valid_items(index):
    ii = 0
    _series_que = [[], []]
    while True:
        _series_que[ii].clear()
        for kp in range(10):
            try:
                _item = find(
                    By.XPATH, f'(//div[@class="lobby-table__container"])[position() = {index + 1}]//div[contains(@class,"roulette-history")]/div[{kp+1}]/div/div').text
            except:
                return "failed"

            if _item.isdigit():
                _series_que[ii].append(int(_item))
            else:
                _series_que[ii].append(-1)

        ii = (ii+1) % 2
        if _series_que[0] == _series_que[1]:
            return _series_que[0].copy()

def get_roullete_name(index):
    rname = "No name"
    try:
        rname = find(By.XPATH, f'(//div[@class="lobby-table__container"])[position() = {index + 1}]//div/div[@class="lobby-table__name-container"]').text
    except:
        pass
    return rname

def kill_app():
    if keyboard.is_pressed('esc'):
        print('finished')
        quit()


def switch_tabs():
    global prev_time
    cur_time = time.time()
    elapsed = cur_time - prev_time

    _flag_pass = True
    if elapsed > 120 or _flag_pass:
        # print("elapsed time {:.1f}\n After switching tabs, it will continue.".format(elapsed))
        prev_time = cur_time
        skip_list.clear()
        sr_str = ["bet365 Exclusive",  "Roulette"] #"Poker", "GAME SHOWS", 

        for item_txt in sr_str:
            try:
                select_routte = find(
                    # lobby-categories__panel lobby-categories_size-7
                    By.XPATH, '//div[@class="lobby-category-item__name"][text()="{0}"]'.format(item_txt))
                
            except Exception as e:
                print(e)
                continue
            select_routte.click()
            time.sleep(0.5)
        time.sleep(1)


def startProcess(u):
    os.system('cls')
    
    driver.get(u)
    time.sleep(5)
    # _inactivity = 0
    while True:
        if keyboard.is_pressed("q"):
            print("\nQ: pressed continuing...")
            break
    print("Shark Bet365 bot ver.2.2")
    driver.implicitly_wait(30)
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

    bar = Bar('Processing')

    while True:
        switch_tabs()
        condition = read_conditions()
        divs = finds(By.XPATH, '(//div[@class="lobby-table__container"])')
        bar.max = len(divs)
        for i in range(len(divs)):
            kill_app()
            bar.next()
            
            names = get_roullete_name(i)            

            if names in skip_list:
                continue

            if names == "No name":
                # print(names)
                # print("No name! index is : {0}".format(i))
                kill_app()
                continue
            

            numbers = find_valid_items(i)
            
            vnames = get_roullete_name(i)
            if names!=vnames:
                # print (".....................................................updated during capture")
                break

            if(numbers == "failed"):
                kill_app()
                skip_list.append(names)
                # print(" Skip {0}".format(names))
                continue



            # end of while
            lis_name = names.strip().replace(" ", "_").replace("?", "")
            try:
                games[lis_name] # if the lis_name is new
            except KeyError:
                games[lis_name] = numbers.copy()
                games[lis_name].reverse()

            temps = games[lis_name].copy()
            temps.reverse()

            # temps= [21, 4, 12, 31, 22, 22, 35, 15, 22, 1]
            # numbers = [29, 21, 4, 12, 31, 22, 22, 35, 15, 22]
            fidx = find_index_list(temps, numbers[5:])
            # print("            >>  ",fidx,"     -------:", names, "------------:    ", numbers) ###############################################################################
            if fidx > 5 or fidx < 0:
                games[lis_name] = numbers.copy()
                games[lis_name].reverse()
                continue

            if fidx == 5:
                continue
            #     _inactivity += 1
            #     print("\ninactivity {0}".format(_inactivity))
                
            #     if _inactivity > 300:
            #         print("Bet365 is in inactivity")
            #         bot.sendMessage(chat_id=SHARK_TELEGRAM_ID,  text='‼️ CONFIGURAR ROBÔ 🤖 ')
            #         quit()
                    
            

            # _inactivity = 0
            fidx = 5 - fidx
            
            for jj in range(fidx):
                games[lis_name].append(numbers[fidx-jj-1])

            # print("---------------", fidx, names + " : " + str(games[lis_name])[1:-1])

            for cdt in condition:
                find_repetition(
                    games[lis_name], cdt, lis_name.replace("_", " "))

            while len(games[lis_name]) > 15:
                games[lis_name].pop(0)
        bar.index = 0

        kill_app()

    bar.finish()


if __name__ == "__main__":
    startProcess('https://casino.bet365.com/Play/LiveRoulette')
