import os


def get_icon_path():
    """获取应用图标路径"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "icon.ico")


def center_window(win, width=None, height=None):
    """将窗口居中显示到屏幕"""
    win.update_idletasks()
    if width is None:
        width = win.winfo_reqwidth()
    if height is None:
        height = win.winfo_reqheight()
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f'{width}x{height}+{x}+{y}')
