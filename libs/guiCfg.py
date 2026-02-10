import json
import xml.etree.ElementTree as ET
import os


class GuiCfg:

    def __init__(self):
        self.sapGuiCommDir = os.path.expanduser('~') + r'\AppData\Roaming\SAP\Common'
        self.appName = 'sapshcut.exe'

    def getSapGuiLogonConfig(self):
        pathStr = self.sapGuiCommDir + r'/SAPUILandscape.xml'
        systems = self.parseSapGuiLogonXml(pathStr)
        return sorted(systems, key=lambda x: x["system"], reverse=False)

    def parseSapGuiLogonXml(self, filePath):
        """使用xml.etree替代xmltodict，减少依赖体积"""
        try:
            tree = ET.parse(filePath)
            root = tree.getroot()
            systems = []
            
            # 查找Services下的所有Service元素
            services = root.find('.//Services')
            if services is not None:
                for service in services.findall('Service'):
                    if service.get('type') == 'SAPGUI':
                        systems.append({
                            'system': service.get('name')
                        })
            
            return systems
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return []

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
