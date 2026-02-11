import sqlite3
import os
from pathlib import Path
from typing import List, Optional, Any
from uuid import UUID
from libs.Model import Node, Link, Config, Base
from libs.guiCfg import GuiCfg


def escape_column(name: str) -> str:
    """转义 SQL 保留字列名"""
    reserved_words = {
        'group', 'order', 'select', 'from', 'where', 'and', 'or', 'not', 'in', 
        'join', 'left', 'right', 'inner', 'outer', 'on', 'as', 'by', 'limit',
        'offset', 'distinct', 'all', 'any', 'exists', 'between', 'like', 'is',
        'null', 'values', 'insert', 'update', 'delete', 'create', 'drop', 'alter'
    }
    if name.lower() in reserved_words:
        return f'"{name}"'
    return name


class QueryBuilder:
    """SQL查询构建器，用于兼容SQLAlchemy的query接口"""
    
    def __init__(self, db_instance, model_class):
        self.db = db_instance
        self.model_class = model_class
        self.filters = []
        self.order_column = None
        self.order_desc = False
        self.limit_count = None
        
    def filter(self, *conditions):
        """添加过滤条件"""
        for condition in conditions:
            self.filters.append(condition)
        return self
    
    def order_by(self, column):
        """添加排序"""
        if hasattr(column, '__call__'):
            # column是一个属性引用，如Node.node
            self.order_column = column
        return self
    
    def all(self) -> List:
        """执行查询，返回所有结果"""
        return self._execute_query(fetch_all=True)
    
    def first(self) -> Optional[Any]:
        """执行查询，返回第一个结果"""
        results = self._execute_query(fetch_all=False)
        # _execute_query 在 fetch_all=False 时可能直接返回单个对象（而不是列表），
        # 因此需要兼容两种返回类型。
        if isinstance(results, list):
            return results[0] if results else None
        return results
    
    def _execute_query(self, fetch_all=True):
        """执行查询"""
        if self.model_class.__name__ == 'Node':
            return self._query_node(fetch_all)
        elif self.model_class.__name__ == 'Link':
            return self._query_link(fetch_all)
        elif self.model_class.__name__ == 'Config':
            return self._query_config(fetch_all)
        return []
    
    def _query_node(self, fetch_all):
        """查询Node表"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        sql = 'SELECT id, node, desc, "group", type, position, uuid, puuid, expanded FROM node'
        params = []
        where_added = False
        
        # 应用过滤条件
        for condition in self.filters:
            condition_sql, condition_params = self._build_condition(condition, 'node', where_added)
            if condition_sql:
                sql += " " + condition_sql
                params.extend(condition_params)
                where_added = True
        
        # 应用排序
        if self.order_column:
            order_field = self._get_field_name(self.order_column)
            sql += f" ORDER BY {escape_column(order_field)}"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall() if fetch_all else cursor.fetchone()
        
        if not rows:
            return [] if fetch_all else None
        
        if not fetch_all:
            rows = [rows]
        
        results = []
        for row in rows:
            node = Node(
                id=row[0],
                node=row[1],
                desc=row[2],
                group=row[3],
                type=row[4],
                position=row[5],
                uuid=UUID(row[6]) if row[6] else None,
                puuid=UUID(row[7]) if row[7] else None,
                expanded=bool(row[8])
            )
            results.append(node)
        
        conn.close()
        return results if fetch_all else (results[0] if results else None)
    
    def _query_link(self, fetch_all):
        """查询Link表"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT id, uuid, node, system, client, user, password, language FROM link"
        params = []
        where_added = False
        
        # 应用过滤条件
        for condition in self.filters:
            condition_sql, condition_params = self._build_condition(condition, 'link', where_added)
            if condition_sql:
                sql += " " + condition_sql
                params.extend(condition_params)
                where_added = True
        
        # 应用排序
        if self.order_column:
            order_field = self._get_field_name(self.order_column)
            sql += f" ORDER BY {escape_column(order_field)}"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall() if fetch_all else cursor.fetchone()
        
        if not rows:
            return [] if fetch_all else None
        
        if not fetch_all:
            rows = [rows]
        
        results = []
        for row in rows:
            link = Link(
                id=row[0],
                uuid=UUID(row[1]) if row[1] else None,
                node=row[2],
                system=row[3],
                client=row[4],
                user=row[5],
                password=row[6],
                language=row[7]
            )
            results.append(link)
        
        conn.close()
        return results if fetch_all else (results[0] if results else None)
    
    def _query_config(self, fetch_all):
        """查询Config表"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT id, key, value FROM config"
        params = []
        where_added = False
        
        # 应用过滤条件
        for condition in self.filters:
            condition_sql, condition_params = self._build_condition(condition, 'config', where_added)
            if condition_sql:
                sql += " " + condition_sql
                params.extend(condition_params)
                where_added = True
        
        # 应用排序
        if self.order_column:
            order_field = self._get_field_name(self.order_column)
            sql += f" ORDER BY {escape_column(order_field)}"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall() if fetch_all else cursor.fetchone()
        
        if not rows:
            return [] if fetch_all else None
        
        if not fetch_all:
            rows = [rows]
        
        results = []
        for row in rows:
            config = Config(
                id=row[0],
                key=row[1],
                value=row[2]
            )
            results.append(config)
        
        conn.close()
        return results if fetch_all else (results[0] if results else None)
    
    def _build_condition(self, condition, table_name, where_added=False):
        """构建过滤条件SQL和参数"""
        # condition 是形如 (Column == value) 的对象
        if hasattr(condition, '__class__'):
            # 检查是否是比较操作对象
            if hasattr(condition, 'left') and hasattr(condition, 'right') and hasattr(condition, 'operator'):
                # 这是一个自定义的比较对象
                field_name = escape_column(self._get_field_name(condition.left))
                operator = condition.operator
                value = condition.right
                prefix = "AND" if where_added else "WHERE"
                
                if operator == '==':
                    # 处理 NULL 比较
                    if value is None:
                        return f"{prefix} {field_name} IS NULL", []
                    elif isinstance(value, UUID):
                        return f"{prefix} {field_name} = ?", [str(value)]
                    else:
                        return f"{prefix} {field_name} = ?", [value]
                elif operator == '!=':
                    # 处理 NULL 比较
                    if value is None:
                        return f"{prefix} {field_name} IS NOT NULL", []
                    elif isinstance(value, UUID):
                        return f"{prefix} {field_name} != ?", [str(value)]
                    else:
                        return f"{prefix} {field_name} != ?", [value]
        return "", []
    
    def delete(self):
        """执行删除"""
        if self.model_class.__name__ == 'Node':
            self._delete_node()
        elif self.model_class.__name__ == 'Link':
            self._delete_link()
        elif self.model_class.__name__ == 'Config':
            self._delete_config()
    
    def _delete_node(self):
        """删除Node"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        sql = "DELETE FROM node"
        params = []
        where_added = False
        
        for condition in self.filters:
            field_name = escape_column(self._get_field_name(condition.left))
            value = condition.right
            prefix = "AND" if where_added else "WHERE"
            if isinstance(value, UUID):
                sql += f" {prefix} {field_name} = ?"
                params.append(str(value))
            else:
                sql += f" {prefix} {field_name} = ?"
                params.append(value)
            where_added = True
        
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    
    def _delete_link(self):
        """删除Link"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        sql = "DELETE FROM link"
        params = []
        where_added = False
        
        for condition in self.filters:
            field_name = escape_column(self._get_field_name(condition.left))
            value = condition.right
            prefix = "AND" if where_added else "WHERE"
            if isinstance(value, UUID):
                sql += f" {prefix} {field_name} = ?"
                params.append(str(value))
            else:
                sql += f" {prefix} {field_name} = ?"
                params.append(value)
            where_added = True
        
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    
    def _delete_config(self):
        """删除Config"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        sql = "DELETE FROM config"
        params = []
        where_added = False
        
        for condition in self.filters:
            field_name = escape_column(self._get_field_name(condition.left))
            value = condition.right
            prefix = "AND" if where_added else "WHERE"
            sql += f" {prefix} {field_name} = ?"
            params.append(value)
            where_added = True
        
        cursor.execute(sql, params)
        conn.commit()
        conn.close()

    def _get_field_name(self, column):
        """从列对象获取字段名"""
        if hasattr(column, '__name__'):
            return column.__name__
        if hasattr(column, 'name'):
            return column.name
        return str(column)


class FilterCondition:
    """过滤条件对象"""
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value
        self.left = column
        self.right = value


class Column:
    """列对象，模拟SQLAlchemy的Column"""
    def __init__(self, name):
        self.__name__ = name
        self.name = name
    
    def __eq__(self, other):
        return FilterCondition(self, '==', other)
    
    def __ne__(self, other):
        return FilterCondition(self, '!=', other)


class SessionMock:
    """模拟SQLAlchemy的Session对象"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        self._dirty_objects = []
    
    def query(self, model_class):
        """创建查询对象"""
        return QueryBuilder(self.db, model_class)
    
    def add(self, obj):
        """添加对象(延迟执行)"""
        self._mark_dirty(obj)
    
    def add_all(self, objs):
        """批量添加对象(延迟执行)"""
        for obj in objs:
            self._mark_dirty(obj)
    
    def mark_dirty(self, obj):
        """标记对象为脏数据（外部使用接口）"""
        self._mark_dirty(obj)
    
    def _mark_dirty(self, obj):
        """标记对象为脏数据"""
        # 使用对象id作为key，避免重复添加
        obj_id = id(obj)
        if obj_id not in [id(o) for o in self._dirty_objects]:
            self._dirty_objects.append(obj)
    
    def commit(self):
        """提交更改"""
        for obj in self._dirty_objects:
            if isinstance(obj, Node):
                self._commit_node(obj)
            elif isinstance(obj, Link):
                self._commit_link(obj)
            elif isinstance(obj, Config):
                self._commit_config(obj)
        self._dirty_objects.clear()
        
        # 同时处理修改过的对象（直接修改了属性的对象）
        self.db._flush_dirty_objects()
    
    def _commit_node(self, node: Node):
        """提交Node对象"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        if node.id is None:
            # 插入新记录
            cursor.execute("""
                INSERT INTO node (node, desc, "group", type, position, uuid, puuid, expanded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                node.node, node.desc, node.group, node.type, node.position,
                str(node.uuid) if node.uuid else None,
                str(node.puuid) if node.puuid else None,
                1 if node.expanded else 0
            ))
            node.id = cursor.lastrowid
        else:
            # 更新现有记录
            cursor.execute("""
                UPDATE node SET node=?, desc=?, "group"=?, type=?, position=?, puuid=?, expanded=?
                WHERE id=?
            """, (
                node.node, node.desc, node.group, node.type, node.position,
                str(node.puuid) if node.puuid else None,
                1 if node.expanded else 0,
                node.id
            ))
        
        conn.commit()
        conn.close()
    
    def _commit_link(self, link: Link):
        """提交Link对象"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        if link.id is None:
            # 插入新记录
            cursor.execute("""
                INSERT INTO link (uuid, node, system, client, user, password, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(link.uuid) if link.uuid else None,
                link.node, link.system, link.client, link.user, link.password, link.language
            ))
            link.id = cursor.lastrowid
        else:
            # 更新现有记录
            cursor.execute("""
                UPDATE link SET uuid=?, node=?, system=?, client=?, user=?, password=?, language=?
                WHERE id=?
            """, (
                str(link.uuid) if link.uuid else None,
                link.node, link.system, link.client, link.user, link.password, link.language,
                link.id
            ))
        
        conn.commit()
        conn.close()
    
    def _commit_config(self, config: Config):
        """提交Config对象"""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        if config.id is None:
            # 插入新记录
            cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (config.key, config.value))
            config.id = cursor.lastrowid
        else:
            # 更新现有记录
            cursor.execute("UPDATE config SET value=? WHERE id=?", (config.value, config.id))
        
        conn.commit()
        conn.close()


class sqliteDB:
    """SQLite数据库管理类，模拟SQLAlchemy接口"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(sqliteDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化（因为实现了单例）
        if getattr(self, '_initialized', False):
            return
        self.dbname = 'zlogon.db'
        self.dbpath = GuiCfg().sapGuiCommDir + '/' + self.dbname
        self.base = Base
        self.session = SessionMock(self)
        self._dirty_objects = {}  # 存储直接修改的对象
        self.checkDB()
        self._initialized = True
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.dbpath)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _flush_dirty_objects(self):
        """刷新脏数据到数据库"""
        for obj in self._dirty_objects.values():
            if isinstance(obj, Node):
                self._update_node(obj)
            elif isinstance(obj, Link):
                self._update_link(obj)
            elif isinstance(obj, Config):
                self._update_config(obj)
        self._dirty_objects.clear()
    
    def _update_node(self, node: Node):
        """更新Node对象"""
        if node.id is None:
            return
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE node SET node=?, desc=?, "group"=?, type=?, position=?, puuid=?, expanded=?
            WHERE id=?
        """, (
            node.node, node.desc, node.group, node.type, node.position,
            str(node.puuid) if node.puuid else None,
            1 if node.expanded else 0,
            node.id
        ))
        conn.commit()
        conn.close()
    
    def _update_link(self, link: Link):
        """更新Link对象"""
        if link.id is None:
            return
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE link SET node=?, system=?, client=?, user=?, password=?, language=?
            WHERE id=?
        """, (
            link.node, link.system, link.client, link.user, link.password, link.language,
            link.id
        ))
        conn.commit()
        conn.close()
    
    def _update_config(self, config: Config):
        """更新Config对象"""
        if config.id is None:
            return
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE config SET value=? WHERE key=?", (config.value, config.key))
        conn.commit()
        conn.close()
    
    def checkDB(self):
        """检查并创建数据库"""
        if not os.path.exists(self.dbpath):
            Path(self.dbpath).parent.mkdir(parents=True, exist_ok=True)
            with open(self.dbpath, 'w', encoding='utf-8'):
                pass
            self.createDBTable()
    
    def createDBTable(self):
        """创建数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 删除旧表
        cursor.execute("DROP TABLE IF EXISTS link")
        cursor.execute("DROP TABLE IF EXISTS node")
        cursor.execute("DROP TABLE IF EXISTS config")
        
        # 创建node表
        cursor.execute("""
            CREATE TABLE node (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node TEXT,
                desc TEXT,
                "group" TEXT,
                type TEXT,
                position INTEGER,
                uuid TEXT UNIQUE,
                puuid TEXT,
                expanded INTEGER DEFAULT 0
            )
        """)
        
        # 创建link表
        cursor.execute("""
            CREATE TABLE link (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE,
                node TEXT,
                system TEXT,
                client TEXT,
                user TEXT,
                password TEXT,
                language TEXT
            )
        """)
        
        # 创建config表
        cursor.execute("""
            CREATE TABLE config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def getGroup(self):
        """获取所有分组"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT node, uuid FROM node 
            WHERE type = 'F'
            ORDER BY node
        """)
        rows = cursor.fetchall()
        conn.close()
        
        groups = []
        for row in rows:
            groups.append({
                'group': row[0],
                'uuid': row[1]
            })
        return groups


# 为了兼容现有代码，添加列定义
Node.node = Column('node')
Node.desc = Column('desc')
Node.group = Column('group')
Node.type = Column('type')
Node.position = Column('position')
Node.uuid = Column('uuid')
Node.puuid = Column('puuid')
Node.expanded = Column('expanded')
Node.id = Column('id')

Link.uuid = Column('uuid')
Link.node = Column('node')
Link.system = Column('system')
Link.client = Column('client')
Link.user = Column('user')
Link.password = Column('password')
Link.language = Column('language')
Link.id = Column('id')

Config.key = Column('key')
Config.value = Column('value')
Config.id = Column('id')
