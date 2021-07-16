import os
from datetime import datetime
from time import time


def main():
    try:
        path = input('Введите путь к папке: ')
        log_file = input('Введите букву диска для сохранения лога: ') + ':\\del_log.txt'
        open_files(path, log_file)
    except Exception as e:
        input('Error: ' + str(e) + ' сек. Нажмите ENTER')
        log = open(log_file, encoding='utf-8', mode='a')
        log.write(''.join('\n' + str(datetime.now())[:-7] + '\nError: ' + str(e) + '\n'))
        log.close()


def open_files(path, log_file):
    try:
        start = time()
        os.chdir(path)
        log = open(log_file, encoding='utf-8', mode='a')
        log.write(''.join('\n' + str(datetime.now())[:-7]))
        log.close()
        f = open('del_lst.txt', encoding='utf-8', mode='r')
        for line in f:
            for root, dirs, files in os.walk('.'):
                for name in files:
                    path = os.path.join(root, name)
                    if path == line[1:-2]:
                        os.remove(path)
                        log = open(log_file, encoding='utf-8', mode='a')
                        log.write(''.join('\n' + path + ' - файл удален'))
                        log.close()
                        print(path + ' - файл удален')
        log = open(log_file, encoding='utf-8', mode='a')
        log.write(''.join('\nПрограмма выполнена за ' + str(-int(start - time())) + ' сек.\n'))
        log.close()
        input('Программа выполнена за ' + str(-int(start - time())) + ' сек. Нажмите ENTER')
    except Exception as e:
        log = open(log_file, encoding='utf-8', mode='a')
        log.write(''.join('\nError: ' + str(e) + '\n'))
        log.close()
        input('Error: ' + str(e) + ' сек. Нажмите ENTER')


if __name__ == '__main__':
    main()
