import customtkinter
import tkinter
import random
import os
import sys


from .gui.views.initial_view import InitialView
from .gui.views.dictation_view import DictationView
from .gui.views.correction_view import CorrectionView
from .gui.views.history_view import HistoryView
from .gui.views.history_detail_view import HistoryDetailView
from .gui.views.copying_view import CopyingView
from .gui.settings_window import SettingsWindow
from .utils.config_manager import load_config, save_config
from .utils.file_handler import load_words_from_file, clear_handwriting_cache, save_history
from .utils.registry_handler import do_register, do_unregister

class App(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("默写小助手")
        self.master.geometry("1280x900")
        self.master.attributes("-fullscreen", True)

        self.config = load_config()
        self.apply_config()

        self.words = []
        self.dictation_list = []
        self.current_word_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.results = []
        self.review_images = []
        self.word_file_path = None
        self.fullscreen = True
        self.history_detail_context = None

        self._create_widgets()
        self.show_initial_view()

        if len(sys.argv) > 1:
            self.load_words(sys.argv[1])

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top bar
        top_frame = customtkinter.CTkFrame(self, height=40, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)

        self.history_button = customtkinter.CTkButton(top_frame, text="历史记录", command=self.show_history)
        self.history_button.pack(side="left", padx=10, pady=5)

        self.fullscreen_button = customtkinter.CTkButton(top_frame, text="全屏", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side="left", padx=10, pady=5)

        self.settings_button = customtkinter.CTkButton(top_frame, text="设置", command=self.open_settings)
        self.settings_button.pack(side="right", padx=10, pady=5)

        # Main frame for views
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def apply_config(self):
        customtkinter.set_appearance_mode(self.config.get("theme", "System"))

    def save_config(self):
        save_config(self.config)

    def switch_view(self, view_class, **kwargs):
        if hasattr(self, 'current_view'):
            self.current_view.destroy()
        
        callbacks = self.get_callbacks()
        self.current_view = view_class(self.main_frame, callbacks, **kwargs)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def get_callbacks(self):
        return {
            'load_words': self.load_words,
            'load_words_from_dialog': self.load_words_from_dialog,
            'start_with_order': self.start_with_order,
            'set_quantity_and_start': self.set_quantity_and_start,
            'ask_custom_quantity': self.ask_custom_quantity,
            'submit_answer': self.submit_answer,
            'record_result': self.record_result,
            'set_input_mode': self.set_input_mode,
            'retry_incorrect': self.retry_incorrect,
            'finish_session': self.finish_session,
            'update_result_from_correction': self.update_result_from_correction,
            'finish_correction': self.finish_correction,
            'show_history': self.show_history,
            'show_initial_view': self.show_initial_view,
            'view_history_detail': self.view_history_detail,
            'show_copying_view': self.show_copying_view,
            'back_to_detail': self.back_to_detail_view
        }

    def show_initial_view(self):
        self.history_button.pack(side="left", padx=10, pady=5)
        self.switch_view(InitialView)

    def view_history_detail(self, file_name):
        self.history_detail_context = {
            'file_name': file_name,
            'back_callback': self.show_history
        }
        self.switch_view(HistoryDetailView, **self.history_detail_context)

    def show_history_detail_view(self):
        if self.history_detail_context:
            self.switch_view(HistoryDetailView, **self.history_detail_context)

    def show_copying_view(self, word_data):
        self.switch_view(CopyingView, word_data=word_data)

    def back_to_detail_view(self):
        self.show_history_detail_view()

    def show_history(self):
        self.switch_view(HistoryView)

    def load_words_from_dialog(self):
        filepath = customtkinter.filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if filepath:
            self.load_words(filepath)

    def load_words(self, filepath):
        self.word_file_path = filepath
        self.words, message = load_words_from_file(filepath)
        if self.words:
            if hasattr(self, 'current_view') and isinstance(self.current_view, InitialView):
                self.current_view.update_status(message)
                self.current_view.show_order_selection()
        else:
            if hasattr(self, 'current_view') and isinstance(self.current_view, InitialView):
                self.current_view.update_status(message)

    def start_with_order(self, shuffle):
        self.dictation_list = self.words.copy()
        if shuffle:
            random.shuffle(self.dictation_list)
        if hasattr(self, 'current_view') and isinstance(self.current_view, InitialView):
            self.current_view.show_quantity_selection()

    def ask_custom_quantity(self):
        dialog = customtkinter.CTkInputDialog(text="请输入默写数量:", title="自定义数量")
        value = dialog.get_input()
        if value and value.isdigit():
            self.set_quantity_and_start(int(value))

    def set_quantity_and_start(self, quantity):
        if quantity > 0:
            self.dictation_list = self.dictation_list[:quantity]
        self.start_dictation()

    def start_dictation(self):
        self.history_button.pack_forget()
        self.current_word_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.results = []
        self.review_images = []
        clear_handwriting_cache()
        self.switch_view(DictationView)
        self.show_next_word()

    def show_next_word(self):
        if self.current_word_index < len(self.dictation_list):
            word_data = self.dictation_list[self.current_word_index]
            if hasattr(self, 'current_view') and isinstance(self.current_view, DictationView):
                self.current_view.reset_view()
                self.current_view.update_prompt(word_data['prompt'])
        else:
            self.show_summary()

    def submit_answer(self):
        word_data = self.dictation_list[self.current_word_index]
        if hasattr(self, 'current_view') and isinstance(self.current_view, DictationView):
            self.current_view.show_answer(word_data['answer'])
            original_image_path = self.current_view.canvas.save_image(f"word_{self.current_word_index}_original.png")
            self.review_images.append({'word': word_data['answer'], 'original_image_path': original_image_path})
            self.current_view.enter_annotation_mode()

    def record_result(self, is_correct):
        if self.current_word_index >= len(self.dictation_list):
            return

        word_data = self.dictation_list[self.current_word_index]
        review_image_data = self.review_images[self.current_word_index]

        if hasattr(self, 'current_view') and isinstance(self.current_view, DictationView):
            annotated_image_path = self.current_view.canvas.save_image(f"word_{self.current_word_index}_annotated.png")
            review_image_data['annotated_image_path'] = annotated_image_path

        self.results.append({
            'prompt': word_data['prompt'],
            'answer': word_data['answer'],
            'correct': is_correct,
            'original_image_path': review_image_data.get('original_image_path'),
            'annotated_image_path': review_image_data.get('annotated_image_path')
        })

        if is_correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1
        
        self.current_word_index += 1
        self.show_next_word()

    def show_summary(self, save=True):
        if not self.results:
            self.show_initial_view()
            return

        stats = {
            'correct': self.correct_count,
            'incorrect': self.incorrect_count,
            'total': len(self.dictation_list)
        }
        if save:
            save_history(self.results, stats, self.word_file_path, self.config)
        self.history_detail_context = {
            'is_summary_view': True,
            'results': self.results,
            'stats': stats,
            'back_callback': self.show_initial_view
        }
        self.switch_view(HistoryDetailView, **self.history_detail_context)

    def retry_incorrect(self):
        self.dictation_list = [res for res in self.results if not res['correct']]
        # Convert back to the original format if needed
        self.dictation_list = [{'prompt': d['prompt'], 'answer': d['answer']} for d in self.dictation_list]
        self.start_dictation()

    def finish_session(self):
        self.history_button.pack(side="left", padx=10, pady=5)
        if self.results:
            self.show_summary(save=True)
        else:
            self.show_initial_view()

    def enter_correction_mode(self):
        self.switch_view(CorrectionView)
        if hasattr(self, 'current_view') and isinstance(self.current_view, CorrectionView):
            self.current_view.start_correction(self.review_images)

    def update_result_from_correction(self, index, is_correct):
        # This logic needs to be refined based on how correction links to results
        pass

    def finish_correction(self):
        self.show_summary()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.master.attributes("-fullscreen", self.fullscreen)

    def open_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        self.settings_window.focus()

    def set_input_mode(self, mode):
        self.config['input_mode'] = mode
        self.save_config()

    def register_context_menu(self):
        do_register()

    def unregister_context_menu(self):
        do_unregister()