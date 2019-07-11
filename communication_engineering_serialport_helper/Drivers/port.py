from communication_engineering_serialport_helper.Drivers import serialPort
from communication_engineering_serialport_helper.Settings import setup

settings = setup.Settings()
com = serialPort.SerialPort(portnum=settings.port)


def sendcommand(command):  # this method does NOT close COM after writing!
    if com.isOpen() == False:
        com.open()
    request = command.encode('ASCII') + b'\x0a\x0a'
    com.write(request)


def readanswer(timeout=5):  # this method does not close COM after reading!
    if com.isOpen() == False:
        com.open()
    answer = com.read_data(timeout)
    try:
        return answer[:-2].decode('ASCII', 'replace')
    except Exception:
        return ''


# def portopen(com=None):
def portopen(com=com):
    if com.isOpen() == False:
        com.open()


def portclose(com=com):
    if com.isOpen() == True:
        com.close()


