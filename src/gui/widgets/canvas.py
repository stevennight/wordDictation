import customtkinter
from tkinter import messagebox
import tkinter
from PIL import Image, ImageGrab
import os

IMAGE_CACHE_DIR = "handwriting_cache"

class HandwritingCanvas(customtkinter.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", highlightthickness=0, **kwargs)
        self.parent = parent
        self.last_x, self.last_y = None, None
        self.paint_mode = "pen"
        self.pen_color = "black"
        self.pen_width = 4
        self.annotation_pen_width = 4
        self.eraser_width = 20
        self.annotation_mode = False

        self.bind("<ButtonPress-1>", self.start_paint)
        self.bind("<B1-Motion>", self.paint)
        self.bind("<ButtonRelease-1>", self.reset_paint)

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_width = int(size)

    def set_annotation_pen_size(self, size):
        self.annotation_pen_width = int(size)

    def set_eraser_size(self, size):
        self.eraser_width = int(size)



    def start_paint(self, event):
        self.last_x, self.last_y = event.x, event.y

    def paint(self, event):
        if self.last_x and self.last_y:
            if self.annotation_mode:
                color = "red"
                width = self.annotation_pen_width
                self.create_line(self.last_x, self.last_y, event.x, event.y, fill=color, width=width, capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=1, tags="annotation")
            else:
                color = self.pen_color if self.paint_mode == "pen" else "white"
                width = self.pen_width if self.paint_mode == "pen" else self.eraser_width
                self.create_line(self.last_x, self.last_y, event.x, event.y, fill=color, width=width, capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=1)
            self.last_x, self.last_y = event.x, event.y

    def reset_paint(self, event):
        self.last_x, self.last_y = None, None


    def clear_canvas(self):
        self.delete("all")

    def clear_annotations(self):
        self.delete("annotation")

    def save_image(self, filename):
        """Saves the current canvas content as an image."""
        try:
            # Create the cache directory if it doesn't exist
            if not os.path.exists(IMAGE_CACHE_DIR):
                os.makedirs(IMAGE_CACHE_DIR)

            x = self.winfo_rootx()
            y = self.winfo_rooty()
            w = self.winfo_width()
            h = self.winfo_height()
            
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            img_path = os.path.join(IMAGE_CACHE_DIR, filename)
            img.save(img_path)
            return img_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
            return None
