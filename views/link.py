import uuid as PUUID
import os
import tkinter as tk
from tkinter import ttk

from libs.Model import Node
from libs.guiCfg import GuiCfg
from libs.gui_util import center_window
from libs.OptionDB import sqliteDB
from libs import message


def _get_icon_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "icon.ico")


class DialogLink(tk.Toplevel):
    def __init__(self, parent=None, param=None):
        super().__init__(parent)
        self.withdraw()
        param = param or {}
        self.data = {
            'type': param.get('type', ''),
            'curGroup': param.get('curGroup', ''),
            'link': param.get('link', '')
        }
        self.result = {'code': None, 'data': None}

        self.db = sqliteDB()
        self.guiCfg = GuiCfg()
        self.changed = False

        self._setup_ui()
        self.init_data()
        self.update_idletasks()
        center_window(self, 429, 320)
        self.deiconify()
        if parent:
            self.transient(parent)
        self.grab_set()
        if parent:
            parent.wait_window(self)

    def _setup_ui(self):
        self.geometry('429x320')
        self.resizable(False, False)

        try:
            self.iconbitmap(_get_icon_path())
        except tk.TclError:
            pass

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        row = 0

        ttk.Label(main_frame, text='快速连接：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.LineEditLink = ttk.Entry(main_frame, width=40)
        self.LineEditLink.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text='描述：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.LineEditDesc = ttk.Entry(main_frame, width=40)
        self.LineEditDesc.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text='分组：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.comboBoxGroup = ttk.Combobox(main_frame, width=37, state='readonly')
        self.comboBoxGroup.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text='SAP连接：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.comboBoxSystem = ttk.Combobox(main_frame, width=37, state='readonly')
        self.comboBoxSystem.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text='Client：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.LineEditClient = ttk.Entry(main_frame, width=40)
        self.LineEditClient.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text='用户：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.LineEditUser = ttk.Entry(main_frame, width=40)
        self.LineEditUser.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        ttk.Label(main_frame, text='密码：').grid(row=row, column=0, sticky=tk.W, pady=3)
        pw_frame = ttk.Frame(main_frame)
        pw_frame.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        self.LineEditPassword = ttk.Entry(pw_frame, width=40, show='*')
        self.LineEditPassword.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._pw_visible = tk.BooleanVar(value=False)
        cb_show_pw = ttk.Checkbutton(pw_frame, text='显示', variable=self._pw_visible, command=self._toggle_pw_visible)
        cb_show_pw.pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        ttk.Label(main_frame, text='语言：').grid(row=row, column=0, sticky=tk.W, pady=3)
        self.comboBoxLanguage = ttk.Combobox(main_frame, width=37, values=['ZH', 'EN'], state='readonly')
        self.comboBoxLanguage.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        row += 1

        main_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text='确定', command=self.accept).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.reject).pack(side=tk.LEFT)

        for w in [self.LineEditLink, self.LineEditDesc, self.LineEditClient, self.LineEditUser, self.LineEditPassword]:
            w.bind('<KeyRelease>', lambda e: self.on_changed())
        self.comboBoxSystem.bind('<<ComboboxSelected>>', lambda e: self.on_changed())
        self.comboBoxLanguage.bind('<<ComboboxSelected>>', lambda e: self.on_changed())
        self.comboBoxGroup.bind('<<ComboboxSelected>>', lambda e: self.on_changed())

    def init_data(self):
        for item in self.guiCfg.getSapGuiLogonConfig():
            self.comboBoxSystem['values'] = list(self.comboBoxSystem['values']) + [item.get('system')]

        self._group_data = {}
        for item in self.db.getGroup():
            self.comboBoxGroup['values'] = list(self.comboBoxGroup['values']) + [item.get('group')]
            self._group_data[item.get('group')] = str(item.get('uuid'))

        if self.data.get('type') == 'add':
            self.title('添加新连接')
            if self.data.get('curGroup'):
                cur = self.data.get('curGroup')
                node_name = cur.get('node', '')
                if node_name and node_name in self._group_data:
                    self.comboBoxGroup.set(node_name)
            self.comboBoxLanguage.set('ZH')  # 默认中文
        elif self.data.get('type') == 'attribute':
            self.title('连接属性')
            link = self.data.get('link', {})
            self.LineEditLink.insert(0, link.get('node', ''))
            self.LineEditDesc.insert(0, link.get('desc', ''))
            self.comboBoxSystem.set(link.get('system', ''))
            self.LineEditClient.insert(0, link.get('client', ''))
            self.LineEditUser.insert(0, link.get('user', ''))
            self.LineEditPassword.insert(0, link.get('password', ''))
            self.comboBoxLanguage.set(link.get('language', ''))
            self.comboBoxGroup.set(link.get('group', ''))

    def _toggle_pw_visible(self):
        self.LineEditPassword.configure(show='' if self._pw_visible.get() else '*')

    def on_changed(self):
        self.changed = True

    def accept(self):
        if self.changed:
            group_text = self.comboBoxGroup.get()
            puuid = self._group_data.get(group_text, '')

            input_link = {
                'node': self.LineEditLink.get().strip(),
                'desc': self.LineEditDesc.get().strip(),
                'system': self.comboBoxSystem.get().strip(),
                'client': self.LineEditClient.get().strip(),
                'user': self.LineEditUser.get().strip(),
                'password': self.LineEditPassword.get().strip(),
                'language': self.comboBoxLanguage.get().strip(),
                'group': group_text,
                'puuid': puuid
            }

            if not input_link['system']:
                message.warning('注意', '请选择系统连接！')
                return
            if not input_link['client']:
                message.warning('注意', '请输入Client！')
                return
            if not input_link['user']:
                message.warning('注意', '请输入用户！')
                return
            if not input_link['password']:
                message.warning('注意', '请输入密码！')
                return
            if not input_link['language']:
                message.warning('注意', '请选择语言！')
                return
            if not input_link['node']:
                input_link['node'] = '{system}-{client}'.format(
                    system=input_link['system'], client=input_link['client'])

            if input_link['node']:
                if self.data.get('type') == 'add':
                    db_link = self.db.session.query(Node).filter(
                        Node.puuid == PUUID.UUID(input_link.get('puuid')),
                        Node.node == input_link.get('node')).first()
                else:
                    db_link = self.db.session.query(Node).filter(
                        Node.puuid == PUUID.UUID(input_link.get('puuid')),
                        Node.node == input_link.get('node'),
                        Node.uuid != PUUID.UUID(self.data.get('link', {}).get('uuid', ''))).first()
                if db_link:
                    message.warning('注意', '已存在相同的连接名称，请修改！')
                    return

            self.result['code'] = 'ok'
            self.result['data'] = input_link

        self.reject()

    def reject(self):
        self.grab_release()
        self.destroy()
