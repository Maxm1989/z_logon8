import os
import tkinter as tk
from tkinter import ttk

from libs.guiCfg import GuiCfg
from libs.gui_util import center_window
from libs.OptionDB import sqliteDB
from libs import message


def _get_icon_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "icon.ico")


class DialogGroup(tk.Toplevel):
    def __init__(self, parent=None, parm=None):
        super().__init__(parent)
        self.withdraw()
        parm = parm or {}
        self.db = sqliteDB()
        self.guiCfg = GuiCfg()

        self.type = parm.get('type')
        self.group = parm.get('group', [])
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
        self.geometry('429x180')
        self.resizable(False, False)

        try:
            self.iconbitmap(_get_icon_path())
        except tk.TclError:
            pass

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text='分组：').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.LineEditGroup = ttk.Entry(main_frame, width=40)
        self.LineEditGroup.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(main_frame, text='描述：').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.LineEditDesc = ttk.Entry(main_frame, width=40)
        self.LineEditDesc.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        main_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text='确定', command=self.accept).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.reject).pack(side=tk.LEFT)

        self.LineEditGroup.bind('<KeyRelease>', lambda e: self.on_changed())
        self.LineEditDesc.bind('<KeyRelease>', lambda e: self.on_changed())

    def init_data(self):
        if self.type == 'attribute':
            self.title('分组属性')
            self.LineEditGroup.insert(0, self.group.get('node', ''))
            self.LineEditDesc.insert(0, self.group.get('desc', ''))
        else:
            self.title('添加分组')

    def on_changed(self):
        self.changed = True

    def accept(self):
        if self.changed:
            if not self.LineEditGroup.get().strip():
                message.warning('注意', '请输入分组！')
                return

            self.result = {
                'code': 'ok',
                'data': {
                    'node': self.LineEditGroup.get().strip(),
                    'desc': self.LineEditDesc.get().strip(),
                    'type': self.group.get('type', 'F') if 'type' in self.group else 'F',
                    'uuid': self.group.get('uuid') if 'type' in self.group else None,
                }
            }
        self.reject()

    def reject(self):
        self.grab_release()
        self.destroy()
