from src.app import App
import os
from tkinterdnd2 import TkinterDnD
import platform

if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        print(f"Error setting DPI awareness: {e}")

HISTORY_DIR = "history"
IMAGE_CACHE_DIR = "handwriting_cache"

if __name__ == "__main__":
    # Create necessary directories
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    if not os.path.exists(IMAGE_CACHE_DIR):
        os.makedirs(IMAGE_CACHE_DIR)

    root = TkinterDnD.Tk()
    app = App(root)
    app.pack(fill="both", expand=True)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.iconbitmap("src/icon.ico")
    root.mainloop()