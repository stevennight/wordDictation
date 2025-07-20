import customtkinter
from tkinterdnd2 import DND_FILES

class InitialView(customtkinter.CTkFrame):
    def __init__(self, parent, app_callbacks):
        super().__init__(parent, fg_color="transparent")
        self.app_callbacks = app_callbacks

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Center the content

        container = customtkinter.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="ew", padx=20)
        container.grid_columnconfigure(0, weight=1)

        self.load_button = customtkinter.CTkButton(container, text="加载单词文件", command=self.app_callbacks['load_words_from_dialog'], height=50, font=("Arial", 18))
        self.load_button.grid(row=0, column=0, pady=10, sticky="ew")

        self.status_label = customtkinter.CTkLabel(container, text="请先加载一个单词文件 (.docx) 或将文件拖入窗口", font=("Arial", 14))
        self.status_label.grid(row=1, column=0, pady=10, sticky="ew")

        # DND setup
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        filepaths = self.tk.splitlist(event.data)
        if filepaths:
            self.app_callbacks['load_words'](filepaths[0])

    def update_status(self, text):
        self.status_label.configure(text=text)

    def show_order_selection(self):
        self.load_button.grid_forget()
        self.status_label.grid_forget()

        self.order_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.order_frame.grid(row=1, column=0, pady=20)

        order_label = customtkinter.CTkLabel(self.order_frame, text="请选择默写顺序：")
        order_label.pack(pady=10)

        sequential_button = customtkinter.CTkButton(self.order_frame, text="顺序开始", command=lambda: self.app_callbacks['start_with_order'](False))
        sequential_button.pack(side="left", padx=20, pady=10)

        shuffled_button = customtkinter.CTkButton(self.order_frame, text="乱序开始", command=lambda: self.app_callbacks['start_with_order'](True))
        shuffled_button.pack(side="right", padx=20, pady=10)

    def show_quantity_selection(self):
        if hasattr(self, 'order_frame'):
            self.order_frame.destroy()

        self.quantity_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.quantity_frame.grid(row=1, column=0, pady=20)

        quantity_label = customtkinter.CTkLabel(self.quantity_frame, text="请选择默写数量：")
        quantity_label.pack(pady=10)

        button_frame = customtkinter.CTkFrame(self.quantity_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        quantities = ["5", "10", "20", "全部", "自定义"]
        for q in quantities:
            if q == "全部":
                cmd = lambda: self.app_callbacks['set_quantity_and_start'](-1) # Use -1 for all
            elif q == "自定义":
                cmd = self.app_callbacks['ask_custom_quantity']
            else:
                cmd = lambda num=q: self.app_callbacks['set_quantity_and_start'](int(num))
            customtkinter.CTkButton(button_frame, text=q, command=cmd).pack(side="left", padx=5)