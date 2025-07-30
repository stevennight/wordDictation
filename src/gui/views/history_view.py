import customtkinter
import os
import json

class HistoryView(customtkinter.CTkFrame):
    def __init__(self, master, callbacks):
        super().__init__(master, fg_color="transparent")
        self.callbacks = callbacks
        self.back_to_main_callback = self.callbacks['show_initial_view']
        self.history_files = []

        self._create_widgets()
        self.load_history()

    def _create_widgets(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = customtkinter.CTkLabel(self, text="历史记录", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=10, sticky="n")

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="默写记录")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        for widget in [self.scrollable_frame, self.scrollable_frame._parent_canvas]:
            widget.bind("<ButtonPress-1>", self._on_button_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_button_release)

        self.back_button = customtkinter.CTkButton(self, text="返回", command=self.back_to_main_callback, height=40, font=("Arial", 16))
        self.back_button.grid(row=2, column=0, pady=20, sticky="s")

    def load_history(self):
        history_dir = "history"
        if not os.path.exists(history_dir):
            return

        self.history_files = sorted([f for f in os.listdir(history_dir) if f.endswith('.json')], reverse=True)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for file_name in self.history_files:
            self.add_history_entry(file_name)

    def add_history_entry(self, file_name):
        entry_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color=("gray85", "gray15"))
        entry_frame.pack(fill="x", padx=10, pady=5)

        base_name = os.path.splitext(file_name)[0]
        label = customtkinter.CTkLabel(entry_frame, text=base_name, anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        view_command = lambda f=file_name: self.callbacks['view_history_detail'](f)
        entry_frame.bind("<Double-Button-1>", lambda e, f=file_name: self.callbacks['view_history_detail'](f))
        label.bind("<Double-Button-1>", lambda e, f=file_name: self.callbacks['view_history_detail'](f))

        for widget in [entry_frame, label]:
            widget.bind("<ButtonPress-1>", self._on_button_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_button_release)

        view_button = customtkinter.CTkButton(entry_frame, text="查看", width=60, command=lambda f=file_name: self.callbacks['view_history_detail'](f))
        view_button.pack(side="right", padx=5)

        delete_button = customtkinter.CTkButton(entry_frame, text="删除", width=60, fg_color="#C00000", hover_color="#A00000", command=lambda f=file_name: self.delete_history(f))
        delete_button.pack(side="right", padx=5)



    def _on_button_press(self, event):
        self.last_y = event.y
        self.dragging = True

    def _on_motion(self, event):
        if hasattr(self, 'dragging') and self.dragging:
            delta_y = event.y - self.last_y
            self.scrollable_frame._parent_canvas.yview_scroll(-1 * int(delta_y), "units")
            self.last_y = event.y

    def _on_button_release(self, event):
        self.dragging = False

    def delete_history(self, file_name):
        print(f"Deleting {file_name}")
        history_dir = "history"
        base_name = os.path.splitext(file_name)[0]
        json_path = os.path.join(history_dir, file_name)
        dir_path = os.path.join(history_dir, base_name)

        try:
            if os.path.exists(json_path):
                os.remove(json_path)
            if os.path.exists(dir_path):
                import shutil
                shutil.rmtree(dir_path)
            self.load_history() # Refresh the list
        except Exception as e:
            print(f"Error deleting history: {e}")