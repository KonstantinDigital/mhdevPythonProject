#!/usr/bin/env python3
# 2022 MHDEv
# This program automates mouse and keyboard actions on the screen

import pyautogui as pag
import sys
import keyboard
from threading import Thread


def main():
    if len(sys.argv) > 1:
        thread1 = Thread(target=wait_exit)
        thread1.start()
        thread1.join(1)

        thread2 = Thread(target=command_parser, args=sys.argv[1:], daemon=True)
        thread2.start()

        thread3 = Thread(target=print_position, daemon=True)
        thread3.start()
    elif len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: python MHDevAutoClicker.py p,0.5[pause between actions (default 1 sec)] "
              "m,1335,124,0.5[move to x, y, action time (default 1 sec)] lc[left click] m,1462,901 lc "
              "300[number of cycles (0 = infinite times)]\nTo STOP and EXIT programm press Esc")
        sys.exit()


def print_position():
    while True:
        x, y = pag.position()
        string_position = "X: " + str(x).rjust(4) + " Y: " + str(y).rjust(4)
        print(string_position, end="")
        print("\b" * len(string_position), end="", flush=True)


def wait_exit():
    print("Press Esc to Exit programm")
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
