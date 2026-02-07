import json
import xmltodict
import os


class GuiCfg:

    def __init__(self):
        self.sapGuiCommDir = os.path.expanduser('~') + r'\AppData\Roaming\SAP\Common'
        self.appName = 'sapshcut.exe'

    def getSapGuiLogonConfig(self):
        pathStr = self.sapGuiCommDir + r'/SAPUILandscape.xml'
        jsonData = self.getXmlFile2JsonData(pathStr)
        sysDict = jsonData.get('Landscape').get('Services')

        systems = []
        for item in sysDict['Service']:
            dict = {}
            if item['@type'] == 'SAPGUI':
                dict['system'] = item['@name']
                # dict['sysname'] = item['@name']
                # dict['SYSTEM'] = item['@systemid']
                systems.append(dict)

        return sorted(systems, key=lambda x: x["system"], reverse=False)

    def getXmlFile2JsonData(self, filePath):
        # 获取xml文件 , encoding='utf-8'
        xmlFile = open(str(filePath), 'r', encoding='utf-8')
        # 读取xml文件内容
        xmlDataStr = xmlFile.read()
        # 将读取的xml内容转为json
        xmlParse = xmltodict.parse(xmlDataStr)
        jsonStr = json.dumps(xmlParse, indent=1)
        jsonData = json.loads(jsonStr)
        return jsonData

    def checkSapGuiDir(self, path=None):
        # def isExist(self, name, path=None):
        '''

        :param name: 需要检测的文件或文件夹名
        :param path: 需要检测的文件或文件夹所在的路径，当path=None时默认使用当前路径检测
        :return: True/False 当检测的文件或文件夹所在的路径下有目标文件或文件夹时返回Ture,
                当检测的文件或文件夹所在的路径下没有有目标文件或文件夹时返回False
        '''

        if path is None:
            path = os.getcwd()
        if os.path.exists(path + '/' + self.appName):
            return True
        else:
            return False
