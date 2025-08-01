import customtkinter
import json
import os
from PIL import Image

class HistoryDetailView(customtkinter.CTkFrame):
    def __init__(self, master, callbacks, config, **kwargs):
        super().__init__(master, fg_color="transparent")
        self.callbacks = callbacks
        self.config = config
        self.file_name = kwargs.get('file_name')
        self.back_callback = kwargs.get('back_callback')
        self.is_summary_view = kwargs.get('is_summary_view', False)
        self.results = kwargs.get('results', [])
        stats = kwargs.get('stats', {})
        self.correct_count = stats.get('correct', 0)
        self.incorrect_count = stats.get('incorrect', 0)
        self.last_y = 0

        self._create_widgets()
        if self.is_summary_view:
            self.update_summary(self.correct_count, self.incorrect_count, self.results)
        else:
            self.load_history_details()


    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)

        title_text = "默写完成！" if self.is_summary_view else os.path.splitext(self.file_name)[0]
        self.title_label = customtkinter.CTkLabel(top_frame, text=title_text, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.pack()

        self.summary_frame = customtkinter.CTkFrame(top_frame, fg_color="transparent")
        self.summary_frame.pack(pady=5)
        
        self.filter_var = customtkinter.BooleanVar()
        self.filter_checkbox = customtkinter.CTkCheckBox(top_frame, text="只显示错误项", variable=self.filter_var, command=self.display_results, height=20)
        self.filter_checkbox.pack(pady=5)

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # 绑定事件到滚动框架和其内部的画布
        for widget in [self.scrollable_frame, self.scrollable_frame._parent_canvas]:
            widget.bind("<ButtonPress-1>", self._on_button_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_button_release)
            widget.bind("<MouseWheel>", self._on_mouse_wheel)
            widget.bind("<Button-4>", self._on_mouse_wheel)
            widget.bind("<Button-5>", self._on_mouse_wheel)

        button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20)

        self.retry_button = customtkinter.CTkButton(button_frame, text="重试错题", command=self.retry_incorrect, height=40, font=("Arial", 16))
        self.retry_button.pack(side="left", padx=20)
        
        back_command = self.callbacks.get('show_initial_view', lambda: None)
        self.back_button = customtkinter.CTkButton(button_frame, text="返回主菜单", command=back_command, height=40, font=("Arial", 16))
        self.back_button.pack(side="left", padx=20)

    def retry_incorrect(self):
        incorrect_results = [res for res in self.results if not res['correct']]
        if not incorrect_results:
            from tkinter import messagebox
            messagebox.showinfo("提示", "没有错题可以重做。")
            return

        if not self.is_summary_view:
            self.callbacks['retry_incorrect'](
                word_file_name=self.word_file_name, 
                timestamp=self.original_timestamp, 
                incorrect_words=incorrect_results
            )
        else:
            word_file_path = self.master.master.word_file_path
            original_word_file_name = os.path.basename(word_file_path) if word_file_path else None
            self.callbacks['retry_incorrect'](
                word_file_name=original_word_file_name, 
                timestamp=None, 
                incorrect_words=incorrect_results
            )

    def load_history_details(self):
        history_dir = "history"
        index_path = os.path.join(history_dir, "history_index.json")
        json_path = os.path.join(history_dir, self.file_name)

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            record = next((r for r in index if r['filename'] == self.file_name), None)

            if not record:
                print(f"Record not found for {self.file_name}")
                return

            self.word_file_name = record.get('word_file_name', '未知文件')
            self.timestamp = record.get('timestamp', '未知时间')
            self.original_timestamp = record.get('original_timestamp', self.timestamp)

            if record.get('is_retry'):
                self.title_label.configure(text=f"{self.word_file_name} {self.original_timestamp} ({self.timestamp})")
            else:
                self.title_label.configure(text=f"{self.word_file_name} ({self.timestamp})")

            with open(json_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)

            self.results = history_data.get("results", [])
            stats = record.get('stats', {})
            correct_count = stats.get('correct', 0)
            incorrect_count = stats.get('incorrect', 0)

            self.update_summary(correct_count, incorrect_count, self.results)

        except Exception as e:
            print(f"Error loading history detail: {e}")

    def update_summary(self, correct_count, incorrect_count, results):
        self.results = results
        total = correct_count + incorrect_count
        accuracy = (correct_count / total * 100) if total > 0 else 0

        accuracy_threshold = self.config.get('accuracy_threshold', 80)
        accuracy_color = "green" if accuracy >= accuracy_threshold else "red"

        # Clear previous summary widgets
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        summary_frame = self.summary_frame

        correct_label = customtkinter.CTkLabel(summary_frame, text=f"正确: {correct_count}", font=("Arial", 16), text_color="green")
        correct_label.pack(side="left", padx=5)

        incorrect_label = customtkinter.CTkLabel(summary_frame, text=f"错误: {incorrect_count}", font=("Arial", 16), text_color="red")
        incorrect_label.pack(side="left", padx=5)

        accuracy_label = customtkinter.CTkLabel(summary_frame, text=f"正确率: {accuracy:.1f}%", font=("Arial", 16), text_color=accuracy_color)
        accuracy_label.pack(side="left", padx=5)

        self.display_results()

        if incorrect_count == 0:
            self.retry_button.configure(state="disabled")
        else:
            self.retry_button.configure(state="normal")

    def display_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        results_to_display = self.results
        if self.filter_var.get():
            results_to_display = [res for res in self.results if not res['correct']]

        for i, res in enumerate(results_to_display):
            self.add_detail_entry(i, res)

    def show_full_image(self, image_path):
        if hasattr(self, 'full_image_frame') and self.full_image_frame.winfo_exists():
            self.full_image_frame.destroy()

        self.full_image_frame = customtkinter.CTkFrame(self, fg_color="black")
        self.full_image_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self.full_image_frame.lift()

        img = Image.open(image_path)
        
        max_width = self.winfo_width() * 0.9
        max_height = self.winfo_height() * 0.9
        
        img.thumbnail((max_width, max_height), Image.LANCZOS)

        ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        
        img_label = customtkinter.CTkLabel(self.full_image_frame, image=ctk_img, text="")
        img_label.pack(expand=True)
        
        self.full_image_frame.bind("<Button-1>", lambda e: self.full_image_frame.destroy())
        img_label.bind("<Button-1>", lambda e: self.full_image_frame.destroy())

    def add_detail_entry(self, index, res):
        item_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color=("gray90", "gray13"))
        item_frame.pack(fill="x", padx=10, pady=5)
        item_frame.grid_columnconfigure(0, weight=1)

        is_correct = res.get('correct', False)
        
        text_frame = customtkinter.CTkFrame(item_frame, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        prompt_label = customtkinter.CTkLabel(text_frame, text=f"{index+1}. 提示: {res['prompt']}\n正确答案: {res['answer']} ")
        prompt_label.pack(side="left")

        result_label = customtkinter.CTkLabel(text_frame, text="(正确)" if is_correct else "(错误)", text_color="green" if is_correct else "red")
        result_label.pack(side="left")

        copy_button = customtkinter.CTkButton(item_frame, text="抄写", width=50)
        copy_button.grid(row=0, column=1, sticky="e", padx=10)
        if self.callbacks and 'show_copying_view' in self.callbacks:
            copy_button.configure(command=lambda r=res: self.callbacks['show_copying_view'](r))

        image_frame = customtkinter.CTkFrame(item_frame, fg_color="transparent")
        image_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        original_image_path = res.get('original_image_path')
        annotated_image_path = res.get('annotated_image_path')

        if not self.is_summary_view and self.file_name:
            history_image_folder = os.path.join("history", os.path.splitext(self.file_name)[0])
            original_image_path = os.path.join(history_image_folder, f"word_{index}_original.png")
            annotated_image_path = os.path.join(history_image_folder, f"word_{index}_annotated.png")

        self.add_image(image_frame, original_image_path, 0)
        self.add_image(image_frame, annotated_image_path, 1)

        # Bind events to all child widgets of the item_frame
        for widget in item_frame.winfo_children():
            widget.bind("<ButtonPress-1>", self._on_button_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_button_release)
            widget.bind("<MouseWheel>", self._on_mouse_wheel)
            widget.bind("<Button-4>", self._on_mouse_wheel)
            widget.bind("<Button-5>", self._on_mouse_wheel)

    def add_image(self, parent, image_path, col):
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(200, 100))
                img_label = customtkinter.CTkLabel(parent, image=ctk_img, text="")
                img_label.grid(row=0, column=col, padx=5, pady=5)
                img_label.bind("<Button-1>", lambda e, p=image_path: self.show_full_image(p))
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")

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

    def _on_mouse_wheel(self, event):
        delta = -1 * (event.delta if hasattr(event, 'delta') else (-120 if event.num == 4 else 120))
        self.scrollable_frame._parent_canvas.yview_scroll(int(delta/40), "units")