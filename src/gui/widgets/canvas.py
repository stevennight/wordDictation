import customtkinter
from tkinter import messagebox
import tkinter
from PIL import ImageGrab
import os

IMAGE_CACHE_DIR = "handwriting_cache"

class HandwritingCanvas(customtkinter.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", highlightthickness=0, **kwargs)
        self.parent = parent
        self.last_x, self.last_y = None, None
        self.paint_mode = "pen"
        self.pen_color = "black"
        self.pen_size = 4
        self.annotation_mode = False

        self.input_mode = "鼠标"
        self.set_input_mode(self.input_mode)

    def set_pen_color(self, color):
        self.pen_color = color

    def set_eraser_size(self, size):
        self.pen_size = int(size)

    def set_input_mode(self, mode):
        self.input_mode = mode
        # 解绑所有事件，以防重复绑定
        for event in ["<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>", 
                      "<Touch-Begin>", "<Touch-Move>", "<Touch-End>",
                      "<Pen-Begin>", "<Pen-Move>", "<Pen-End>"]:
            self.unbind(event)

        try:
            self.bind("<ButtonPress-1>", self.start_paint)
            self.bind("<B1-Motion>", self.paint)
            self.bind("<ButtonRelease-1>", self.reset_paint)
            self.bind("<Touch-Begin>", self.start_paint)
            self.bind("<Touch-Move>", self.paint)
            self.bind("<Touch-End>", self.reset_paint)
            self.bind("<Pen-Begin>", self.start_paint)
            self.bind("<Pen-Move>", self.paint)
            self.bind("<Pen-End>", self.reset_paint)
        except tkinter.TclError as e:
            if 'Touch' in str(e) or 'Pen' in str(e):
                pass # 忽略不支持的触摸和笔事件
            else:
                raise e

    def start_paint(self, event):
        if not self._is_event_allowed(event):
            return
        self.last_x, self.last_y = event.x, event.y

    def paint(self, event):
        if not self._is_event_allowed(event) or self.last_x is None:
            return
        if self.last_x and self.last_y:
            if self.annotation_mode:
                color = "red"
                width = 3
                self.create_line(self.last_x, self.last_y, event.x, event.y, fill=color, width=width, capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=36, tags="annotation")
            else:
                color = self.pen_color if self.paint_mode == "pen" else "white"
                width = self.pen_size if self.paint_mode == "pen" else 50
                self.create_line(self.last_x, self.last_y, event.x, event.y, fill=color, width=width, capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=36)
            self.last_x, self.last_y = event.x, event.y

    def reset_paint(self, event):
        self.last_x, self.last_y = None, None

    def _is_event_allowed(self, event):
        event_type_str = str(event.type)

        if self.input_mode == "鼠标":
            return event_type_str in ["ButtonPress", "Motion", "ButtonRelease", "4", "5", "6"]
        elif self.input_mode == "触摸":
            return event_type_str in ["TouchBegin", "TouchMove", "TouchEnd"]
        elif self.input_mode == "笔":
            return event_type_str in ["PenBegin", "PenMove", "PenEnd"]
        return False

    def clear_canvas(self):
        self.delete("all")

    def clear_annotations(self):
        self.delete("annotation")

    def save_image(self, filename):
        """Saves the current canvas content as an image."""
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        try:
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            img_path = os.path.join(IMAGE_CACHE_DIR, filename)
            img.save(img_path)
            return img_path
        except Exception as e:
            print(f"Error saving canvas image: {e}")
            return None
