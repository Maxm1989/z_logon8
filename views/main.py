import uuid as PUUID
import subprocess
import tkinter as tk
from tkinter import ttk

from views.config import DialogCfg
from views.link import DialogLink
from views.group import DialogGroup
from libs.Model import Node, Link, Config
from libs.guiCfg import GuiCfg
from libs.gui_util import center_window, get_icon_path
from libs.OptionDB import sqliteDB
from libs.icon_drawing import create_folder_closed_icon, create_folder_open_icon, create_link_icon
from libs import message


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
        # 确保主窗口获得焦点
        self.focus_force()
        self.treeView.focus_set()

    def _setup_ui(self):
        self.withdraw()
        self.title("Z Logon")
        self.geometry("531x560")
        self.resizable(False, False)

        try:
            self.iconbitmap(get_icon_path())
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
        for img in (create_folder_closed_icon(), create_folder_open_icon(), create_link_icon()):
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
        # 默认选择第一个项目并设置焦点
        self.after(50, self._select_first_item)

    def _select_first_item(self):
        """延迟选择第一个项目，确保树形控件已完全初始化"""
        children = self.treeView.get_children()
        if children:
            first_item = children[0]
            self.treeView.selection_set(first_item)
            self.treeView.focus_set()
            self.treeView.focus(first_item)

    def _clear_tree(self):
        for item in self.treeView.get_children():
            self.treeView.delete(item)

    def set_node(self, parent_iid, info=None):
        # 获取当前父节点下的文件夹和链接，然后合并排序再插入
        if info is None:
            parent_filter = None
        else:
            parent_filter = info.uuid

        childs_f = self.db.session.query(Node).filter(
            Node.type == 'F', Node.puuid == parent_filter).all()
        childs_l = self.db.session.query(Node).filter(
            Node.type == 'L', Node.puuid == parent_filter).all()

        items = []
        for f in childs_f:
            items.append({'type': 'F', 'node': f.node, 'desc': f.desc, 'uuid': f.uuid, 'expanded': f.expanded})
        for l in childs_l:
            items.append({'type': 'L', 'node': l.node, 'desc': l.desc, 'uuid': l.uuid})

        # 文件夹优先，随后按名称忽略大小写排序
        items.sort(key=lambda x: (0 if x['type'] == 'F' else 1, x['node'].lower()))

        for it in items:
            iid = str(it['uuid'])
            if it['type'] == 'F':
                # 启动时（self.init 为 True）强制展开，避免默认折叠
                expanded_flag = it.get('expanded') or getattr(self, 'init', False)
                folder_tag = 'folder-open' if expanded_flag else 'folder-closed'
                self.treeView.insert(parent_iid, 'end', iid=iid, text=it['node'],
                                    values=(it.get('desc', ''), str(it['uuid']), 'F'),
                                    tags=(folder_tag,))
                if expanded_flag:
                    self.treeView.item(iid, open=True)
                # 递归渲染子节点
                try:
                    child_node = self.db.session.query(Node).filter(Node.uuid == it['uuid']).first()
                except Exception:
                    child_node = None
                self.set_node(iid, child_node)
            else:
                self.treeView.insert(parent_iid, 'end', iid=iid, text=it['node'],
                                    values=(it.get('desc', ''), str(it['uuid']), 'L'),
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
                if data.get('puuid'):
                    try:
                        db_node.puuid = PUUID.UUID(data['puuid'])
                    except (ValueError, TypeError):
                        pass
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
               'V2.26.02.10 Tkinter重构！  By Jimmy Ma')
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

