from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libs.Model import Node, Link, Config, Base
from libs.guiCfg import GuiCfg
import os


class sqliteDB:
    def __init__(self):
        self.dbname = 'zlogon.db'
        self.dbpath = GuiCfg().sapGuiCommDir + '/' + self.dbname
        DB_URI = r'sqlite:///{path}'.format(path=self.dbpath)
        self.engine = create_engine(DB_URI)
        self.base = Base
        self.session = sessionmaker(bind=self.engine)()
        self.checkDB()

    def checkDB(self):
        # 如果没有db文件，创建文件
        if not os.path.exists(self.dbpath):
            # try:
            with open(self.dbpath, 'w', encoding='utf-8') as f:
                # print(f)
                self.createDBTable()
            # except:
            #     message.error('错误', '请安装SAP GUI后使用！')
            #     # QApplication.instance().quit()


    def createDBTable(self):
        self.base.metadata.drop_all(self.engine)
        # self.base.metadata.create_all(self.engine)
        # self.base.metadata.drop_all(self.engine, tables=[Link.__table__])
        self.base.metadata.create_all(self.engine, tables=[Link.__table__])
        self.base.metadata.create_all(self.engine, tables=[Node.__table__])
        self.base.metadata.create_all(self.engine, tables=[Config.__table__])
        self.session.commit()

    def getGroup(self):
        db_group = self.session.query(Node).filter(Node.type == 'F').all()

        group = []
        for list in db_group:
            group.append({
                'group': list.node,
                'uuid': list.uuid
            })
        return group
