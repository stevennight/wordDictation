import customtkinter
from ..widgets.canvas import HandwritingCanvas
from ...utils import config_manager

class DictationView(customtkinter.CTkFrame):
    def __init__(self, parent, app_callbacks):
        super().__init__(parent, fg_color="transparent")
        self.app_callbacks = app_callbacks
        self.config = config_manager.load_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Prompt row
        self.grid_rowconfigure(1, weight=1)  # Canvas row
        self.grid_rowconfigure(2, weight=0)  # Tool frame row
        self.grid_rowconfigure(3, weight=0)  # Answer row
        self.grid_rowconfigure(4, weight=0)  # Button row

        self.prompt_label = customtkinter.CTkLabel(self, text="", font=("Arial", 24))
        self.prompt_label.grid(row=0, column=0, pady=20, sticky="ew")

        self.canvas = HandwritingCanvas(self)
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.set_pen_size(self.config.get('pen_size', 5))
        self.set_annotation_pen_size(self.config.get('pen_size', 5))

        self.answer_label = customtkinter.CTkLabel(self, text="", font=("Arial", 20), text_color="green")
        self.answer_label.grid(row=3, column=0, pady=10, sticky="ew")

        self._create_tool_frame()
        self._create_annotation_tool_frame()
        self._create_control_buttons()
        self._create_judgement_buttons()

    def _create_tool_frame(self):
        self.tool_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.tool_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.tool_frame.grid_columnconfigure(3, weight=1)

        button_frame = customtkinter.CTkFrame(self.tool_frame, fg_color="transparent")
        button_frame.pack(side="left", padx=10)

        self.pen_button = customtkinter.CTkButton(button_frame, text="画笔", command=self.set_pen_mode, width=60, corner_radius=0, border_spacing=0)
        self.pen_button.pack(side="left")

        self.eraser_button = customtkinter.CTkButton(button_frame, text="橡皮擦", command=self.set_eraser_mode, width=60, corner_radius=0, border_spacing=0)
        self.eraser_button.pack(side="left")

        self.clear_button_tool = customtkinter.CTkButton(self.tool_frame, text="清空", command=self.canvas.clear_canvas)
        self.clear_button_tool.pack(side="left", padx=10)

        self.pen_size_slider = customtkinter.CTkSlider(self.tool_frame, from_=1, to=10, command=self.set_pen_size)
        self.pen_size_slider.set(self.config.get('pen_size', 5))
        self.pen_size_slider.pack(side="left", padx=10, fill="x", expand=True)

    def _create_annotation_tool_frame(self):
        self.annotation_tool_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.annotation_tool_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.annotation_tool_frame.grid_columnconfigure(3, weight=1)

        button_frame = customtkinter.CTkFrame(self.annotation_tool_frame, fg_color="transparent")
        button_frame.pack(side="left", padx=10)

        self.annotation_pen_button = customtkinter.CTkButton(button_frame, text="画笔", command=self.set_pen_mode, width=60, corner_radius=0, border_spacing=0)
        self.annotation_pen_button.pack(side="left")

        self.annotation_eraser_button = customtkinter.CTkButton(button_frame, text="橡皮擦", command=self.set_eraser_mode, width=60, corner_radius=0, border_spacing=0)
        self.annotation_eraser_button.pack(side="left")

        self.clear_annotation_button = customtkinter.CTkButton(self.annotation_tool_frame, text="清除批注", command=self.canvas.clear_annotations)
        self.clear_annotation_button.pack(side="left", padx=10)

        self.annotation_pen_size_slider = customtkinter.CTkSlider(self.annotation_tool_frame, from_=1, to=10, command=self.set_annotation_pen_size)
        self.annotation_pen_size_slider.set(self.config.get('annotation_pen_size', 5))
        self.annotation_pen_size_slider.pack(side="left", padx=10, fill="x", expand=True)

    def _create_control_buttons(self):
        self.button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        button_font = ("Arial", 18)
        self.submit_button = customtkinter.CTkButton(self.button_frame, text="提交", command=self.app_callbacks['submit_answer'], height=50, font=button_font)
        self.submit_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.end_button = customtkinter.CTkButton(self.button_frame, text="提前结束", command=self.app_callbacks['finish_session'], height=50, font=button_font, fg_color="#D32F2F", hover_color="#B71C1C")
        self.end_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def _create_judgement_buttons(self):
        self.judgement_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.judgement_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.judgement_frame.grid_columnconfigure((0, 1), weight=1)

        button_font = ("Arial", 18)
        self.correct_button = customtkinter.CTkButton(self.judgement_frame, text="正确", command=lambda: self.app_callbacks['record_result'](True), height=50, font=button_font)
        self.correct_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.incorrect_button = customtkinter.CTkButton(self.judgement_frame, text="错误", command=lambda: self.app_callbacks['record_result'](False), height=50, font=button_font, fg_color="#D32F2F", hover_color="#B71C1C")
        self.incorrect_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")



    def set_pen_size(self, size):
        pen_size = int(size)
        self.canvas.set_pen_size(pen_size)
        self.config['pen_size'] = pen_size
        config_manager.save_config(self.config)

    def set_annotation_pen_size(self, size):
        pen_size = int(size)
        self.canvas.set_annotation_pen_size(pen_size)
        self.config['annotation_pen_size'] = pen_size
        config_manager.save_config(self.config)

    def set_pen_mode(self):
        self.canvas.paint_mode = "pen"
        self.pen_button.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
        self.eraser_button.configure(fg_color="gray")
        self.annotation_pen_button.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
        self.annotation_eraser_button.configure(fg_color="gray")

    def set_eraser_mode(self):
        self.canvas.paint_mode = "eraser"
        self.eraser_button.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
        self.pen_button.configure(fg_color="gray")
        self.annotation_eraser_button.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
        self.annotation_pen_button.configure(fg_color="gray")

    def update_prompt(self, text, current_word_index=None, total_words=None):
        if current_word_index is not None and total_words is not None:
            self.prompt_label.configure(text=f"[{current_word_index}/{total_words}] {text}")
        else:
            self.prompt_label.configure(text=text)

    def show_answer(self, text):
        self.answer_label.configure(text=f"正确答案: {text}")

    def reset_view(self):
        self.canvas.clear_canvas()
        self.canvas.clear_annotations() # 确保批注也被清除
        self.answer_label.configure(text="")
        self.judgement_frame.grid_forget()
        self.annotation_tool_frame.grid_forget()
        self.tool_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.submit_button.configure(state="normal")
        self.canvas.annotation_mode = False
        self.set_pen_mode()

    def enter_annotation_mode(self):
        self.canvas.annotation_mode = True
        self.prompt_label.configure(text="请用红色墨迹批注，完成后点击下方按钮")
        self.tool_frame.grid_forget()
        self.annotation_tool_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.button_frame.grid_forget()
        self.judgement_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.set_pen_mode()