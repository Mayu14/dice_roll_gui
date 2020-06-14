# -- coding: utf-8 --
import PySimpleGUI as sg
from random import randint
from pathlib import Path
from mutagen.mp3 import MP3
from pygame import mixer
from time import time, sleep
from zipfile import ZipFile
from io import BytesIO

srcDir = Path("src")
fzip = srcDir / Path("sound.zip")
fini = "dice_setting.ini"
def __set_default(numDice=8, rareRate=3):
    fname = Path(fini)
    if not fname.exists():
        with open(fname, "w") as f:
            f.write(f"diceNum {numDice}\nrareRate {rareRate}\n")
    else:
        with open(fname, "r") as f:
            txt = f.read()
        txts = txt.split("\n")
        numDice = int(txts[0].split(" ")[1])
        rareRate = int(txts[1].split(" ")[1])
    return numDice, rareRate

def __get_layout(numDice):
    layout = [
        [sg.Text('ダイスの面数'), sg.InputText(default_text=str(numDice), size=(2, 1), key='numDice'), sg.Button("更新", key="update")],
        [sg.Submit('ダイスを振る')]
    ]
    return layout

def __create_window(layout):
    return sg.Window('Dice Roll GUI', layout, resizable=True)

def __reflesh_window(numDice, window):
    layout = __get_layout(numDice)
    window.close()
    window = __create_window(layout)
    return window

def __dice_roll(numDice):
    return randint(1, numDice)

def __get_fpath(ori_num=6, rare_num=33, rareRate=3):
    isRare = randint(1,100) <= rareRate
    if isRare:
        target = randint(1, rare_num)
        target = Path("yj" + str(target).zfill(2) + ".mp3")
    else:
        target = randint(1, ori_num)
        target = Path(str(target).zfill(3) + ".mp3")
    return target
    # return srcDir / target

def __start_sound(fpath):
    with ZipFile(fzip) as myzip:
        with myzip.open(str(fpath)) as mp3_file:
            mp3_bin = BytesIO(mp3_file.read())
    # fpath = fpath.resolve()
    mixer.init()
    # pygame.mixer.music.load(str(fpath))
    mixer.music.load(mp3_bin)
    # mp3_length = MP3(fpath).info.length
    mp3_length = MP3(mp3_bin).info.length
    # mp3_length = 1.0
    mixer.music.play(1)
    start = time()
    return start, mp3_length

def __stop_sound(start, length):
    wait = length - (time() - start)
    if wait > 0:
        sleep(wait)
    mixer.music.stop()
    return None

def main(numDice, rareRate):
    #  セクション1 - オプションの設定と標準レイアウト
    sg.theme('Dark Blue 3')

    layout = __get_layout(numDice=numDice)
    # セクション 2 - ウィンドウの生成
    window = __create_window(layout)

    # セクション 3 - イベントループ
    while True:
        event, values = window.read()

        if event is None:
            with open(Path(fini), "w") as f:
                f.write(f"diceNum {numDice}\nrareRate {rareRate}\n")
            break

        if event == "update":
            numDice = values['numDice']
            numDice = int(numDice)
            window = __reflesh_window(numDice=numDice, window=window)

        if event == 'ダイスを振る':
            # ポップアップ
            zip_status = fzip.exists()
            if zip_status:
                fpath = __get_fpath(rareRate=rareRate)
                start, length = __start_sound(fpath)
            else:
                sg.popup(f'/src/sound.zipがありません')
            dice = __dice_roll(numDice=numDice)
            sg.popup(f'DICE -> {dice}')
            if zip_status:
                __stop_sound(start, length)

    # セクション 4 - ウィンドウの破棄と終了
    window.close()

if __name__ == '__main__':
    # __for_package()
    numDice, rareRate = __set_default()
    main(numDice=numDice, rareRate=rareRate)