import customtkinter
from ..widgets.canvas import HandwritingCanvas

class DictationView(customtkinter.CTkFrame):
    def __init__(self, parent, app_callbacks):
        super().__init__(parent, fg_color="transparent")
        self.app_callbacks = app_callbacks

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.prompt_label = customtkinter.CTkLabel(self, text="", font=("Arial", 24))
        self.prompt_label.grid(row=0, column=0, pady=20)

        self.canvas = HandwritingCanvas(self)
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.answer_label = customtkinter.CTkLabel(self, text="", font=("Arial", 20), text_color="green")
        self.answer_label.grid(row=2, column=0, pady=10)

        self._create_tool_frame()
        self._create_control_buttons()
        self._create_judgement_buttons()

    def _create_tool_frame(self):
        self.tool_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.tool_frame.grid(row=3, column=0, pady=(0, 10))

        self.pen_button = customtkinter.CTkButton(self.tool_frame, text="画笔", command=self.set_pen_mode)
        self.pen_button.pack(side="left", padx=10, pady=5)

        self.eraser_button = customtkinter.CTkButton(self.tool_frame, text="橡皮擦", command=self.set_eraser_mode)
        self.eraser_button.pack(side="left", padx=10, pady=5)

        self.clear_button_tool = customtkinter.CTkButton(self.tool_frame, text="清空", command=self.canvas.clear_canvas)
        self.clear_button_tool.pack(side="left", padx=10, pady=5)

        self.input_mode_menu = customtkinter.CTkOptionMenu(self.tool_frame, values=["鼠标", "触摸", "笔"], command=self.set_input_mode)
        self.input_mode_menu.pack(side="left", padx=10, pady=5)
        self.set_pen_mode()

    def _create_control_buttons(self):
        self.button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        button_font = ("Arial", 18)
        self.submit_button = customtkinter.CTkButton(self.button_frame, text="提交", command=self.app_callbacks['submit_answer'], height=50, font=button_font)
        self.submit_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.end_button = customtkinter.CTkButton(self.button_frame, text="提前结束", command=self.app_callbacks['finish_session'], height=50, font=button_font, fg_color="#D32F2F")
        self.end_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def _create_judgement_buttons(self):
        self.judgement_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.judgement_frame.grid_columnconfigure((0, 1), weight=1)

        button_font = ("Arial", 18)
        self.correct_button = customtkinter.CTkButton(self.judgement_frame, text="正确", command=lambda: self.app_callbacks['record_result'](True), height=50, font=button_font)
        self.correct_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.incorrect_button = customtkinter.CTkButton(self.judgement_frame, text="错误", command=lambda: self.app_callbacks['record_result'](False), height=50, font=button_font)
        self.incorrect_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def set_input_mode(self, mode):
        self.app_callbacks['set_input_mode'](mode)
        self.canvas.set_input_mode(mode)

    def set_pen_mode(self):
        self.canvas.paint_mode = "pen"
        self.pen_button.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
        self.eraser_button.configure(fg_color="gray")

    def set_eraser_mode(self):
        self.canvas.paint_mode = "eraser"
        self.eraser_button.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
        self.pen_button.configure(fg_color="gray")

    def update_prompt(self, text):
        self.prompt_label.configure(text=text)

    def show_answer(self, text):
        self.answer_label.configure(text=f"正确答案: {text}")

    def reset_view(self):
        self.canvas.clear_canvas()
        self.canvas.clear_annotations() # 确保批注也被清除
        self.answer_label.configure(text="")
        self.judgement_frame.grid_forget()
        self.tool_frame.grid(row=3, column=0, pady=(0, 10))
        self.button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        self.submit_button.configure(state="normal")
        self.clear_button_tool.configure(text="清空", command=self.canvas.clear_canvas, state="normal")
        self.canvas.annotation_mode = False
        self.set_pen_mode()

    def enter_annotation_mode(self):
        self.canvas.annotation_mode = True
        self.prompt_label.configure(text="请用红色墨迹批注，完成后点击下方按钮")
        self.clear_button_tool.configure(text="清除批注", command=self.canvas.clear_annotations, state="normal")
        self.button_frame.grid_forget()
        self.judgement_frame.grid(row=4, column=0, pady=20, sticky="ew")