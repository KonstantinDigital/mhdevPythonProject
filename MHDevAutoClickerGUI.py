#!/usr/bin/env python3

import pyautogui as pag
import tkinter as tk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
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


def edit_cmds():
    global CMDS


def start_thread():
    thread1 = Thread(target=wait_exit, daemon=True)
    thread1.start()
    thread1.join(2)

    thread2 = Thread(target=command_parser, daemon=True)
    thread2.start()

    # thread3 = Thread(target=print_position, daemon=True)
    # thread3.start()

    # if len(sys.argv) > 1:
    #     thread1 = Thread(target=wait_exit)
    #     thread1.start()
    #     thread1.join(2)
    #
    #     thread2 = Thread(target=command_parser, args=sys.argv[1:], daemon=True)
    #     thread2.start()
    #
    #     thread3 = Thread(target=print_position, daemon=True)
    #     thread3.start()


def print_position():
    while True:
        x, y = pag.position()
        string_position = "X: " + str(x).rjust(4) + " Y: " + str(y).rjust(4)
        print(string_position, end="")
        print("\b" * len(string_position), end="", flush=True)


def wait_exit():
    global root
    keyboard.wait("esc")
    root.destroy()


def command_parser():
    global CMDS
    CMDS = CMDS.split()
    print(CMDS)
    pag.PAUSE = 2
    cnt_cycle = int(CMDS[-1])
    if cnt_cycle == 0:
        while True:
            for cmd in CMDS[:-1]:
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
            for cmd in CMDS[:-1]:
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


CMDS = "0"
root = tk.Tk()

root.title("Auto Clicker")
root.geometry("600x600")

b_font = Font(size="16")
m_font = Font(size="12")

l_action = tk.Label(root, font=b_font, text="Choose Action:")
l_action.place(x=230, y=20)

l_pause = tk.Label(root, font=m_font, text="Pause:")
l_pause.place(x=20, y=60)

l_psec = tk.Label(root, font=m_font, text="Sec =")
l_psec.place(x=20, y=90)
e_pause = tk.Entry(root, width=4, font=m_font)
e_pause.place(x=70, y=90)

l_move_to = tk.Label(root, font=m_font, text="Move To:")
l_move_to.place(x=150, y=60)

l_x = tk.Label(root, font=m_font, text="X =")
l_x.place(x=150, y=90)
e_x = tk.Entry(root, width=4, font=m_font)
e_x.place(x=200, y=90)

l_y = tk.Label(root, font=m_font, text="Y =")
l_y.place(x=150, y=115)
e_y = tk.Entry(root, width=4, font=m_font)
e_y.place(x=200, y=115)

l_msec = tk.Label(root, font=m_font, text="Sec =")
l_msec.place(x=150, y=140)
e_msec = tk.Entry(root, width=4, font=m_font)
e_msec.place(x=200, y=140)

b_pause = tk.Button(root, font=m_font, text="Add")
b_pause.place(x=45, y=165)

b_move = tk.Button(root, font=m_font, text="Add")
b_move.place(x=175, y=165)

l_lc = tk.Label(root, font=m_font, text="LClick:")
l_lc.place(x=40, y=250)

b_lc = tk.Button(root, font=m_font, text="Add")
b_lc.place(x=45, y=275)

l_rc = tk.Label(root, font=m_font, text="RClick:")
l_rc.place(x=170, y=250)

b_rc = tk.Button(root, font=m_font, text="Add")
b_rc.place(x=175, y=275)

l_dc = tk.Label(root, font=m_font, text="DClick:")
l_dc.place(x=300, y=250)

b_dc = tk.Button(root, font=m_font, text="Add")
b_dc.place(x=305, y=275)

command_line = ScrolledText(root, width=65, height=1)
command_line.place(x=30, y=465)
command_line.insert(tk.END, CMDS)

b_run = tk.Button(root, font=b_font, text="RUN", command=start_thread)
b_run.place(x=260, y=535)

root.mainloop()
