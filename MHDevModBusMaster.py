import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import serial
from PIL import ImageTk, Image
from tkinter import messagebox
from threading import Thread, RLock, BoundedSemaphore
from queue import Queue
import modbus_tk.defines as mb_cst
import modbus_tk.modbus_rtu as mb_rtu


class MainWindow(tk.Tk):
    def __init__(self):
        # инициализация главного окна
        super().__init__()
        self.title("MHDev ModBus")
        self.minsize(width=600, height=600)
        self.resizable(True, False)
        # инициализация переменных для создания и сдвига "регистровых окошек"
        self.obj_count = 0
        self.shift = -180
        self.scroll_shift = -587
        # инициализация переменных для подключения modbus
        self.number = None
        self.ser = serial.Serial(parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=1)
        # инициализация переменных для очереди
        self.q = Queue()
        self.r_lock = RLock()
        self.b_semaphore = BoundedSemaphore(value=1)
        self.in_queue = 0
        self.programm_stopped = False
        # инициализация переменных для скролла
        self.scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self, width=600, height=600, highlightthickness=0, xscrollcommand=self.scroll.set)
        self.scroll.config(command=self.canvas.xview)
        self.frame = tk.Frame(self.canvas, width=600, height=600)
        self.canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.bind("<Configure>", self.resize)
        self.update_idletasks()
        # self.minsize(self.frame.winfo_width(), self.frame.winfo_height())
        # инициализация переменных для фона

        self.img = ImageTk.PhotoImage(Image.open("bg600copy.jpg"))
        self.imglabel = tk.Label(self.frame, image=self.img)
        self.imglabel.place(x=0, y=0, anchor=tk.NW)
        # создание начальных элементов
        self.my_font = Font(family="Bernard MT Condensed", size="16")
        self.label_comport = ttk.Label(self.frame, text="COM port:")
        self.label_comport.configure(font=self.my_font, background="light blue")
        self.label_comport.place(x=15, y=17)
        self.entry_comport = tk.Entry(self.frame, width=3, font="Tahoma 16")
        self.entry_comport.place(x=100, y=17)
        self.baud_label = ttk.Label(self.frame, text="Baudrate:")
        self.baud_label.configure(font=self.my_font, background="light blue")
        self.baud_label.place(x=155, y=17)
        self.baud_var = tk.StringVar(self)
        self.baud_option = ["   1200", "   2400", "   4800", "   9600", "  14400", "  19200", "  38400", "  57600",
                            " 115200"]
        self.my_style = ttk.Style(self.frame)
        self.baud_menu = ttk.OptionMenu(self.frame, self.baud_var, self.baud_option[3], *self.baud_option,
                                        style="raised.TMenubutton")
        self.my_style.theme_use("clam")
        self.my_style.configure("raised.TMenubutton", background="white", font="Tahoma 13", width=7, borderwidth=-1)
        self.baud_menu["menu"].configure(background="white", font="Tahoma 13", activeborderwidth=-2)
        self.baud_menu.place(x=244, y=17)
        self.connect_but = ttk.Button(self.frame, text="Connect", command=self.connect_modbus)
        self.my_style.configure("TButton", background="light green", font=self.my_font, width=9, height=5,
                                borderwidth=-1)
        self.connect_but.place(x=360, y=14)
        self.status_label = ttk.Label(self.frame, text="Status:")
        self.status_label.configure(font=self.my_font, background="light blue")
        self.status_label.place(x=481, y=17)
        self.status_window = tk.Label(self.frame, bg="red", width=4, height=2)
        self.status_window.place(x=551, y=14)
        # инициализация переменных для элементов после открытия порта
        self.device_address_label = ttk.Label(self.frame, text="Device address:")
        self.device_address_label.configure(font=self.my_font, background="light blue")
        self.num_dev = tk.StringVar(self)
        self.entry_device_address = tk.Entry(self.frame, textvariable=self.num_dev, width=4, font="Tahoma 16")
        self.register_address_label = tk.Label(self.frame, text="Register address:")
        self.register_address_label.configure(font=self.my_font, background="light blue")
        self.num_reg = tk.StringVar(self)
        self.entry_register_address = tk.Entry(self.frame, textvariable=self.num_reg, width=6, font="Tahoma 16")
        self.memory_var = tk.StringVar(self)
        self.memory_option = ["Input Registers", "Holding Registers"]
        self.memory_menu = ttk.OptionMenu(self.frame, self.memory_var, self.memory_option[0], *self.memory_option,
                                          style="TMenubutton")
        self.my_style.configure("TMenubutton", background="white", font="Tahoma 12", width=14, borderwidth=-1)
        # self.memory_var.set(self.memory_option[1])
        self.memory_menu["menu"].configure(background="white", font="Tahoma 11", activeborderwidth=0)
        self.add_register_but = ttk.Button(self.frame, text="ADD", command=self.add_register)
        self.flag_register_created = tk.BooleanVar(self)
        self.flag_register_created.set(False)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.programm_stopped = True
            stop_prog = Thread(target=self.check_q, daemon=True)
            stop_prog.start()

    def check_q(self):
        if self.in_queue == 0:
            if self.ser.is_open:
                self.ser.close()
                if not self.ser.is_open:
                    print("Port closed")
                print("Program stopped")
                self.destroy()
            else:
                print("Program stopped")
                self.destroy()
        else:
            print("queue not empty")
            self.after(1000, self.check_q)

    # метод меняет размер скролла
    def resize(self, _event):
        if not self.programm_stopped:
            region = self.canvas.bbox(tk.ALL)
            self.canvas.configure(scrollregion=region)

    # метод подключает протокол модбас
    def connect_modbus(self):
        try:
            # если порт не открыт, то подключаемся
            if not self.ser.is_open:
                self.ser.baudrate = int(self.get_baudrate())
                self.number = self.get_comport()
                self.ser.port = "COM{}".format(self.number)
                self.ser.open()
                self.check_connect()
                print("Port " + self.ser.port + " is open on " + str(self.ser.baudrate) + " baudrate")
            # если порт открыт и номер порта и скорость соединения равны с прошлым подключением
            elif self.ser.is_open and self.get_comport() == self.number \
                    and int(self.get_baudrate()) == self.ser.baudrate:
                print("Port " + self.ser.port + " is already OPEN on " + str(self.ser.baudrate) + " baudrate")
            # если порт открыт, но изменились данные для подключения
            else:
                self.ser.close()
                self.ser.baudrate = int(self.get_baudrate())
                self.number = self.get_comport()
                self.ser.port = "COM{}".format(self.number)
                self.ser.open()
                self.check_connect()
                print("Port " + self.ser.port + " is open on other baudrate " + str(self.ser.baudrate))
        except Exception as e:
            self.check_connect()
            print(e)

    # метод проверки соединения
    def check_connect(self):
        if self.ser.is_open:
            self.status_window.configure(bg="green")
            self.create_register()
        else:
            self.status_window.configure(bg="red")
            self.destroy_register()

    # при успешном подключении модбаса, создаем элементы для создания регистровых окошек
    def create_register(self):
        self.device_address_label.place(x=15, y=60)
        self.entry_device_address.place(x=146, y=60)
        self.register_address_label.place(x=214, y=59)
        self.entry_register_address.place(x=360, y=60)
        self.memory_menu.place(x=445, y=60)
        self.add_register_but.place(x=250, y=100)
        self.flag_register_created.set(True)
        print("create_register successfully")

    # при неудачном подключении модбаса, уничтожаем элементы для создания регистровых окошек
    def destroy_register(self):
        if self.flag_register_created.get():
            destroy_widget = [self.device_address_label, self.entry_device_address, self.register_address_label,
                              self.entry_register_address, self.memory_menu, self.add_register_but]
            for widget in destroy_widget:
                widget.destroy()
            self.device_address_label = tk.Label(self, text="Device address:", fg="black", font="Tahoma")
            self.entry_device_address = tk.Entry(self, textvariable=self.num_dev, width=4, font="Tahoma")
            self.register_address_label = tk.Label(self, text="Register address:", fg="black", font="Tahoma")
            self.entry_register_address = tk.Entry(self, textvariable=self.num_reg, width=6, font="Tahoma")
            self.memory_menu = tk.OptionMenu(self, self.memory_var, *self.memory_option)
            self.add_register_but = tk.Button(self, text="ADD", font="Tahoma", command=self.add_register)
            self.flag_register_created.set(False)
            print("destroy_register successfully")
        else:
            print("create_register is not")

    # метод возвращает скорость соединения
    def get_baudrate(self):
        return self.baud_var.get()

    # метод возвращает номер порта
    def get_comport(self):
        return self.entry_comport.get()

    # метод возвращает номер устройства в сети модбас
    def get_number_device(self):
        return self.num_dev.get()

    # метод возвращает номер регистра
    def get_register_number(self):
        return self.num_reg.get()

    # метод возвращает тип памяти
    def get_memory_type(self):
        return self.memory_var.get()

    # метод создает новый обьект класса Register
    def add_register(self):
        try:
            self.obj_count += 1
            self.shift += 180
            self.scroll_shift += 180
            obj_name = "obj{}".format(self.obj_count)
            globals()[obj_name] = Register(obj_name, self.get_number_device(), self.get_register_number(),
                                           self.get_memory_type(), self, self.scroll_shift, self.frame,
                                           self.obj_count, self.shift)
            globals()[obj_name].setDaemon(True)
            globals()[obj_name].start()
        except Exception as e:
            print(e)


class Register(Thread):
    def __init__(self, name, device, register, memory, rut, scroll_shift, frame, obj_count, shift):
        Thread.__init__(self)
        # инициализируем переданные аргументы
        self.var_name = name
        self.device = device
        self.register = register
        self.memory = memory
        self.root = rut
        self.scroll_shift = scroll_shift
        self.frame = frame
        self.obj_count = obj_count
        self.shift = shift
        self.old_mask = 0
        self.state = "disable"
        self.label_frame = tk.LabelFrame(self.frame, height=442, width=170)
        self.master = mb_rtu.RtuMaster(root.ser)
        # инициализируем переменные битовой маски
        self._0bit_var = tk.BooleanVar(self.label_frame)
        self._1bit_var = tk.BooleanVar(self.label_frame)
        self._2bit_var = tk.BooleanVar(self.label_frame)
        self._3bit_var = tk.BooleanVar(self.label_frame)
        self._4bit_var = tk.BooleanVar(self.label_frame)
        self._5bit_var = tk.BooleanVar(self.label_frame)
        self._6bit_var = tk.BooleanVar(self.label_frame)
        self._7bit_var = tk.BooleanVar(self.label_frame)
        self._8bit_var = tk.BooleanVar(self.label_frame)
        self._9bit_var = tk.BooleanVar(self.label_frame)
        self._10bit_var = tk.BooleanVar(self.label_frame)
        self._11bit_var = tk.BooleanVar(self.label_frame)
        self._12bit_var = tk.BooleanVar(self.label_frame)
        self._13bit_var = tk.BooleanVar(self.label_frame)
        self._14bit_var = tk.BooleanVar(self.label_frame)
        self._15bit_var = tk.BooleanVar(self.label_frame)
        self.write_mask = tk.IntVar(self.label_frame)
        self.read_flag = False
        self.device_label = tk.Label(self.label_frame, font="Tahoma", text="Device: " + self.device)
        self.register_label = tk.Label(self.label_frame, font="Tahoma", text="Register: " + self.register)
        self.memory_label = tk.Label(self.label_frame, font="Tahoma", text=self.memory)
        self.pixel_virtual = tk.PhotoImage(width=1, height=1)
        self.read_but = tk.Button(self.label_frame, image=self.pixel_virtual, compound=tk.CENTER, width=75, height=30,
                                  text="READ", font="Tahoma", command=self.start_read_register)
        self.radio_read = tk.BooleanVar(self.label_frame)
        self.read_radio_but = tk.Radiobutton(self.label_frame, text="1", variable=self.radio_read, value=0,
                                             font="-weight bold")
        self.reading_radio_but = tk.Radiobutton(self.label_frame, text=chr(8734), variable=self.radio_read, value=1,
                                                font="-weight bold", command=self.start_read_register)
        self.mask_label = tk.Button(self.label_frame, image=self.pixel_virtual,
                                    compound=tk.CENTER, width=74, height=16, font="Tahoma", command=self.write_mask_but)
        self.mask_value_text = tk.StringVar(self.label_frame)
        self.mask_value = tk.Entry(self.label_frame, textvariable=self.mask_value_text,
                                   width=8, font="Tahoma")
        self.write_but = tk.Button(self.label_frame, image=self.pixel_virtual, compound=tk.CENTER, width=74,
                                   height=30, text="WRITE", font="Tahoma", command=self.start_write_register)
        self.radio_write = tk.BooleanVar(self.label_frame)
        self.write_radio_but = tk.Radiobutton(self.label_frame, text="1", variable=self.radio_write, value=0,
                                              font="-weight bold")
        self.writing_radio_but = tk.Radiobutton(self.label_frame, text=chr(8734), variable=self.radio_write,
                                                value=1, font="-weight bold", command=self.start_write_register)
        self.check_0_bit = tk.Checkbutton(self.label_frame, variable=self._0bit_var, state=self.state,
                                          text="- 0 bit", font="Tahoma")
        self.check_1_bit = tk.Checkbutton(self.label_frame, variable=self._1bit_var, state=self.state,
                                          text="- 1 bit", font="Tahoma")
        self.check_2_bit = tk.Checkbutton(self.label_frame, variable=self._2bit_var, state=self.state,
                                          text="- 2 bit", font="Tahoma")
        self.check_3_bit = tk.Checkbutton(self.label_frame, variable=self._3bit_var, state=self.state,
                                          text="- 3 bit", font="Tahoma")
        self.check_4_bit = tk.Checkbutton(self.label_frame, variable=self._4bit_var, state=self.state,
                                          text="- 4 bit", font="Tahoma")
        self.check_5_bit = tk.Checkbutton(self.label_frame, variable=self._5bit_var, state=self.state,
                                          text="- 5 bit", font="Tahoma")
        self.check_6_bit = tk.Checkbutton(self.label_frame, variable=self._6bit_var, state=self.state,
                                          text="- 6 bit", font="Tahoma")
        self.check_7_bit = tk.Checkbutton(self.label_frame, variable=self._7bit_var, state=self.state,
                                          text="- 7 bit", font="Tahoma")
        self.check_8_bit = tk.Checkbutton(self.label_frame, variable=self._8bit_var, state=self.state,
                                          text="- 8 bit", font="Tahoma")
        self.check_9_bit = tk.Checkbutton(self.label_frame, variable=self._9bit_var, state=self.state,
                                          text="- 9 bit", font="Tahoma")
        self.check_10_bit = tk.Checkbutton(self.label_frame, variable=self._10bit_var, state=self.state,
                                           text="- 10 bit", font="Tahoma")
        self.check_11_bit = tk.Checkbutton(self.label_frame, variable=self._11bit_var, state=self.state,
                                           text="- 11 bit", font="Tahoma")
        self.check_12_bit = tk.Checkbutton(self.label_frame, variable=self._12bit_var, state=self.state,
                                           text="- 12 bit", font="Tahoma")
        self.check_13_bit = tk.Checkbutton(self.label_frame, variable=self._13bit_var, state=self.state,
                                           text="- 13 bit", font="Tahoma")
        self.check_14_bit = tk.Checkbutton(self.label_frame, variable=self._14bit_var, state=self.state,
                                           text="- 14 bit", font="Tahoma")
        self.check_15_bit = tk.Checkbutton(self.label_frame, variable=self._15bit_var, state=self.state,
                                           text="- 15 bit", font="Tahoma")
        self.is_checkbox_created = False
        self.m_defines = mb_cst

    def run(self):
        if self.scroll_shift < 0:
            self.scroll_shift = 0
        self.master.set_timeout(0.3)
        self.frame.configure(width=600 + self.scroll_shift)
        # создаем пространство обьекта Register
        self.label_frame.place(x=12+self.shift, y=150)
        self.label_frame.grid_propagate(False)
        # self.read_flag.set(False)
        # создаем элементы регистрового окошка
        self.device_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.register_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.memory_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.read_but.grid(row=3, column=0, sticky=tk.W)
        self.radio_read.set(0)
        self.read_radio_but.grid(row=4, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.reading_radio_but.grid(row=5, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.disable_state()
        if self.memory == "Holding Registers":
            self.active_state()
            self.write_but.grid(row=3, column=1, sticky=tk.E)
            self.radio_write.set(0)
            self.write_radio_but.grid(row=4, column=1, sticky=tk.N + tk.S + tk.W + tk.E)
            self.writing_radio_but.grid(row=5, column=1, sticky=tk.N + tk.S + tk.W + tk.E)
        print("Обьект класса Register с именем " + self.var_name + " успешно создан")

    def active_state(self):
        self.mask_value.configure(state="normal")
        self.mask_label.configure(state="normal")

    def disable_state(self):
        self.mask_value.configure(state="disable")
        self.mask_label.configure(state="disable")

    def checkbox_state(self):
        if (self.memory == "Input Registers") or \
                (self.memory == "Holding Registers" and self.radio_read.get() == 1):
            self.state = "disable"
        else:
            self.state = "normal"

    def start_read_register(self):
        if not root.programm_stopped:
            if not self.read_flag:
                self.mask_label.configure(text="Mask int: ")
                self.mask_label.grid(row=14, column=0, sticky=tk.W)
                self.mask_value.grid(row=14, column=1, sticky=tk.W)
            # self.read_flag.set(True)
            if self.radio_read.get() == 0:
                self.active_state()
                root.q.put(Thread(target=self.read_register, daemon=True))
                root.in_queue += 1
                # print(root.in_queue)
                root.q.get().start()
            else:
                self.disable_state()
                root.q.put(Thread(target=self.read_register, daemon=True))
                root.in_queue += 1
                # print(root.in_queue)
                root.q.get().start()
                self.label_frame.after(850, self.start_read_register)

    def checkbox_created(self):
        self.check_0_bit.grid(row=6, column=0, sticky=tk.W)
        self.check_1_bit.grid(row=7, column=0, sticky=tk.W)
        self.check_2_bit.grid(row=8, column=0, sticky=tk.W)
        self.check_3_bit.grid(row=9, column=0, sticky=tk.W)
        self.check_4_bit.grid(row=10, column=0, sticky=tk.W)
        self.check_5_bit.grid(row=11, column=0, sticky=tk.W)
        self.check_6_bit.grid(row=12, column=0, sticky=tk.W)
        self.check_7_bit.grid(row=13, column=0, sticky=tk.W)
        self.check_8_bit.grid(row=6, column=1, sticky=tk.W)
        self.check_9_bit.grid(row=7, column=1, sticky=tk.W)
        self.check_10_bit.grid(row=8, column=1, sticky=tk.W)
        self.check_11_bit.grid(row=9, column=1, sticky=tk.W)
        self.check_12_bit.grid(row=10, column=1, sticky=tk.W)
        self.check_13_bit.grid(row=11, column=1, sticky=tk.W)
        self.check_14_bit.grid(row=12, column=1, sticky=tk.W)
        self.check_15_bit.grid(row=13, column=1, sticky=tk.W)

    def read_register(self):
        with root.b_semaphore:
            try:
                root.r_lock.acquire()
                self.reading_register()
            except Exception as e:
                print("Error: " + str(e))
            finally:
                if not self.read_flag:
                    self.read_flag = True
                root.in_queue -= 1
                root.r_lock.release()

    def start_write_register(self):
        if not root.programm_stopped:
            if self.radio_write.get() == 0:
                self.active_state()
                root.q.put(Thread(target=self.write_register, daemon=True))
                root.in_queue += 1
                root.q.get().start()
            else:
                self.disable_state()
                root.q.put(Thread(target=self.write_register, daemon=True))
                root.in_queue += 1
                root.q.get().start()
                self.label_frame.after(850, self.start_write_register)

    def reading_register(self):
        if self.memory == "Input Registers":
            self.disable_state()
            get_data = self.master.execute(int(self.device), self.m_defines.READ_INPUT_REGISTERS,
                                           int(self.register), 1)
        else:
            get_data = self.master.execute(int(self.device), self.m_defines.READ_HOLDING_REGISTERS,
                                           int(self.register), 1)
        self.checkbox_state()
        mask = bin(get_data[0])
        mask_arr = []
        str_mask = str(mask[2:])
        for i in range(len(str_mask)):
            mask_arr.append(int(str_mask[i]))
        while len(mask_arr) < 16:
            mask_arr.insert(0, 0)
        if not self.is_checkbox_created:
            self.checkbox_created()
            self.is_checkbox_created = True
        if mask_arr[15] == 0:
            self.check_0_bit.configure(state=self.state)
            self.check_0_bit.deselect()
        else:
            self.check_0_bit.configure(state=self.state)
            self.check_0_bit.select()
        if mask_arr[14] == 0:
            self.check_1_bit.configure(state=self.state)
            self.check_1_bit.deselect()
        else:
            self.check_1_bit.configure(state=self.state)
            self.check_1_bit.select()
        if mask_arr[13] == 0:
            self.check_2_bit.configure(state=self.state)
            self.check_2_bit.deselect()
        else:
            self.check_2_bit.configure(state=self.state)
            self.check_2_bit.select()
        if mask_arr[12] == 0:
            self.check_3_bit.configure(state=self.state)
            self.check_3_bit.deselect()
        else:
            self.check_3_bit.configure(state=self.state)
            self.check_3_bit.select()
        if mask_arr[11] == 0:
            self.check_4_bit.configure(state=self.state)
            self.check_4_bit.deselect()
        else:
            self.check_4_bit.configure(state=self.state)
            self.check_4_bit.select()
        if mask_arr[10] == 0:
            self.check_5_bit.configure(state=self.state)
            self.check_5_bit.deselect()
        else:
            self.check_5_bit.configure(state=self.state)
            self.check_5_bit.select()
        if mask_arr[9] == 0:
            self.check_6_bit.configure(state=self.state)
            self.check_6_bit.deselect()
        else:
            self.check_6_bit.configure(state=self.state)
            self.check_6_bit.select()
        if mask_arr[8] == 0:
            self.check_7_bit.configure(state=self.state)
            self.check_7_bit.deselect()
        else:
            self.check_7_bit.configure(state=self.state)
            self.check_7_bit.select()
        if mask_arr[7] == 0:
            self.check_8_bit.configure(state=self.state)
            self.check_8_bit.deselect()
        else:
            self.check_8_bit.configure(state=self.state)
            self.check_8_bit.select()
        if mask_arr[6] == 0:
            self.check_9_bit.configure(state=self.state)
            self.check_9_bit.deselect()
        else:
            self.check_9_bit.configure(state=self.state)
            self.check_9_bit.select()
        if mask_arr[5] == 0:
            self.check_10_bit.configure(state=self.state)
            self.check_10_bit.deselect()
        else:
            self.check_10_bit.configure(state=self.state)
            self.check_10_bit.select()
        if mask_arr[4] == 0:
            self.check_11_bit.configure(state=self.state)
            self.check_11_bit.deselect()
        else:
            self.check_11_bit.configure(state=self.state)
            self.check_11_bit.select()
        if mask_arr[3] == 0:
            self.check_12_bit.configure(state=self.state)
            self.check_12_bit.deselect()
        else:
            self.check_12_bit.configure(state=self.state)
            self.check_12_bit.select()
        if mask_arr[2] == 0:
            self.check_13_bit.configure(state=self.state)
            self.check_13_bit.deselect()
        else:
            self.check_13_bit.configure(state=self.state)
            self.check_13_bit.select()
        if mask_arr[1] == 0:
            self.check_14_bit.configure(state=self.state)
            self.check_14_bit.deselect()
        else:
            self.check_14_bit.configure(state=self.state)
            self.check_14_bit.select()
        if mask_arr[0] == 0:
            self.check_15_bit.configure(state=self.state)
            self.check_15_bit.deselect()
        else:
            self.check_15_bit.configure(state=self.state)
            self.check_15_bit.select()
        self.mask_value_text.set(get_data[0])

    def write_register(self):
        with root.b_semaphore:
            try:
                root.r_lock.acquire()
                if not self.read_flag:
                    self.mask_label.configure(text="Mask int: ")
                    self.mask_label.grid(row=14, column=0, sticky=tk.W)
                    self.mask_value.grid(row=14, column=1, sticky=tk.W)
                    self.reading_register()
                    self.read_flag = True
                write_mask = 0
                if self._0bit_var.get() == 1:
                    write_mask += 1
                if self._1bit_var.get() == 1:
                    write_mask += 2
                if self._2bit_var.get() == 1:
                    write_mask += 4
                if self._3bit_var.get() == 1:
                    write_mask += 8
                if self._4bit_var.get() == 1:
                    write_mask += 16
                if self._5bit_var.get() == 1:
                    write_mask += 32
                if self._6bit_var.get() == 1:
                    write_mask += 64
                if self._7bit_var.get() == 1:
                    write_mask += 128
                if self._8bit_var.get() == 1:
                    write_mask += 256
                if self._9bit_var.get() == 1:
                    write_mask += 512
                if self._10bit_var.get() == 1:
                    write_mask += 1024
                if self._11bit_var.get() == 1:
                    write_mask += 2048
                if self._12bit_var.get() == 1:
                    write_mask += 4096
                if self._13bit_var.get() == 1:
                    write_mask += 8192
                if self._14bit_var.get() == 1:
                    write_mask += 16384
                if self._15bit_var.get() == 1:
                    write_mask += 32768
                self.master.execute(int(self.device), self.m_defines.WRITE_SINGLE_REGISTER, int(self.register),
                                    output_value=write_mask)
                self.mask_value_text.set(str(write_mask))
            except Exception as e:
                print("Error: " + str(e))
            finally:
                root.in_queue -= 1
                root.r_lock.release()

    def write_mask_but(self):
        root.q.put(Thread(target=self.q_write_mask_but, daemon=True))
        root.in_queue += 1
        root.q.get().start()

    def q_write_mask_but(self):
        with root.b_semaphore:
            try:
                root.r_lock.acquire()
                write_mask = int(self.mask_value_text.get())
                self.master.execute(int(self.device), self.m_defines.WRITE_SINGLE_REGISTER, int(self.register),
                                    output_value=write_mask)
                mask_arr = []
                str_mask = str(bin(write_mask)[2:])
                for i in range(len(str_mask)):
                    mask_arr.append(int(str_mask[i]))
                while len(mask_arr) < 16:
                    mask_arr.insert(0, 0)
                if mask_arr[15] == 0:
                    self.check_0_bit.deselect()
                else:
                    self.check_0_bit.select()
                if mask_arr[14] == 0:
                    self.check_1_bit.deselect()
                else:
                    self.check_1_bit.select()
                if mask_arr[13] == 0:
                    self.check_2_bit.deselect()
                else:
                    self.check_2_bit.select()
                if mask_arr[12] == 0:
                    self.check_3_bit.deselect()
                else:
                    self.check_3_bit.select()
                if mask_arr[11] == 0:
                    self.check_4_bit.deselect()
                else:
                    self.check_4_bit.select()
                if mask_arr[10] == 0:
                    self.check_5_bit.deselect()
                else:
                    self.check_5_bit.select()
                if mask_arr[9] == 0:
                    self.check_6_bit.deselect()
                else:
                    self.check_6_bit.select()
                if mask_arr[8] == 0:
                    self.check_7_bit.deselect()
                else:
                    self.check_7_bit.select()
                if mask_arr[7] == 0:
                    self.check_8_bit.deselect()
                else:
                    self.check_8_bit.select()
                if mask_arr[6] == 0:
                    self.check_9_bit.deselect()
                else:
                    self.check_9_bit.select()
                if mask_arr[5] == 0:
                    self.check_10_bit.deselect()
                else:
                    self.check_10_bit.select()
                if mask_arr[4] == 0:
                    self.check_11_bit.deselect()
                else:
                    self.check_11_bit.select()
                if mask_arr[3] == 0:
                    self.check_12_bit.deselect()
                else:
                    self.check_12_bit.select()
                if mask_arr[2] == 0:
                    self.check_13_bit.deselect()
                else:
                    self.check_13_bit.select()
                if mask_arr[1] == 0:
                    self.check_14_bit.deselect()
                else:
                    self.check_14_bit.select()
                if mask_arr[0] == 0:
                    self.check_15_bit.deselect()
                else:
                    self.check_15_bit.select()
            except Exception as e:
                print("Error: " + str(e))
            finally:
                root.in_queue -= 1
                root.r_lock.release()


if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()
