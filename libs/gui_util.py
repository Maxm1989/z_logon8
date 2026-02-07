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
