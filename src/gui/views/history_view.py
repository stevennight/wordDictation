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
        self.title_label = customtkinter.CTkLabel(self, text="历史记录", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=10)

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="默写记录")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.back_button = customtkinter.CTkButton(self, text="返回", command=self.back_to_main_callback)
        self.back_button.pack(pady=10)

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

        view_button = customtkinter.CTkButton(entry_frame, text="查看", width=60, command=lambda f=file_name: self.callbacks['view_history_detail'](f))
        view_button.pack(side="right", padx=5)

        delete_button = customtkinter.CTkButton(entry_frame, text="删除", width=60, fg_color="#C00000", hover_color="#A00000", command=lambda f=file_name: self.delete_history(f))
        delete_button.pack(side="right", padx=5)



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