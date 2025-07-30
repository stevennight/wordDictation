import customtkinter
from ..utils.registry_handler import is_admin, run_as_admin

class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config = parent.config

        self.title("设置")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        # Theme settings
        theme_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        theme_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        theme_label = customtkinter.CTkLabel(theme_frame, text="主题:")
        theme_label.pack(side="left", padx=10)
        self.theme_menu = customtkinter.CTkOptionMenu(theme_frame, values=["System", "Dark", "Light"], command=self.change_theme)
        self.theme_menu.set(self.config.get("theme", "System"))
        self.theme_menu.pack(side="left", padx=10)

        # History settings
        history_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        history_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        history_label = customtkinter.CTkLabel(history_frame, text="保存历史记录数量:")
        history_label.pack(side="left", padx=10)
        self.history_entry = customtkinter.CTkEntry(history_frame)
        self.history_entry.insert(0, str(self.config.get("max_history_size", 50)))
        self.history_entry.pack(side="left", padx=10)

        # Accuracy threshold settings
        accuracy_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        accuracy_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        accuracy_label = customtkinter.CTkLabel(accuracy_frame, text="正确率阈值 (%):")
        accuracy_label.pack(side="left", padx=10)
        self.accuracy_entry = customtkinter.CTkEntry(accuracy_frame)
        self.accuracy_entry.insert(0, str(self.config.get("accuracy_threshold", 80)))
        self.accuracy_entry.pack(side="left", padx=10)

        # Registry settings
        self.registry_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.registry_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.update_registry_buttons()

        # Save button
        save_button = customtkinter.CTkButton(self, text="保存设置", command=self.save_settings)
        save_button.grid(row=4, column=0, padx=20, pady=20)

    def change_theme(self, theme):
        self.config["theme"] = theme

    def save_settings(self):
        try:
            history_count = int(self.history_entry.get())
            self.config["max_history_size"] = history_count

            accuracy_threshold = int(self.accuracy_entry.get())
            self.config["accuracy_threshold"] = accuracy_threshold

            self.parent.save_config()
            self.parent.apply_config()
            self.destroy()
        except ValueError:
            # Handle invalid input
            pass

    def update_registry_buttons(self):
        for widget in self.registry_frame.winfo_children():
            widget.destroy()

        if is_admin():
            register_button = customtkinter.CTkButton(self.registry_frame, text="注册右键菜单", command=self.do_register)
            register_button.pack(side="left", padx=10, pady=5)
            unregister_button = customtkinter.CTkButton(self.registry_frame, text="注销右键菜单", command=self.do_unregister)
            unregister_button.pack(side="left", padx=10, pady=5)
        else:
            admin_button = customtkinter.CTkButton(self.registry_frame, text="以管理员身份运行以注册菜单", command=self.run_app_as_admin)
            admin_button.pack(expand=True, pady=5)

    def do_register(self):
        self.parent.register_context_menu()
        self.update_registry_buttons()

    def do_unregister(self):
        self.parent.unregister_context_menu()
        self.update_registry_buttons()

    def run_app_as_admin(self):
        import sys
        run_as_admin(sys.executable + ' ' + ' '.join(sys.argv))