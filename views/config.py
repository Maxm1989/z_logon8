import tkinter as tk
from tkinter import ttk
from libs.Model import Config
from libs.guiCfg import GuiCfg
from libs.gui_util import center_window, get_icon_path
from libs.OptionDB import sqliteDB
from libs import message


class DialogCfg(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.withdraw()
        self.db = sqliteDB()
        self.guiCfg = GuiCfg()

        self.changed = False
        self.result = {
            'code': None,
            'data': None
        }

        self._setup_ui()
        self.init_data()
        self.update_idletasks()
        center_window(self, 429, 180)
        self.deiconify()
        if parent:
            self.transient(parent)
        self.grab_set()
        if parent:
            parent.wait_window(self)

    def _setup_ui(self):
        self.title('配置')
        self.geometry('429x180')
        self.resizable(False, False)

        try:
            self.iconbitmap(get_icon_path())
        except tk.TclError:
            pass

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text='GUI安装路径：').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.lineEditConfig = ttk.Entry(main_frame, width=50)
        self.lineEditConfig.grid(row=1, column=0, sticky=tk.EW, pady=(0, 20))
        main_frame.columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, sticky=tk.E)

        def on_ok():
            self.accept()

        def on_cancel():
            self.reject()

        ttk.Button(btn_frame, text='确定', command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='取消', command=on_cancel).pack(side=tk.LEFT)

        self.lineEditConfig.bind('<KeyRelease>', lambda e: self.on_changed())

    def init_data(self):
        db_config = self.db.session.query(Config).filter(Config.key == 'path').first()
        if db_config:
            self.lineEditConfig.insert(0, db_config.value)

    def on_changed(self):
        self.changed = True

    def accept(self):
        if self.changed:
            if not self.lineEditConfig.get().strip():
                message.warning('注意', '请输入saplogon.exe安装路径！')
                return

            self.result = {
                'code': 'ok',
                'data': {'path': self.lineEditConfig.get().strip()}
            }
        self.reject()

    def reject(self):
        self.grab_release()
        self.destroy()
