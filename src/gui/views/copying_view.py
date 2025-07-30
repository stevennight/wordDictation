import customtkinter
from ..widgets.canvas import HandwritingCanvas
from ...utils import config_manager

class CopyingView(customtkinter.CTkFrame):
    def __init__(self, parent, callbacks, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.callbacks = callbacks
        self.word_data = kwargs.get('word_data')
        self.config = config_manager.load_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.prompt_label = customtkinter.CTkLabel(self, text=f"抄写: {self.word_data.get('prompt', '')}  正确答案: {self.word_data.get('answer', '')}", font=("Arial", 24))
        self.prompt_label.grid(row=0, column=0, pady=20)

        self.canvas = HandwritingCanvas(self)
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.set_pen_size(self.config.get('pen_size', 5))
        self.set_pen_color(self.config.get('pen_color', 'black'))

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

        self.pen_color_button = customtkinter.CTkButton(self.tool_frame, text="颜色", command=self.open_color_picker)
        self.pen_color_button.pack(side="left", padx=10, pady=5)

        self.pen_size_slider = customtkinter.CTkSlider(self.tool_frame, from_=1, to=10, command=self.set_pen_size)
        self.pen_size_slider.set(self.config.get('pen_size', 5))
        self.pen_size_slider.pack(side="left", padx=10, pady=5, fill="x", expand=True)







    def set_pen_size(self, size):
        pen_size = int(size)
        self.canvas.set_pen_size(pen_size)
        self.config['pen_size'] = pen_size
        config_manager.save_config(self.config)

    def open_color_picker(self):
        from ..widgets.color_picker import ColorPickerDialog
        dialog = ColorPickerDialog(self, command=self.set_pen_color)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

    def set_pen_color(self, color):
        self.canvas.set_pen_color(color)
        self.config['pen_color'] = color
        config_manager.save_config(self.config)

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