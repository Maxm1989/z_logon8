from dataclasses import dataclass, field, asdict
from typing import Optional
from uuid import UUID


@dataclass
class Node:
    """数据库节点表模型"""
    node: str = ""
    desc: str = ""
    group: str = ""
    type: str = ""  # 'F' for folder, 'L' for link
    position: int = 0
    uuid: Optional[UUID] = None
    puuid: Optional[UUID] = None
    expanded: bool = False
    id: Optional[int] = None

    def __hash__(self):
        return hash(self.id) if self.id else hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id if self.id and other.id else self.uuid == other.uuid


@dataclass
class Link:
    """数据库连接表模型"""
    uuid: Optional[UUID] = None
    node: str = ""
    system: str = ""
    client: str = ""
    user: str = ""
    password: str = ""
    language: str = ""
    id: Optional[int] = None

    def __hash__(self):
        return hash(self.id) if self.id else hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Link):
            return False
        return self.id == other.id if self.id and other.id else self.uuid == other.uuid


@dataclass
class Config:
    """数据库配置表模型"""
    key: str = ""
    value: str = ""
    id: Optional[int] = None

    def __hash__(self):
        return hash(self.id) if self.id else hash(self.key)

    def __eq__(self, other):
        if not isinstance(other, Config):
            return False
        return self.key == other.key


# 用于兼容SQLAlchemy的Base类（空实现）
class Base:
    """用于兼容现有代码"""
    pass
