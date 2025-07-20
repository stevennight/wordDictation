import customtkinter
from PIL import Image, ImageTk

class CorrectionView(customtkinter.CTkFrame):
    def __init__(self, parent, app_callbacks):
        super().__init__(parent, fg_color="transparent")
        self.app_callbacks = app_callbacks
        self.review_images = []
        self.current_review_index = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = customtkinter.CTkLabel(self, text="批改手写答案", font=("Arial", 24))
        self.title_label.grid(row=0, column=0, pady=10)

        self.image_label = customtkinter.CTkLabel(self, text="")
        self.image_label.grid(row=1, column=0, pady=10)

        self.word_label = customtkinter.CTkLabel(self, text="", font=("Arial", 20))
        self.word_label.grid(row=2, column=0, pady=10)

        button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)

        self.correct_button = customtkinter.CTkButton(button_frame, text="正确", command=lambda: self.record_correction(True), height=40, font=("Arial", 16))
        self.correct_button.pack(side="left", padx=20)

        self.incorrect_button = customtkinter.CTkButton(button_frame, text="错误", command=lambda: self.record_correction(False), height=40, font=("Arial", 16))
        self.incorrect_button.pack(side="left", padx=20)

    def start_correction(self, review_images):
        self.review_images = review_images
        self.current_review_index = 0
        self.show_next_for_correction()

    def show_next_for_correction(self):
        if self.current_review_index < len(self.review_images):
            item = self.review_images[self.current_review_index]
            word = item['word']
            image_path = item['image_path']

            self.word_label.configure(text=f"单词: {word}")

            img = Image.open(image_path)
            ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.image_label.configure(image=ctk_img)
        else:
            self.app_callbacks['finish_correction']()

    def record_correction(self, is_correct):
        self.app_callbacks['update_result_from_correction'](self.current_review_index, is_correct)
        self.current_review_index += 1
        self.show_next_for_correction()