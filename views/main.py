import uuid as PUUID
import os
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas

_HAS_PIL = False

from views.config import DialogCfg
from views.link import DialogLink
from views.group import DialogGroup
from libs.Model import Node, Link, Config
from libs.guiCfg import GuiCfg
from libs.gui_util import center_window
from libs.OptionDB import sqliteDB
from libs import message


def _get_icon_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "icon.ico")


def _create_folder_closed_icon(size=16):
    """创建关闭的文件夹图标，返回PhotoImage对象"""
    img = tk.PhotoImage(width=size, height=size)
    
    # 设置透明背景
    for x in range(size):
        for y in range(size):
            img.put("#%02x%02x%02x" % (255, 255, 255), (x, y))  # 白色背景
    
    # 绘制文件夹身体
    for x in range(2, size-2):
        for y in range(4, size-2):
            img.put("#FFB84D", (x, y))  # 橙黄色
    
    # 绘制边框
    for x in range(2, size-2):
        img.put("#E69500", (x, 4))  # 上边框
        img.put("#E69500", (x, size-3))  # 下边框
    for y in range(4, size-2):
        img.put("#E69500", (2, y))  # 左边框
        img.put("#E69500", (size-3, y))  # 右边框
    
    # 绘制顶部标签
    for x in range(2, size-2):
        for y in range(1, 4):
            if y == 1:  # 顶部线
                img.put("#E69500", (x, y))
            elif y == 2:  # 中间填充
                img.put("#FFD966", (x, y))
            elif y == 3 and (x <= 5 or x >= size-5):  # 两边竖线
                img.put("#E69500", (x, y))
    
    return img


def _create_folder_open_icon(size=16):
    """创建打开的文件夹图标，返回PhotoImage对象"""
    img = tk.PhotoImage(width=size, height=size)
    
    # 设置透明背景
    for x in range(size):
        for y in range(size):
            img.put("#%02x%02x%02x" % (255, 255, 255), (x, y))  # 白色背景
    
    # 绘制文件夹身体
    for x in range(2, size-2):
        for y in range(5, size-2):
            img.put("#FFB84D", (x, y))
    
    # 绘制边框
    for x in range(2, size-2):
        img.put("#E69500", (x, 5))  # 上边框
        img.put("#E69500", (x, size-3))  # 下边框
    for y in range(5, size-2):
        img.put("#E69500", (2, y))  # 左边框
        img.put("#E69500", (size-3, y))  # 右边框
    
    # 绘制打开的标签部分
    # 左侧标签
    for x in range(2, 8):
        for y in range(2, 5):
            if y == 2:  # 顶部线
                img.put("#E69500", (x, y))
            elif y == 3:  # 中间填充
                img.put("#FFD966", (x, y))
            elif y == 4 and (x == 2 or x == 7):  # 两边竖线
                img.put("#E69500", (x, y))
    
    # 右侧标签
    for x in range(size-8, size-2):
        for y in range(2, 5):
            if y == 2:  # 顶部线
                img.put("#E69500", (x, y))
            elif y == 3:  # 中间填充
                img.put("#FFD966", (x, y))
            elif y == 4 and (x == size-8 or x == size-3):  # 两边竖线
                img.put("#E69500", (x, y))
    
    return img


def _create_link_icon(size=16):
    """创建连接图标：插头造型，返回PhotoImage对象"""
    img = tk.PhotoImage(width=size, height=size)
    
    # 设置透明背景
    for x in range(size):
        for y in range(size):
            img.put("#%02x%02x%02x" % (255, 255, 255), (x, y))  # 白色背景
    
    # 绘制插头主体（矩形）
    for x in range(3, size-3):
        for y in range(2, size-6):
            img.put("#81C784", (x, y))  # 浅绿色
    
    # 绘制插头边框
    for x in range(3, size-3):
        img.put("#4CAF50", (x, 2))  # 上边框
        img.put("#4CAF50", (x, size-7))  # 下边框
    for y in range(2, size-6):
        img.put("#4CAF50", (3, y))  # 左边框
        img.put("#4CAF50", (size-4, y))  # 右边框
    
    # 绘制两个插脚
    for x in range(5, 7):
        for y in range(size-6, size-2):
            img.put("#4CAF50", (x, y))  # 左插脚
    for x in range(size-7, size-5):
        for y in range(size-6, size-2):
            img.put("#4CAF50", (x, y))  # 右插脚
    
    return img


class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        try:
            self.db = sqliteDB()
        except Exception as e:
            message.error('错误', f'数据库初始化失败: {e}')
            self.destroy()
            raise SystemExit(1)
        self.guiCfg = GuiCfg()
        self.init = True
        self._setup_ui()
        self.set_tree()
        self.init = False

    def _setup_ui(self):
        self.withdraw()
        self.title("Z Logon")
        self.geometry("531x560")
        self.resizable(False, False)

        try:
            self.iconbitmap(_get_icon_path())
        except tk.TclError:
            pass

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        menubar = tk.Menu(self)
        self['menu'] = menubar

        menu_options = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="选项", menu=menu_options)
        menu_options.add_command(label="配置", command=self.config)
        menu_options.add_separator()
        menu_options.add_command(label="退出", command=self.exit)

        menu_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=menu_help)
        menu_help.add_command(label="关于", command=self.about)

        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # 文件夹开合图标
        style = ttk.Style()
        style.configure('.', indicatorsize=0)

        columns = ('desc', 'id', 'type')
        self.treeView = ttk.Treeview(main_frame, columns=columns, height=25, selectmode='browse', show='tree headings')
        self.treeView.heading('#0', text='连接')
        self.treeView.heading('desc', text='描述')
        self.treeView.heading('id', text='')
        self.treeView.heading('type', text='')

        self.treeView.column('#0', width=240, minwidth=240)
        self.treeView.column('desc', width=200, minwidth=200)
        self.treeView.column('id', width=0, minwidth=0, stretch=False)
        self.treeView.column('type', width=0, minwidth=0, stretch=False)

        self.treeView.grid(row=0, column=0, sticky=tk.NSEW)

        # 创建并配置树形图标 (透明背景，选中时与行背景融为一体)
        self._tree_icons = []
        # 即使没有PIL也创建图标
        for img in (_create_folder_closed_icon(), _create_folder_open_icon(), _create_link_icon()):
            self._tree_icons.append(img)
        self.treeView.tag_configure('folder-closed', image=self._tree_icons[0])
        self.treeView.tag_configure('folder-open', image=self._tree_icons[1])
        self.treeView.tag_configure('link', image=self._tree_icons[2])

        self.treeView.bind('<Double-1>', lambda e: self.logon_on())
        self.treeView.bind('<Return>', lambda e: self.logon_on())
        self.treeView.bind('<Button-3>', self._context_menu)
        self.treeView.bind('<<TreeviewOpen>>', self._on_expand)
        self.treeView.bind('<<TreeviewClose>>', self._on_collapse)

        self.update_idletasks()
        center_window(self, 531, 560)
        self.deiconify()

    def set_tree(self):
        self._clear_tree()
        self.set_node('')

    def _clear_tree(self):
        for item in self.treeView.get_children():
            self.treeView.delete(item)

    def set_node(self, parent_iid, info=None):
        if info is None:
            childs_f = self.db.session.query(Node).order_by(Node.node).filter(
                Node.type == 'F', Node.group == '').all()
            childs_l = self.db.session.query(Node).order_by(Node.node).filter(
                Node.type == 'L', Node.group == '').all()
            for folder in childs_f:
                iid = str(folder.uuid)
                folder_tag = 'folder-open' if folder.expanded else 'folder-closed'
                self.treeView.insert(parent_iid, 'end', iid=iid, text=folder.node,
                                    values=(folder.desc, str(folder.uuid), folder.type),
                                    tags=(folder_tag,))
                if folder.expanded:
                    self.treeView.item(iid, open=True)
                self.set_node(iid, folder)
            for link in childs_l:
                iid = str(link.uuid)
                self.treeView.insert(parent_iid, 'end', iid=iid, text=link.node,
                                    values=(link.desc, str(link.uuid), link.type),
                                    tags=('link',))
        else:
            childs_f = self.db.session.query(Node).order_by(Node.node).filter(
                Node.type == 'F', Node.puuid == info.uuid).all()
            childs_l = self.db.session.query(Node).order_by(Node.node).filter(
                Node.type == 'L', Node.puuid == info.uuid).all()
            for folder in childs_f:
                iid = str(folder.uuid)
                folder_tag = 'folder-open' if folder.expanded else 'folder-closed'
                self.treeView.insert(parent_iid, 'end', iid=iid, text=folder.node,
                                    values=(folder.desc, str(folder.uuid), folder.type),
                                    tags=(folder_tag,))
                if folder.expanded:
                    self.treeView.item(iid, open=True)
                self.set_node(iid, folder)
            for link in childs_l:
                iid = str(link.uuid)
                self.treeView.insert(parent_iid, 'end', iid=iid, text=link.node,
                                    values=(link.desc, str(link.uuid), link.type),
                                    tags=('link',))

    def _context_menu(self, event):
        item = self.treeView.identify_row(event.y)
        
        # 清除当前选择，确保在空白处右键时不会影响之前的选中项
        self.treeView.selection_set('')
        self.treeView.focus('')
        
        if item:
            # 如果点击的是某个项目，则设置该项目为选中状态
            self.treeView.selection_set(item)
            self.treeView.focus(item)
            
            values = self.treeView.item(item, 'values')
            nodetype = values[2] if values else ''

            menu = tk.Menu(self, tearoff=0)
            if nodetype == 'L':
                menu.add_command(label='登录', command=self.logon_on)
                menu.add_separator()
                menu.add_command(label='删除', command=self.delete)
                menu.add_separator()
                menu.add_command(label='属性', command=self.attribute)
            else:
                menu.add_command(label='添加新连接', command=self.add_link)
                menu.add_separator()
                menu.add_command(label='添加分组', command=self.add_group)
                if nodetype == 'F':
                    menu.add_separator()
                    menu.add_command(label='删除', command=self.delete)
                    menu.add_separator()
                    menu.add_command(label='属性', command=self.attribute)
        else:
            # 在空白区域右键，提供添加分组和添加新连接的选项
            menu = tk.Menu(self, tearoff=0)
            # menu.add_separator()
            menu.add_command(label='添加分组', command=self.add_group)

        menu.tk_popup(event.x_root, event.y_root)

    def logon_on(self):
        import subprocess

        sel = self.treeView.selection()
        if not sel:
            return
        item = sel[0]
        values = self.treeView.item(item, 'values')
        if not values or values[2] == 'F':
            return

        cur_uuid = values[1]
        uuid = PUUID.UUID(cur_uuid)
        db_link = self.db.session.query(Link).filter(Link.uuid == uuid).first()
        if db_link:
            db_cfg_path = self.db.session.query(Config).filter(Config.key == 'path').first()
            if not db_cfg_path or db_cfg_path.value == '':
                message.error('错误', '请维护菜单->选项->配置后登录！')
                self.config()
                return
            if not self.guiCfg.checkSapGuiDir(db_cfg_path.value):
                message.error('错误', 'saplogon.exe 路径错误，请修改配置！')
                return
            if db_link.system.find(' ') != -1:
                msg = 'SAP系统连接<' + db_link.system + '>存在空格，请调整后重试。'
                message.error('错误', msg)
                return

            user = '-user=' + db_link.user
            pw = '-pw=' + db_link.password
            language = '-language=' + db_link.language
            SYSTEM = '-SYSTEM='
            CLIENT = '-CLIENT=' + db_link.client
            sysname = '-sysname=' + db_link.system
            shcut_app = db_cfg_path.value + '/' + GuiCfg().appName
            maxgui = '-max'

            try:
                subprocess.run([shcut_app, user, pw, language, SYSTEM, CLIENT, sysname, maxgui])
            except Exception:
                message.error('错误', 'GUI配置异常，请调整后重试。')

    def config(self):
        dialog = DialogCfg(self)
        code = dialog.result['code']
        data = dialog.result['data']
        if code == 'ok':
            self.db.session.query(Config).filter(Config.key == 'path').delete()
            self.db.session.add(Config(key='path', value=data['path']))
            self.db.session.commit()

    def add_link(self):
        sel = self.treeView.selection()
        if not sel:
            return
        item = sel[0]
        values = self.treeView.item(item, 'values')
        text = self.treeView.item(item, 'text')
        group = {
            'node': text,
            'desc': values[0] if values else '',
            'uuid': values[1] if values else '',
            'type': values[2] if values else '',
        }
        param = {'type': 'add', 'curGroup': group}
        dialog = DialogLink(self, param)
        code = dialog.result['code']
        data = dialog.result['data']

        if code == 'ok':
            uuid = PUUID.uuid1()
            puuid_str = data['puuid']
            puuid = PUUID.UUID(puuid_str) if puuid_str else None
            nodes = [Node(node=data['node'], desc=data['desc'], group=data['group'],
                         type='L', position=0, uuid=uuid, puuid=puuid)]
            links = [Link(uuid=uuid, node=data['node'], system=data['system'],
                         client=data['client'], user=data['user'], password=data['password'],
                         language=data['language'])]
            self.db.session.add_all(nodes)
            self.db.session.add_all(links)
            self.db.session.commit()

            parent_iid = '' if data['group'] == '' else str(data.get('puuid', ''))
            new_iid = str(uuid)
            self.treeView.insert(parent_iid, 'end', iid=new_iid, text=data['node'],
                                values=(data['desc'], str(uuid), 'L'), tags=('link',))

    def attribute(self):
        sel = self.treeView.selection()
        if not sel:
            return
        item = sel[0]
        values = self.treeView.item(item, 'values')
        text = self.treeView.item(item, 'text')
        nodetype = values[2] if values else ''

        if nodetype == 'F':
            group = {'node': text, 'desc': values[0], 'uuid': values[1], 'type': nodetype}
            param = {'type': 'attribute', 'group': group}
            dialog = DialogGroup(self, param)
            code = dialog.result['code']
            data = dialog.result['data']
            if code == 'ok':
                db_group = self.db.session.query(Node).filter(
                    Node.uuid == PUUID.UUID(data['uuid'])).first()
                db_group.node = data['node']
                db_group.desc = data['desc']
                self.db.session.commit()
                self.treeView.item(item, text=data['node'], values=(data['desc'], data['uuid'], 'F'))
        else:
            cur_uuid = values[1]
            db_node = self.db.session.query(Node).filter(Node.uuid == PUUID.UUID(cur_uuid)).first()
            db_link = self.db.session.query(Link).filter(Link.uuid == PUUID.UUID(cur_uuid)).first()
            link = {
                'node': text, 'desc': values[0], 'uuid': cur_uuid, 'type': nodetype,
                'system': db_link.system, 'client': db_link.client, 'user': db_link.user,
                'password': db_link.password, 'language': db_link.language,
                'group': db_node.group
            }
            param = {'type': 'attribute', 'link': link}
            dialog = DialogLink(self, param)
            code = dialog.result['code']
            data = dialog.result['data']
            if code == 'ok':
                db_node = self.db.session.query(Node).filter(Node.uuid == PUUID.UUID(cur_uuid)).first()
                if db_node.group == data['group']:
                    self.treeView.item(item, text=data['node'],
                                       values=(data['desc'], cur_uuid, 'L'))
                else:
                    self.treeView.delete(item)
                    parent_iid = str(data['puuid'])
                    new_iid = str(cur_uuid)
                    self.treeView.insert(parent_iid, 'end', iid=new_iid, text=data['node'],
                                        values=(data['desc'], cur_uuid, 'L'), tags=('link',))

                db_node.node = data['node']
                db_node.desc = data['desc']
                db_node.group = data['group']
                db_node.puuid = PUUID.UUID(data['puuid'])
                db_link.node = data['node']
                db_link.system = data['system']
                db_link.client = data['client']
                db_link.user = data['user']
                db_link.password = data['password']
                db_link.language = data['language']
                self.db.session.commit()

    def add_group(self):
        param = {'type': 'add'}
        dialog = DialogGroup(self, param)
        code = dialog.result['code']
        data = dialog.result['data']
        if code == 'ok':
            uuid = PUUID.uuid1()
            nodes = [Node(node=data['node'], desc=data['desc'], group='',
                         type='F', position=0, uuid=uuid)]
            self.db.session.add_all(nodes)
            self.db.session.commit()

            iid = str(uuid)
            self.treeView.insert('', 'end', iid=iid, text=data['node'],
                                values=(data['desc'], str(uuid), 'F'), tags=('folder-closed',))

    def add_group_empty(self):
        """在空白区域右键添加分组"""
        param = {'type': 'add'}
        dialog = DialogGroup(self, param)
        code = dialog.result['code']
        data = dialog.result['data']
        if code == 'ok':
            uuid = PUUID.uuid1()
            nodes = [Node(node=data['node'], desc=data['desc'], group='',
                         type='F', position=0, uuid=uuid)]
            self.db.session.add_all(nodes)
            self.db.session.commit()

            iid = str(uuid)
            self.treeView.insert('', 'end', iid=iid, text=data['node'],
                                values=(data['desc'], str(uuid), 'F'), tags=('folder-closed',))

    def delete(self):
        sel = self.treeView.selection()
        if not sel:
            return
        item = sel[0]
        values = self.treeView.item(item, 'values')
        nodetype = values[2]
        cur_uuid = values[1]

        if nodetype == 'F':
            result = message.warning('注意', '确定删除选中的分组？')
            if not result:
                return
            db_links = self.db.session.query(Node).filter(Node.puuid == PUUID.UUID(cur_uuid)).all()
            for link in db_links:
                self.db.session.query(Link).filter(Link.uuid == link.uuid).delete()
            self.db.session.query(Node).filter(Node.uuid == PUUID.UUID(cur_uuid)).delete()
            self.db.session.commit()
        else:
            result = message.warning('注意', '确定删除选中的连接？')
            if not result:
                return
            self.db.session.query(Node).filter(Node.uuid == PUUID.UUID(cur_uuid)).delete()
            self.db.session.query(Link).filter(Link.uuid == PUUID.UUID(cur_uuid)).delete()
            self.db.session.commit()

        self.treeView.delete(item)

    def exit(self):
        self.quit()
        self.destroy()

    def about(self):
        msg = ('👉 一次配置，即可免密登录SAP Logon\n'
               '😈 Bug只是一个未定义的特性...\n\n\n'
               'V2.26.02.97 Tkinter重构！  By Jimmy Ma')
        message.about('关于Z Logon', msg=msg)

    def _on_expand(self, event):
        if self.init:
            return
        item = self.treeView.focus()
        if not item:
            return
        values = self.treeView.item(item, 'values')
        if not values or values[2] != 'F':
            return
        self.treeView.item(item, tags=('folder-open',))
        cur_uuid = values[1]
        db_group = self.db.session.query(Node).filter(Node.uuid == PUUID.UUID(cur_uuid)).first()
        if db_group:
            db_group.expanded = True
            self.db.session.commit()

    def _on_collapse(self, event):
        if self.init:
            return
        item = self.treeView.focus()
        if not item:
            return
        values = self.treeView.item(item, 'values')
        if not values or values[2] != 'F':
            return
        self.treeView.item(item, tags=('folder-closed',))
        cur_uuid = values[1]
        db_group = self.db.session.query(Node).filter(Node.uuid == PUUID.UUID(cur_uuid)).first()
        if db_group:
            db_group.expanded = False
            self.db.session.commit()
