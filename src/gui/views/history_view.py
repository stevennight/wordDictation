import customtkinter
import os
import json
from src.utils.file_handler import delete_history_record

class HistoryView(customtkinter.CTkFrame):
    def __init__(self, master, callbacks, config, **kwargs):
        super().__init__(master, fg_color="transparent")
        self.callbacks = callbacks
        self.config = config
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

        try:
            with open(os.path.join(history_dir, "history_index.json"), 'r', encoding='utf-8') as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        # 按时间倒序排序
        index.sort(key=lambda x: x['timestamp'], reverse=True)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for record in index:
            self.add_history_entry(record)

    def add_history_entry(self, record):
        entry_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color=("gray85", "gray15"))
        entry_frame.pack(fill="x", padx=10, pady=5)

        # 创建一个子框架来容纳文件名和重做标识
        title_frame = customtkinter.CTkFrame(entry_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        # 显示默写文件名和时间
        if record.get('is_retry'):
            display_text = f"{record['word_file_name']} {record.get('original_timestamp', '')}"
        else:
            display_text = f"{record['word_file_name']}"
        
        label = customtkinter.CTkLabel(title_frame, text=display_text, anchor="w")
        label.pack(side="left")

        record_time_label = customtkinter.CTkLabel(
            title_frame,
            text=f"{record['timestamp']}",
            fg_color="#666666",
            text_color="white",
            corner_radius=4,
            width=40,
            height=20
        )
        record_time_label.pack(side="left", padx=10)

        # 如果是重做记录，添加红底白字的"重做"标识
        if record.get('is_retry'):
            retry_label = customtkinter.CTkLabel(
                title_frame,
                text="重做",
                fg_color="#C00000",
                text_color="white",
                corner_radius=4,
                width=40,
                height=20
            )
            retry_label.pack(side="left", padx=10)

        # 显示统计信息
        stats = record['stats']
        correct = stats.get('correct', 0)
        wrong = stats.get('incorrect', 0)
        total = correct + wrong
        accuracy = (correct / total * 100) if total > 0 else 0

        accuracy_threshold = self.config.get('accuracy_threshold', 80)
        accuracy_color = "green" if accuracy >= accuracy_threshold else "red"

        stats_text = f"{correct}/{wrong}/{total}  {accuracy:.1f}%"
        stats_label = customtkinter.CTkLabel(entry_frame, text=stats_text, anchor="e", text_color=accuracy_color)
        stats_label.pack(side="left", padx=10)

        # 绑定事件处理器
        view_command = lambda f=record['filename']: self.callbacks['view_history_detail'](f)
        
        # 将双击事件绑定到整个条目框架
        for widget in [entry_frame, title_frame, label, stats_label]:
            widget.bind("<Double-Button-1>", lambda e, f=record['filename']: self.callbacks['view_history_detail'](f))
            widget.bind("<ButtonPress-1>", self._on_button_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_button_release)

        # 添加按钮
        view_button = customtkinter.CTkButton(entry_frame, text="查看", width=60, command=lambda f=record['filename']: self.callbacks['view_history_detail'](f))
        view_button.pack(side="right", padx=5)

        delete_button = customtkinter.CTkButton(entry_frame, text="删除", width=60, fg_color="#C00000", hover_color="#A00000", command=lambda f=record['filename']: self.delete_history(f))
        delete_button.pack(side="right", padx=5)



    def _on_button_press(self, event):
        self.last_y = event.y
        self.dragging = True

    def _on_motion(self, event):
        if hasattr(self, 'dragging') and self.dragging:
            delta_y = event.y - self.last_y
            first, last = self.scrollable_frame._parent_canvas.yview()

            # 向上拖动 (内容向下滚动)
            if delta_y > 0 and first > 0:
                self.scrollable_frame._parent_canvas.yview_scroll(-1, "units")
            # 向下拖动 (内容向上滚动)
            elif delta_y < 0 and last < 1.0:
                self.scrollable_frame._parent_canvas.yview_scroll(1, "units")

            self.last_y = event.y

    def _on_button_release(self, event):
        self.dragging = False

    def delete_history(self, file_name):
        try:
            delete_history_record(file_name)
            self.load_history() # 刷新列表
        except Exception as e:
            print(f"Error deleting history: {e}")