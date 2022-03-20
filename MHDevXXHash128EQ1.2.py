#!/usr/bin/env python3
# 2021 MHDEv
# This program searches for duplicate files in the specified directory
# by comparing their hashes and saves the results to a file

import os
from datetime import datetime
from time import time
from xxhash import xxh3_128_digest as xxh128


def main():
    try:
        path = input('Введите путь к папке: ')
        log_file = input('Введите букву диска для сохранения лога: ') + ':\\log.txt'
        find_file(path, log_file)
    except Exception as e:
        input('Error: ' + str(e) + ' сек. Нажмите ENTER')
        f = open(log_file, encoding='utf-8', mode='a')
        f.write(''.join('\n' + str(datetime.now())[:-7] + '\nError: ' + str(e) + '\n'))
        f.close()


def find_file(path, log_file):
    try:
        start = time()
        os.chdir(path)
        f = open(log_file, encoding='utf-8', mode='a')
        f.write(''.join('\n' + str(datetime.now())[:-7]))
        f.close()
        file_list = []
        file_id = 1
        for root, dirs, files in os.walk('.'):
            for name in files:
                temp = []
                path = os.path.join(root, name)
                temp.append(path)
                temp.append(get_hash(path, log_file))
                temp.append(file_id)
                file_list.append(temp)
                print('ID: ' + str(temp[2]) + '  "' + temp[0] + '" ' + ' XXH3_128 = ' + str(temp[1]))
                file_id += 1
        equal_hash(file_list, log_file, start)
    except Exception as e:
        f = open(log_file, encoding='utf-8', mode='a')
        f.write(''.join('\nError: ' + str(e) + '\n'))
        f.close()
        input('Error: ' + str(e) + ' сек. Нажмите ENTER')


def get_hash(file, log_file):
    try:
        with open(file, 'rb') as f:
            data = f.read()
            read_hash = xxh128(data)
        f.close()
        return read_hash
    except Exception as e:
        f = open(log_file, encoding='utf-8', mode='a')
        f.write(''.join('\nError: ' + str(e) + '\n'))
        f.close()
        input('Error: ' + str(e) + ' сек. Нажмите ENTER')


def equal_hash(lst, log_file, start):
    try:
        print("\nEqual XXhash xxh3_128")
        rec_id = set()
        for i in range(len(lst)):
            for j in range(len(lst)):
                if lst[i][1] == lst[j][1] and lst[i][0] != lst[j][0] and \
                        lst[i][2] not in rec_id and lst[j][2] not in rec_id:
                    f = open(log_file, encoding='utf-8', mode='a')
                    f.write(''.join('\nID: ' + str(lst[i][2]) + '  "' + lst[i][0] + '" ' + ' *****====***** ' + 'ID: ' +
                                    str(lst[j][2]) + '  "' + lst[j][0] + '"'))
                    f.close()
                    print('ID: ' + str(lst[i][2]) + '  "' + lst[i][0] + '" ' + ' *****====***** ' + 'ID: ' +
                          str(lst[j][2]) + '  "' + lst[j][0] + '"')
                    rec_id.add(lst[i][2])
                    rec_id.add(lst[j][2])
        f = open(log_file, encoding='utf-8', mode='a')
        f.write(''.join('\nПрограмма выполнена за ' + str(-int(start - time())) + ' сек.\n'))
        f.close()
        input('Программа выполнена за ' + str(-int(start - time())) + ' сек. Нажмите ENTER')
    except Exception as e:
        f = open(log_file, encoding='utf-8', mode='a')
        f.write(''.join('\nError: ' + str(e) + '\n'))
        f.close()
        input('Error: ' + str(e) + ' сек. Нажмите ENTER')


if __name__ == '__main__':
    main()
