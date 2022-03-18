#!/usr/bin/env python3

import pyautogui as pag
import tkinter as tk
import sys
import keyboard
from threading import Thread
import os

# pag.position() - текущая позиция мыши
# pag.click() - клик левой кнопкой мыши
# pag.click(button="right") - клик правой кнопкой мыши
# pag.doubleClick() - двойной клик
# pag.moveTo(x, y, sec) - перемещение мыши за сколько секунд
# pag.dragTo(300, 400, 2, button="left") - перетащить мышь
# pag.press("enter") - нажать Enter
# pag.hotkey("ctrl", "c") - сочетание нажатия клавиш
# pag.PAUSE = 1 - одна инструкция каждую секунду
# pag.write("default", interval=0.3) - ввод с клавиатуры
# python MHDevAutoClicker.py p,0.5 m,1335,124,0.5 lc m,1462,901 lc m,784,506 lc m,1635,16 lc m,999,125 lc 300

WORK = True


def main():
    if len(sys.argv) > 1:
        thread1 = Thread(target=wait_exit)
        thread1.start()
        thread1.join(2)

        thread2 = Thread(target=command_parser, args=sys.argv[1:], daemon=True)
        thread2.start()

        thread3 = Thread(target=print_position, daemon=True)
        thread3.start()


def print_position():
    while True:
        x, y = pag.position()
        string_position = "X: " + str(x).rjust(4) + " Y: " + str(y).rjust(4)
        print(string_position, end="")
        print("\b" * len(string_position), end="", flush=True)


def wait_exit():
    # global WORK
    # while WORK:
    #     if keyboard.is_pressed("esc"):
    #         sys.exit()
    # sys.exit()
    keyboard.wait("esc")
    sys.exit()


def command_parser(*cmds):
    global WORK
    pag.PAUSE = 1
    cnt_cycle = int(cmds[-1])
    if cnt_cycle == 0:
        while True:
            for cmd in cmds[:-1]:
                cmd = cmd.split(",")
                if cmd[0] == "m":
                    sec = float(cmd[3]) if len(cmd) > 3 else 1
                    pag.moveTo(int(cmd[1]), int(cmd[2]), sec)
                elif cmd[0] == "p":
                    pag.PAUSE = float(cmd[1])
                elif cmd[0] == "lc":
                    pag.click()
                elif cmd[0] == "rc":
                    pag.click(button="right")
                elif cmd[0] == "dc":
                    pag.doubleClick()
                elif cmd[0] == "e":
                    pag.press("enter")
    else:
        while cnt_cycle > 0:
            for cmd in cmds[:-1]:
                cmd = cmd.split(",")
                if cmd[0] == "m":
                    sec = float(cmd[3]) if len(cmd) > 3 else 1
                    pag.moveTo(int(cmd[1]), int(cmd[2]), sec)
                elif cmd[0] == "p":
                    pag.PAUSE = float(cmd[1])
                elif cmd[0] == "lc":
                    pag.click()
                elif cmd[0] == "rc":
                    pag.click(button="right")
                elif cmd[0] == "dc":
                    pag.doubleClick()
                elif cmd[0] == "e":
                    pag.press("enter")
            cnt_cycle -= 1
        WORK = False


if __name__ == '__main__':
    main()
