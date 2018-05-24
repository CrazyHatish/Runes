import json
from re import compile
from time import sleep

import pyautogui as pygui
from bs4 import BeautifulSoup
from requests import get


def get_tree(champion, pos, tree, rn):
    r = get("http://champion.gg/champion/{}/{}".format(champion, pos))
    runes = []

    soup = BeautifulSoup(r.content, "html.parser")
    right_side = soup.find_all("div", compile("Slot__RightSide*"))
    keystone = ""

    for element in range(len(right_side)):
        if (
            tree == "Mais Popular"
            and element >= 8
            or tree == "Melhor Winrate"
            and element < 8
        ):
            m = str(
                right_side[element].find("div", compile("Description__Title*")).string
            )
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
                get_runes("runes.json")
                with open("runes.json") as file:
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


def make_page(runes, lang, scale, client):
    def click_client(x, y):
        pygui.click(client[0] + x, client[1] + y)
        sleep(0.2)

    l_coords = {"en": [(485, 98), (459, 98)], "pt": [(501, 98), (471, 98)]}

    coords = (
        (350, 545),
        l_coords[lang][0],
        (484, 306),
        l_coords[lang][1],
        "sleep",
        (170 * runes[0], 183),
        (203 + 54 * (runes[1] - 1), 262),
        (203 + 54 * (runes[2] - 4), 340),
        (203 + 54 * (runes[3] - 7), 411),
        (203 + 54 * (runes[4] - 10), 482),
        (457 + 39 * (runes[5] - 1), 168),
        (463 + 54 * ((runes[6] - 4) % 3), 237 + 63 * ((runes[6] - 4) // 3)),
        (463 + 54 * ((runes[7] - 4) % 3), 237 + 63 * ((runes[7] - 4) // 3)),
    )

    sleep(1)
    pygui.hotkey("ctrl", "=")
    [pygui.hotkey("ctrl", "-") for _ in range(3)]
    if scale > 0.8:
        pygui.hotkey("ctrl", "=")
        if scale > 1:
            pygui.hotkey("ctrl", "=")
    sleep(1)

    for coord in coords:
        if coord == "sleep":
            sleep(1)
        else:
            click_client(coord[0] * scale / 0.8, coord[1] * scale / 0.8)


def get_champions(file):
    c = []
    r = get("http://champion.gg")
    s = r.text

    reg = compile(r'/champion/(.*)/\w*"')
    for champ in reg.findall(s):
        if champ not in c:
            c.append(champ)

    with open(file, "w") as out:
        json.dump(sorted(c), out)


def get_runes(file):
    r = get("https://raw.githubusercontent.com/CrazyHatish/Runes/master/runes.json")

    with open(file, "w") as out:
        json.dump(r.json(), out)


def get_pos(champs):
    pos = {champ.lower(): [] for champ in champs}

    r = get("http://champion.gg")
    s = r.text

    reg = compile(r'/champion/(.*)/(\w*)"')
    try:
        for p in reg.findall(s):
            if p[1] not in pos[p[0].lower()]:
                pos[p[0].lower()].append(p[1])
    except KeyError:
        get_champions("champs.json")
        with open("champs.json") as file:
            champs = json.load(file)

        pos = {champ.lower(): [] for champ in champs}
        for p in reg.findall(s):
            if p[1] not in pos[p[0].lower()]:
                pos[p[0].lower()].append(p[1])

    return pos