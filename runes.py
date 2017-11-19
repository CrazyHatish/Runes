import pyautogui as pygui
import json
from bs4 import BeautifulSoup
from re import compile
from tkinter import Tk, StringVar, Menu
from tkinter.ttk import Combobox, Button
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

client = 0


def main():
    def update_pos(*args):
        position.config(values=positions[tkvar.get().lower()])
        pos.set(positions[tkvar.get().lower()][0])

    champs = []
    scale = 0.8

    try:
        with open('/Riot Games/League of Legends/Config/LCULocalPreferences.yaml') as file:
            for line in file:
                if "ZoomScale" in line:
                    scale = float(line[-9:])
    except FileNotFoundError:
        pass

    try:
        with open('champs.json') as file:
            champs = json.load(file)
    except FileNotFoundError:
        get_champions('champs.json')
        with open('champs.json') as file:
            champs = json.load(file)

    try:
        with open('runes.json') as file:
            rn = json.load(file)
    except FileNotFoundError:
        get_runes('runes.json')
        with open('runes.json') as file:
            rn = json.load(file)

    positions = get_pos(champs)
    screen_size = pygui.size()
    global client
    client = (screen_size[0]/2 - (1024 * scale/0.8)/2, (screen_size[1]-get_taskbar_size())/2 - (576 * scale/0.8)/2)


    root = Tk()
    root.title("Runes")
    root.geometry("350x120")

    tkvar, lang, pos, tree = (StringVar(root), StringVar(root), StringVar(root), StringVar(root))
    tkvar.set("Aatrox")
    lang.set("pt")
    pos.set("Top")
    tree.set("Mais Popular")

    menu = Combobox(root, textvariable=tkvar, values=champs)
    menu.bind("<<ComboboxSelected>>", update_pos)
    menu.place(x = 20, y=70)

    language = Combobox(root, textvariable=lang, values=['en', 'pt'], state='readonly', width=2)
    language.place(x = 20, y=20)

    position = Combobox(root, textvariable=pos, values=positions[tkvar.get().lower()], state='readonly', width=7)
    position.place(x = 90, y=20)

    tree_choose = Combobox(root, textvariable=tree, values=['Mais Popular', 'Melhor Winrate'], state='readonly', width=15)
    tree_choose.place(x = 180, y=20)

    button = Button(root, text="Start", command= lambda:
                                                    make_page(
                                                        get_tree(tkvar.get(), pos.get(), tree.get(), rn),
                                                        lang.get(), scale)
                                                        )
    button.place(x=225, y=68)

    root.mainloop()

def get_tree(champion, pos, tree, rn):

    r = get("http://champion.gg/champion/{}/{}".format(champion, pos))
    runes = []

    soup = BeautifulSoup(r.content, 'html.parser')
    right_side = soup.find_all("div", compile("Slot__RightSide*"))
    keystone = ""

    for element in range(len(right_side)):
        if tree == "Mais Popular" and element >= 8 or tree == "Melhor Winrate" and element < 8:
            m = str(right_side[element].find("div", compile("Description__Title*")).string)
            try:
                if rn.get(m, None) is not None:
                    x = 0
                    if keystone != "" and rn[m][0] > rn[keystone][0]:
                        x = 1
                    keystone = m
                    runes.append(rn[m][0] - x)
                else:
                    runes.append(rn[keystone][1][m])
            except KeyError:
                get_runes('runes.json')
                with open('runes.json') as file:
                    rn = json.load(file)

                if rn.get(m, None) is not None:
                    x = 0
                    if keystone != "" and rn[m][0] > rn[keystone][0]:
                        x = 1
                    keystone = m
                    runes.append(rn[m][0] - x)
                else:
                    runes.append(rn[keystone][1][m])


    return runes

def make_page(runes, lang, scale):
    l_coords = {
        "en": [(485, 98), (459, 98)],
        "pt": [(501, 98), (471, 98)],
        }

    coords = [
        (326, 549), l_coords[lang][0],
        (484, 306), l_coords[lang][1],
        'sleep',
        (170*runes[0], 183), (203 + 54*(runes[1]-1), 262),
        (203 + 54*(runes[2]-4), 340), (203 + 54*(runes[3]-7), 411),
        (203 + 54*(runes[4]-10), 482), (457 + 39*(runes[5]-1), 168),
        (463 + 54*((runes[6]-4)%3), 237 + 63*((runes[6]-4)//3)),
        (463 + 54*((runes[7]-4)%3), 237 + 63*((runes[7]-4)//3)),
    ]

    sleep(1)
    pygui.hotkey('ctrl', '=')
    [pygui.hotkey('ctrl', '-') for _ in range(3)]
    if scale > 0.8:
        pygui.hotkey('ctrl', '=')
        if scale > 1:
            pygui.hotkey('ctrl', '=')
    sleep(1)

    for coord in coords:
        if coord == 'sleep':
            sleep(1)
        else:
            click_client(coord[0] * scale/0.8, coord[1] * scale/0.8)


def click_client(x, y):
    pygui.click(client[0]+x, client[1]+y)
    sleep(0.2)

def get_champions(file):
    c = []
    r = get("http://champion.gg")
    s = r.text

    reg = compile("\/champion\/(.*)\/\w*\"")
    for champ in reg.findall(s):
        if champ not in c:
            c.append(champ)


    with open(file, 'w') as out:
        json.dump(sorted(c), out)

def get_runes(file):
    r = get("https://raw.githubusercontent.com/CrazyHatish/Runes/master/runes.json")

    with open(file, 'w') as out:
        json.dump(r.json(), out)

def get_pos(champs):
    pos = {champ.lower(): [] for champ in champs}

    r = get("http://champion.gg")
    s = r.text

    reg = compile("\/champion\/(.*)\/(\w*)\"")
    try:
        for p in reg.findall(s):
            if p[1] not in pos[p[0].lower()]:
                pos[p[0].lower()].append(p[1])
    except KeyError:
        get_champions('champs.json')
        with open('champs.json') as file:
            champs = json.load(file)

        pos = {champ.lower(): [] for champ in champs}
        for p in reg.findall(s):
            if p[1] not in pos[p[0].lower()]:
                pos[p[0].lower()].append(p[1])


    return pos


if __name__ == "__main__":
    main()
