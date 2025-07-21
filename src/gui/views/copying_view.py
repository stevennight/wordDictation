import customtkinter
from ..widgets.canvas import HandwritingCanvas

class CopyingView(customtkinter.CTkFrame):
    def __init__(self, parent, callbacks, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.callbacks = callbacks
        self.word_data = kwargs.get('word_data')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.prompt_label = customtkinter.CTkLabel(self, text=f"抄写: {self.word_data.get('prompt', '')}  正确答案: {self.word_data.get('answer', '')}", font=("Arial", 24))
        self.prompt_label.grid(row=0, column=0, pady=20)

        self.canvas = HandwritingCanvas(self)
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self._create_tool_frame()
        self._create_control_buttons()

    def _create_tool_frame(self):
        self.tool_frame = customtkinter.CTkFrame(self)
        self.tool_frame.grid(row=2, column=0, pady=10, sticky="ew")

        self.clear_button_tool = customtkinter.CTkButton(self.tool_frame, text="清空", command=self.canvas.clear_canvas)
        self.clear_button_tool.pack(side="left", padx=10, pady=5)

        self.paint_mode_button = customtkinter.CTkSegmentedButton(self.tool_frame, values=["画笔", "橡皮擦"], command=self.set_paint_mode)
        self.paint_mode_button.pack(side="left", padx=10, pady=5)
        self.paint_mode_button.set("画笔")

        self.pen_color_button = customtkinter.CTkOptionMenu(self.tool_frame, values=["black", "blue", "red"], command=self.canvas.set_pen_color)
        self.pen_color_button.pack(side="left", padx=10, pady=5)

        self.eraser_size_slider = customtkinter.CTkSlider(self.tool_frame, from_=5, to=50, command=self.canvas.set_eraser_size)
        self.eraser_size_slider.pack(side="left", padx=10, pady=5)
        self.eraser_size_slider.set(20)





    def set_paint_mode(self, mode):
        if mode == "画笔":
            self.canvas.paint_mode = "pen"
        else:
            self.canvas.paint_mode = "eraser"

    def _create_control_buttons(self):
        self.button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)

        button_font = ("Arial", 18)
        self.back_button = customtkinter.CTkButton(self.button_frame, text="返回", command=self.callbacks['back_to_detail'], height=50, font=button_font)
        self.back_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")