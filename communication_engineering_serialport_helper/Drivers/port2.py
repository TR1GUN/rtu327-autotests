from Drivers import serialPort
from Settings import setup

class Port:
    def __init__(self, portnum = None, terminate = 'b\x0a\x0a'):
        self.settings = setup.Settings()
        self.terminate = terminate
        if portnum == None:
            self.com = serialPort.SerialPort(portnum = self.settings.port) # ????????
        else:
            self.com = serialPort.SerialPort(portnum = portnum)
  
    def sendcommand(self, command): #this method does NOT close COM after writing!
        if self.com.isOpen() == False:
            self.com.open()       
        request = command.encode('ASCII') + self.terminate    
        self.com.write(request)    

    def readanswer(self, timeout=5): #this method does not close COM after reading!
        if self.com.isOpen() == False:
            self.com.open()
        answer = self.com.read_data(timeout)
        try:    
            return answer[:-2].decode('ASCII', 'replace')
        except Exception:
            return ''

    def sendRecieve(self, command, timeout = 5): #this method closes COM
        if self.com.isOpen() == False:
            self.com.open()
        request = command.encode('ASCII') + self.terminate    
        self.com.write(request)
        answer = self.com.read_data(timeout)
        self.portclose()
        try:    
            return answer[:-2].decode('ASCII', 'replace')
        except Exception:
            return ''

    def portflush(self, timeout=5):
        if self.com.isOpen() == False:
            self.com.open()
        self.com.read_data_flush(timeout)
        self.portclose()


    def portclose(self):
        if self.com.isOpen() == True:
            self.com.close()
