import tkinter
from tkinter import *
from tkinter import scrolledtext

from_conv = 2
to_conv = 2
num = 0
lang = "русский"


def convert_from():
    try:
        global from_conv
        global num
        from_conv = int(from_conv_var.get())
        num = str(enter_number.get())
        if from_conv == 2:
            num = int(num, 2)
            convert_to()
        elif from_conv == 8:
            num = int(num, 8)
            convert_to()
        elif from_conv == 10:
            num = int(num, 10)
            convert_to()
        elif from_conv == 16:
            num = int(num, 16)
            convert_to()
    except:
        set_error()


def convert_to():
    try:
        global num
        global to_conv
        to_conv = int(to_conv_var.get())
        if to_conv == 2:
            num = bin(num)
            set_result()
        elif to_conv == 8:
            num = oct(num)
            set_result()
        elif to_conv == 10:
            num = str(num)
            set_result()
        elif to_conv == 16:
            num = hex(num)
            set_result()
    except:
        set_error()


def set_result():
    global lang
    if lang == "english":
        con_result.configure(state="normal")
        con_result.insert(END, num + "\n")
        con_result.yview(END)
        con_result.configure(state="disabled")
        result_label.config(text="Current result:")
        result_num_label.config(text=str(num))
    else:
        con_result.configure(state="normal")
        con_result.insert(END, num + "\n")
        con_result.yview(END)
        con_result.configure(state="disabled")
        result_label.config(text="Текущий результат:")
        result_num_label.config(text=str(num))


def set_error():
    global lang
    if lang == "english":
        con_result.configure(state="normal")
        con_result.insert(END, "Data entered incorrectly!" + "\n")
        con_result.yview(END)
        con_result.configure(state="disabled")
        result_label.config(text="Data entered incorrectly!")
        result_num_label.config(text="")
    else:
        con_result.configure(state="normal")
        con_result.insert(END, "Некорректно введены данные!" + "\n")
        con_result.yview(END)
        con_result.configure(state="disabled")
        result_label.config(text="Некорректно введены данные!")
        result_num_label.config(text="")


def change_lang(selection):
    global lang
    if selection == "english":
        lang = "english"
        lang_option_label.config(text="Language:")
        from_conv_label.config(text="From which number system:")
        to_conv_label.config(text="In which number system:")
        enter_label.config(text="Enter number:")
        convert_button.config(text="Convert")
        result_label.config(text="Current result:")
        button_end.config(text="Exit")
        return "english"
    else:
        lang = "русский"
        lang_option_label.config(text="Язык:")
        from_conv_label.config(text="Из какой системы счисления:")
        to_conv_label.config(text="В какую систему счисления:")
        enter_label.config(text="Введите число:")
        convert_button.config(text="Перевести")
        result_label.config(text="Текущий результат:")
        button_end.config(text="Закончить")
        return "русский"


def kill_window():
    global root
    root.destroy()
    root.quit()


from_conv_option = [2, 8, 10, 16]
to_conv_option = [2, 8, 10, 16]
lang_option = ["русский", "english"]

root = Tk()

lang_option_label = tkinter.Label(text="Язык:")
lang_option_label.pack()
lang_option_var = StringVar(root)
lang_option_var.set(lang_option[0])
lang_option_menu = OptionMenu(root, lang_option_var, *lang_option, command=change_lang)
lang_option_menu.pack()

from_conv_label = tkinter.Label(text="Из какой системы счисления:")
from_conv_label.pack()
from_conv_var = StringVar(root)
from_conv_var.set(from_conv_option[0])
from_conv_menu = OptionMenu(root, from_conv_var, *from_conv_option)
from_conv_menu.pack()

enter_label = tkinter.Label(text="Введите число:")
enter_label.pack()
enter_number = tkinter.Entry(width=43)
enter_number.pack()

to_conv_label = tkinter.Label(text="В какую систему счисления:")
to_conv_label.pack()
to_conv_var = StringVar(root)
to_conv_var.set(to_conv_option[0])
to_conv_menu = OptionMenu(root, to_conv_var, *to_conv_option)
to_conv_menu.pack()

convert_button = tkinter.Button(text="Перевести", width=10, height=1, command=convert_from)
convert_button.pack()
con_result = tkinter.scrolledtext.ScrolledText(width=30, height=8, state="disabled")
con_result.pack()
result_label = tkinter.Label(text="Текущий результат:")
result_label.pack()
result_num_label = tkinter.Label(text="")
result_num_label.pack()

button_end = tkinter.Button(text="Закончить", width=10, height=1, command=kill_window)
button_end.pack()

root.title("Number System Converter")
root.geometry('300x450')

root.mainloop()
