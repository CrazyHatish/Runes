import json
from ctypes import windll, wintypes, byref
from tkinter import Tk, StringVar
from tkinter.ttk import Combobox, Button

import pyautogui as pygui
from functions import make_page, get_tree, get_runes, get_pos, get_champions


def main():
    SPI_GETWORKAREA = 48
    SM_CYSCREEN = 1

    def get_taskbar_size():
        SystemParametersInfo = windll.user32.SystemParametersInfoA
        work_area = wintypes.RECT()
        if SystemParametersInfo(SPI_GETWORKAREA, 0, byref(work_area), 0):
            GetSystemMetrics = windll.user32.GetSystemMetrics
            return GetSystemMetrics(SM_CYSCREEN) - work_area.bottom

    def update_pos(*args):
        position.config(values=positions[tkvar.get().lower()])
        pos.set(positions[tkvar.get().lower()][0])

    champs = []
    scale = 0.8

    try:
        with open(
            "/Riot Games/League of Legends/Config/LCULocalPreferences.yaml"
        ) as file:
            for line in file:
                if "ZoomScale" in line:
                    scale = float(line[-9:])
    except FileNotFoundError:
        pass

    try:
        with open("champs.json") as file:
            champs = json.load(file)
    except FileNotFoundError:
        get_champions("champs.json")
        with open("champs.json") as file:
            champs = json.load(file)

    try:
        with open("runes.json") as file:
            rn = json.load(file)
    except FileNotFoundError:
        get_runes("runes.json")
        with open("runes.json") as file:
            rn = json.load(file)

    positions = get_pos(champs)
    screen_size = pygui.size()
    client = (
        screen_size[0] / 2 - (1024 * scale / 0.8) / 2,
        (screen_size[1] - get_taskbar_size()) / 2 - (576 * scale / 0.8) / 2,
    )

    root = Tk()
    root.title("Runes")
    root.geometry("350x120")

    tkvar, lang, pos, tree = (
        StringVar(root),
        StringVar(root),
        StringVar(root),
        StringVar(root),
    )
    tkvar.set("Aatrox")
    lang.set("en")
    pos.set("Top")
    tree.set("Mais Popular")

    menu = Combobox(root, textvariable=tkvar, values=champs)
    menu.bind("<<ComboboxSelected>>", update_pos)
    menu.place(x=20, y=70)

    language = Combobox(
        root, textvariable=lang, values=["en", "pt"], state="readonly", width=2
    )
    language.place(x=20, y=20)

    position = Combobox(
        root,
        textvariable=pos,
        values=positions[tkvar.get().lower()],
        state="readonly",
        width=7,
    )
    position.place(x=90, y=20)

    tree_choose = Combobox(
        root,
        textvariable=tree,
        values=["Most Popular", "Best Winrate"],
        state="readonly",
        width=15,
    )
    tree_choose.place(x=180, y=20)

    button = Button(
        root,
        text="Start",
        command=lambda: make_page(
            get_tree(tkvar.get(), pos.get(), tree.get(), rn), lang.get(), scale, client
        ),
    )
    button.place(x=225, y=68)

    root.mainloop()


if __name__ == "__main__":
    main()
