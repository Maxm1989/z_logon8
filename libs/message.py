import tkinter as tk
from tkinter import messagebox
from libs.gui_util import get_icon_path


def _setup_icon():
    try:
        root = tk._default_root
        if root and root.winfo_exists():
            root.iconbitmap(get_icon_path())
    except (tk.TclError, AttributeError):
        pass


def about(title, msg):
    _setup_icon()
    messagebox.showinfo(title, msg)


def error(title, msg):
    _setup_icon()
    messagebox.showerror(title, msg)


def warning(title, msg):
    _setup_icon()
    result = messagebox.askyesno(title, msg)
    return result  # True=Yes, False=No (兼容原 PyQt StandardButton.Yes 检查)


def question(title, msg):
    _setup_icon()
    result = messagebox.askquestion(title, msg)
    return result


def information(title, msg):
    _setup_icon()
    messagebox.showinfo(title, msg)
