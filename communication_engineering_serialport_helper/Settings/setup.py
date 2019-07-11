from xml.dom import minidom
import os
xmldoc = minidom.parse(os.path.join('communication_engineering_serialport_helper','Settings', 'settings.xml'))

class Settings:
    def     __init__(self):
        self.reload()

    def reload(self):
        xmldoc = minidom.parse(os.path.join('communication_engineering_serialport_helper','Settings', 'settings.xml'))
        self.port = self.getValue('port') #read COM port from SETUP file 
        self.pwd1 = self.getValue('pwd1')
        self.pwd2 = self.getValue('pwd2')
        self.pwd3 = self.getValue('pwd3')
        self.pwde = self.getValue('pwde')
        self.swver = self.getValue('swver')
        self.hwver = self.getValue('hwver')
        self.blver = self.getValue('blver')
        self.dev = self.getValue('dev')
        self.modem_name = self.getValue('modem_name')
        self.modem_model = self.getValue('modem_model')       
        self.ifaces = self.getValue('ifaces')
        self.di_inputs = self.getValue('di_inputs')
        self.pls = self.getValue('pls')
        self.real_time = self.getValue('real_time')
        self.UMTS = self.getValue('UMTS')
        self.dev_type = self.getValue('dev_type')
        self.df1 = self.getValue('df1')
        self.df2 = self.getValue('df2')
        self.fram = self.getValue('FRAM')
        self.scid = self.getValue('SCID')
        self.hw_info = self.getValue('HW_INFO')
        self.ops = self.getValue('OPS')
        self.imei = self.getValue('imei')

    def getValue(self, tag):
        try:
            val = str(xmldoc.getElementsByTagName(tag)[0].firstChild.data)
        except Exception:
            val = None
        return val

    def setValue(self, tag, val):
        if xmldoc.getElementsByTagName(tag)[0].firstChild == None:
            if val == None or val == '':
                pass
            else:
                data = xmldoc.createTextNode(val)
                xmldoc.getElementsByTagName(tag)[0].appendChild(data)
        else:
            if val == None or val == '':
                xmldoc.getElementsByTagName(tag)[0].removeChild(xmldoc.getElementsByTagName(tag)[0].firstChild)
            else:
                xmldoc.getElementsByTagName(tag)[0].firstChild.data = str(val)

    def saveXml(self):
        xmldoc.writexml(open(os.path.join('Settings', 'settings.xml'),'w'))