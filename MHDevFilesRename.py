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
