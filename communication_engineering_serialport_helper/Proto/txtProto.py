import re
from Proto import CRC16RTU

class TxtProto():
    def __init__(self, pwd='00000000'):
        self.pwd = pwd
        self.ecodes = {'ERROR':'ERROR', 'NO_DATA':'NO_DATA', 'CRC_ERROR':'CRC_ERROR'}
        self.codes = {'OK':'OK'}
        self.crc16 = CRC16RTU.Crc16()
    
    #Returns a array of command name and command parameters, use for: 'command=param1;param2;param3;paramX'
    def parse(self, respond):
        try:
            data = re.search('.+', respond).group(0)
        except Exception:
            data = ''
        if len(data) == 0:
            return ['NO_DATA']
        raw_answer = data[:-4]
        raw_crc = bytes.fromhex(data[-4:])
        crc = self.crc16.makeCRC16(raw_answer)                        
        if crc == raw_crc:
            #return re.split('([^;=]+)', raw_answer)
            return re.split('\=|;', raw_answer)
        else:            
            return ['CRC_ERROR']
    
    def parse_rdiagn(self, respond):
        data = respond        
        if len(data) == 0:
            return ['NO_DATA']
        raw_answer = data[:-4]
        try:
            raw_crc = bytes.fromhex(data[-4:])
        except Exception:
            return ['CRC_ERROR']
        crc_string = ''
        for item in re.findall('[^\r\n]+', raw_answer):
            crc_string = crc_string + item
        crc = self.crc16.makeCRC16(crc_string)                        
        if crc == raw_crc and raw_answer != 'ERROR':
            rdiagn = {}
            try:
                rdiagn['dev'] = re.findall('^(.*)', raw_answer)[0]
            except Exception:
                rdiagn['dev'] = None
            try:
                rdiagn['fwrev'] = re.search('FWREV=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['fwrev'] = None
            try:
                rdiagn['ops'] = re.search('OPS=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['ops'] = None
            try:
                rdiagn['scid'] = re.search('SCID=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['scid'] = None
            try:
                rdiagn['imei'] = re.search('IMEI=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['imei'] = None
            try:
                rdiagn['reg'] = re.search('\nREG=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['reg'] = None
            try:
                rdiagn['df1'] = re.search('DF1=(\w+)', raw_answer).group(1)
            except Exception:
                rdiagn['df1'] = None
            try:
                rdiagn['df2'] = re.search('DF2=(\w+)', raw_answer).group(1)
            except Exception:
                rdiagn['df2'] = None
            try:
                rdiagn['hw_info'] = re.search('HW_INFO=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['hw_info'] = None
            try:
                rdiagn['fram'] = re.search('FRAM=(.+)', raw_answer).group(1)
            except Exception:
                rdiagn['fram'] = None            
            return ['OK', rdiagn]
        elif crc == raw_crc and raw_answer == 'ERROR':
            return re.split('\=|;', raw_answer)
        else:            
            return ['CRC_ERROR']
    
        #Template for old commands
    def parse_old(self, respond):
        try:
            data = re.search('.+', respond).group(0)
        except Exception:
            data = ''
        if len(data) == 0:
            return ['NO_DATA']
        raw_answer = data[:-4]
        raw_crc = bytes.fromhex(data[-4:])
        crc = self.crc16.makeCRC16(raw_answer)        
        if crc == raw_crc:
            return re.findall('([^:.\s=]+)', raw_answer)
        else:            
            return ['CRC_ERROR']
        

    def make_old(self, command):
        return
    
    #making command from array
    def make(self, *command):
        command_str = ''
        i = 1
        if command[1] == None:
            command_str = str(command[0])
        else:
            for param in command:
                if i == 1:
                    command_str = command_str + str(param) + '='
                    i += 1
                elif i < (len(command) - command.count(None)):
                    if param != None:
                        command_str = command_str + str(param) + ';'
                        i += 1
                else:
                    if param != None:
                        command_str = command_str + str(param)

        command_str = self.pwd + ',' + command_str
        crc = self.crc16.makeCRC16(command_str)        
        return command_str + crc.hex()
   
