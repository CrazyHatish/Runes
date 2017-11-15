import pyautogui as pygui
from bs4 import BeautifulSoup
from re import compile
from tkinter import Tk, StringVar
from tkinter.ttk import Combobox, Button
import json
from time import sleep, time
from requests import get
from ctypes import windll, wintypes, byref

SPI_GETWORKAREA = 48
SM_CYSCREEN = 1

def get_taskbar_size():
    SystemParametersInfo = windll.user32.SystemParametersInfoA
    work_area = wintypes.RECT()
    if (SystemParametersInfo(SPI_GETWORKAREA, 0, byref(work_area), 0)):
        GetSystemMetrics = windll.user32.GetSystemMetrics
        return GetSystemMetrics(SM_CYSCREEN) - work_area.bottom

screen_size = pygui.size()
client = (screen_size[0]/2 - 1024/2, (screen_size[1]-get_taskbar_size())/2 - 576/2)


def main():
    champs = []

    try:
        with open('champs.json') as file:
            champs = json.load(file)
    except FileNotFoundError:
        get_champions('champs.json')
        with open('champs.json') as file:
            champs = json.load(file)

    root = Tk()
    root.geometry("400x120")

    tkvar, lang, pos, tree = (StringVar(root), StringVar(root), StringVar(root), StringVar(root))
    tkvar.set("Aatrox")
    lang.set("pt")
    pos.set("Top")
    tree.set("Mais Popular")

    menu = Combobox(root, textvariable=tkvar, values=champs)
    menu.place(x = 50, y=70)

    language = Combobox(root, textvariable=lang, values=['en', 'pt'], width=2)
    language.place(x = 50, y=20)

    position = Combobox(root, textvariable=pos, values=['Top', 'Jungle', 'Middle', 'ADC', 'Support'], width=6)
    position.place(x = 120, y=20)

    tree_choose = Combobox(root, textvariable=tree, values=['Mais Popular', 'Melhor Winrate'], width=15)
    tree_choose.place(x = 200, y=20)

    button = Button(root, text="Start", command= lambda: make_page(get_tree(tkvar.get(), pos.get(), tree.get()), lang.get()))
    button.place(x=250, y=70)

    root.mainloop()

def get_tree(champion, pos, tree):
    with open('m.json') as file:
        rn = json.load(file)

    r = get("http://champion.gg/champion/{}/{}".format(champion, pos))
    runes = []

    soup = BeautifulSoup(r.content, 'html.parser')
    right_side = soup.find_all("div", compile("Slot__RightSide*"))
    keystone = ""

    for element in range(len(right_side)):
        if tree == "Mais Popular" and element >= 8 or tree == "Melhor Winrate" and element < 8:
            m = str(right_side[element].find("div", compile("Description__Title*")).string)
            if rn.get(m, None) is not None:
                x = 0
                if keystone != "" and rn[m][0] > rn[keystone][0]:
                    x = 1
                keystone = m
                runes.append(rn[m][0] - x)
            else:
                runes.append(rn[keystone][1][m])

    return runes

def make_page(runes, lang):
    coords = {
        "en": [(485, 98), (459, 98)],
        "pt": [(501, 98), (471, 98)],
        }

    sleep(1)
    pygui.hotkey('ctrl', '=')
    [pygui.hotkey('ctrl', '-') for _ in range(3)]
    sleep(1)

    click_client(326, 549)
    click_client(coords[lang][0][0], coords[lang][0][1])
    click_client(484, 306)
    click_client(coords[lang][1][0], coords[lang][1][1])
    sleep(1)
    click_client(170*runes[0], 183)
    click_client(203 + 54*(runes[1]-1), 262)
    click_client(203 + 54*(runes[2]-4), 340)
    click_client(203 + 54*(runes[3]-7), 411)
    click_client(203 + 54*(runes[4]-10), 482)
    click_client(457 + 39*(runes[5]-1), 168)
    click_client(463 + 54*((runes[6]-4)%3), 237 + 63*((runes[6]-4)//3))
    click_client(463 + 54*((runes[7]-4)%3), 237 + 63*((runes[7]-4)//3))


def click_client(x, y):
    pygui.click(client[0]+x, client[1]+y)
    sleep(0.2)

def get_champions(file):
    champs = []
    c = []
    r = get("https://ddragon.leagueoflegends.com/cdn/6.24.1/data/en_US/champion.json")
    champs = r.json()

    for k, v in champs['data'].items():
        c.append(k)

    with open(file, 'w') as out:
        json.dump(c, out)



if __name__ == "__main__":
    main()
