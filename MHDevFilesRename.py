#!/usr/bin/env python3
# 2021 MHDEv
# This program renames files in the specified directory by deleting the specified
# number of characters from the beginning of the file name

import os


def main():
    my_dir = input("Введите путь к папке: ")
    sym_num = int(input("Сколько символов удалить: "))
    if os.path.isdir(my_dir):
        os.chdir(my_dir)
        for root, dirs, files in os.walk("."):
            for name in files:
                os.rename(name, name[sym_num:])


if __name__ == '__main__':
    main()
