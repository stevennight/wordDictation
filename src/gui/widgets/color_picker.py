import customtkinter

class ColorPickerDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, command=None):
        super().__init__(parent)
        self.command = command

        self.title("选择颜色")
        self.geometry("300x400")
        self.attributes("-topmost", True)

        self.grid_columnconfigure(0, weight=1)

        self.color_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.color_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#000000", "#FFFFFF", "#808080", "#C0C0C0", "#800000", "#008000"
        ]

        for i, color in enumerate(self.colors):
            row = i // 4
            col = i % 4
            color_button = customtkinter.CTkButton(
                self.color_frame, text="", fg_color=color, hover_color=color,
                width=50, height=50, command=lambda c=color: self.select_color(c)
            )
            color_button.grid(row=row, column=col, padx=5, pady=5)

        self.custom_color_button = customtkinter.CTkButton(self, text="自定义颜色", command=self.open_custom_color_dialog)
        self.custom_color_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def select_color(self, color):
        if self.command:
            self.command(color)
        self.destroy()

    def open_custom_color_dialog(self):
        from tkinter import colorchooser
        color_code = colorchooser.askcolor(title="选择一个颜色")
        if color_code and color_code[1]:
            self.select_color(color_code[1])