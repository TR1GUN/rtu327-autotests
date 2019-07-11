from Drivers import port2
from Drivers import logger
from Proto import txtProto
from datetime import datetime
import time


class Action:
    def __init__(self, answer_command, test_name, pwd, write_command=None, read_command=None, timeout=5):
        self.answer_command = answer_command
        self.test_name = test_name
        self.pwd = pwd
        self.write_command = write_command
        self.read_command = read_command
        self.log = logger.Log(self.answer_command, self.test_name)        
        self.proto = txtProto.TxtProto(pwd = self.pwd)
        self.port = port2.Port()
        self.timeout = timeout
        
    def __write_read__(self, request):
        success = False #command done
        retry = 0 #retry counter
        while not success and retry < 3:
            retry += 1
            time.sleep(0.03)            
            rqtime = str(datetime.now().time().isoformat())
            raw_data = self.port.sendRecieve(request, self.timeout)            
            answtime = str(datetime.now().time().isoformat())            
            self.log.write_log(request, raw_data, rqtime, answtime)
            if len(raw_data) != 0:
                success = True
            else:
                print('\r\n\r\nWARNING! Retry has been used!')
        return raw_data

    def write_to_device(self, cmd, *params):        
        if len(params) > 1:
            request = self.proto.make(cmd, *params)
        else:
            request = self.proto.make(cmd, params[0])



        raw_data = self.__write_read__(request) #using internal method for retry attempts
        answer = self.proto.parse(raw_data)



        try:
            return [self.proto.codes[answer[0]], answer]
        except Exception:
            try:
                return [self.proto.ecodes[answer[0]], answer]
            except Exception:
                return ['NO_DATA', answer]

    def write_to_device_default (self, *params):
        return self.write_to_device(self.write_command, *params)            

    def write_to_device_counter (self, type, *params):        
        #transopen
        transopen = self.write_to_device('TRANSOPEN', None)
        if transopen[0] != 'OK':
            return transopen
        transadd = self.write_to_device(type, *params)
        if transadd[0] != 'OK':
            transrollback = self.write_to_device('TRANSROLLBACK', None)
            if transrollback[0] != 'OK':
                closesession = self.write_to_device('CLOSESESSION', None)
                return transadd
            else:
                return transadd
        transcommit = self.write_to_device('TRANSCOMMIT', None)
        if transcommit[0] != 'OK':
            transrollback = self.write_to_device('TRANSROLLBACK', None)
            if transrollback[0] != 'OK':
                closesession = self.write_to_device('CLOSESESSION', None)
                return transcommit
            else:
                return transcommit
        else:
            return transcommit
        
    def write_to_device_counters (self, num, commit, type, *params):        
        #transopen
        write_params = [*params]
        transopen = self.write_to_device('TRANSOPEN', None)
        if transopen[0] != 'OK':
            return transopen
        i = 0 #counter

        while i < int(num):
            write_params[0] = int(write_params[0]) + i
            transadd = self.__write_custom__(type, *write_params)
            i+=1
            if transadd[0] != 'OK':
                transrollback = self.write_to_device('TRANSROLLBACK', None)
                if transrollback[0] != 'OK':
                    closesession = self.write_to_device('CLOSESESSION', None)
                    return transadd
                else:
                    return transadd

        if commit == True:
            transcommit = self.write_to_device('TRANSCOMMIT', None)
            if transcommit[0] != 'OK':
                transrollback = self.write_to_device('TRANSROLLBACK', None)
                if transrollback[0] != 'OK':
                    closesession = self.write_to_device('CLOSESESSION', None)
                    return transcommit
                else:
                    return transcommit
            else:
                return transcommit
        else:
            return transadd
        
    def read_from_device(self, cmd, *params):
        if len(params) > 1:
            request = self.proto.make(cmd, *params)
        else:
            request = self.proto.make(cmd, params[0])
        
        raw_data = self.__write_read__(request)
        answer = self.proto.parse(raw_data)
        if answer[0] == self.answer_command:
            return ['OK', answer]
        else:
           try:
               return [self.proto.ecodes[answer[0]], answer]
           except Exception:
                return ['NO_DATA', answer]

    def read_from_device_default(self, *params):
        return self.read_from_device(self.read_command, *params)

    def read_from_device_old (self, cmd, *params):        
        if len(params) > 1:
            request = self.proto.make(cmd, *params)
        else:
            request = self.proto.make(cmd, params[0])
        raw_data = self.__write_read__(request)
        answer = self.proto.parse_old(raw_data)        
        if answer[0] == self.answer_command:
            return ['OK', answer]
        else:
           try:
               return [self.proto.ecodes[answer[0]], answer]
           except Exception:
                return ['NO_DATA', answer]

    def read_from_device_old_default(self, *params):
        return self.read_from_device_old(self.read_command, *params)

    def read_from_device_rdiagn (self, *params):
        #default_timeout = self.timeout
        #port.com.timeout = 1
        if len(params) > 1:
            request = self.proto.make(self.read_command, *params)
        else:
            request = self.proto.make(self.read_command, params[0])
        raw_data = self.__write_read__(request)
        answer = self.proto.parse_rdiagn(raw_data)
        #port.com.timeout = default_timeout
        if len(answer[0]) > 0 and answer[0] != 'ERROR' and answer[0] != 'CRC_ERROR':
            return answer
        else:
           try:
               return [self.proto.ecodes[answer[0]], answer]
           except Exception:
                return ['NO_DATA', answer]

    def defaultconfig(self, *params):
        if len(params) > 1:
            defaults = self.write_to_device('DEFAULTCONFIG', *params)
        else:
            defaults = self.write_to_device('DEFAULTCONFIG', params[0])
        if defaults[0] == 'OK':
            self.proto.pwd = '00000000'
            self.port.portflush(20)
            timer = time.time() + 340            
            time.sleep(60)
            fw_boot = False
            rname = self.proto.make('RNAME', None)
            while fw_boot == False and time.time() < timer:
                raw_data = self.__write_read__(rname)
                answer = self.proto.parse(raw_data)                                
                if answer[0] == 'NAME':
                    fw_boot = True
            if fw_boot == False:
                print('\n\nWARNING! RESET FAILED!\n')
                return ['ERROR']
            #reset passwords            
            return self.__reset_passwords__()
        else:
            return defaults
    
    def __reset_passwords__(self):
        pwd_backup = self.proto.pwd
        self.proto.pwd = '00000000'            
        spass1 = self.write_to_device('SPASS1', self.port.settings.pwd1)
        spass2 = self.write_to_device('SPASS2', self.port.settings.pwd2)
        spass3 = self.write_to_device('SPASS3', self.port.settings.pwd3)
        self.proto.pwd = pwd_backup
        if spass1[0] == 'OK' and spass2[0] == 'OK' and spass3[0] == 'OK':               
           print('\n\nPWD RESET OK')               
           return ['OK']
        else:
           print('\n\nPWD RESET ERROR')
           return ['ERROR']        

    def reboot_to_fw(self):
        self.port.com.baudrate = 115200
        self.port.com.timeout = 0.8
        hello_cmd = b'\x00\x01\xC0\x70'
        auth_cmd = b'\x05\x01\x12\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x06\x62'
        set_block_len_cmd = b'\x02\x00\x04\xd1\xc3'
        reboot_cmd = b'\x0F\x02\x85\x81'
        commands = [hello_cmd, auth_cmd, set_block_len_cmd, reboot_cmd]
        i = 0 #counter
        retry = 0 #counter2
        while i <= 3 and retry < 3:
            time.sleep(0.03)
            rqtime = str(datetime.now().time().isoformat())
            self.port.com.write(commands[i])
            answ = self.port.com.read_data()
            answtime = str(datetime.now().time().isoformat())
            self.log.write_log(str(commands[i]), str(answ), rqtime, answtime)
            if answ[0] != b'\x01' and len(answ) > 0:
                i+=1
                status = 'OK'
            elif answ[0] == b'\x01':
                status = 'ERROR'
                retry+=1
            else:
                status = 'NO_DATA'
                retry+=1
            
        self.port.com.baudrate = 9600
        self.port.com.timeout = 0.3
        return [status]
              

    def tranzit_off (self, speed='6', length='8', parity='0', stop='0'):
        speed_dict = {'1':300, '2':600, '3': 1200, '4':2400, '5':4800, '6': 9600, '7':19200, '8':38400, '9':57600, '10':115200}
        length_dict = {'5':5, '6':6, '7':7, '8':8}
        parity_dict = {'0':'N', '1':'E', '2':'O'}
        stop_dict = {'0':1, '1':2}
        self.port.com.baudrate = speed_dict[speed]
        self.port.com.bytesize = length_dict[length]
        self.port.com.parity = parity_dict[parity]
        self.port.com.stopbits = stop_dict[stop]
        self.port.com.timeout = 0.8
        success = False
        retry = 0
        while retry < 15 and not success:
            time.sleep(0.03)
            rqtime = str(datetime.now().time().isoformat())
            self.port.CSDConnect.sendcommand('TRANZIT_OFF')
            raw_data = self.port.readanswer(self.timeout)
            answtime = str(datetime.now().time().isoformat())
            self.log.write_log('TRANZIT_OFF', raw_data, rqtime, answtime)
            if len(raw_data) > 6:
                raw_data = raw_data[-6:]
            try:
                answer = self.proto.parse(raw_data)
            except Exception:
                answer = ['CRC_ERROR']
            if answer[0] == 'OK':
                success = True
            else:
                retry+=1

        self.port.com.baudrate = 9600
        self.port.com.bytesize = 8
        self.port.com.parity = 'N'
        self.port.com.stopbits = 1
        self.port.com.timeout = 0.3        
        
        try:
            return [self.proto.codes[answer[0]], answer]
        except Exception:
            try:
                return [self.proto.ecodes[answer[0]], answer]
            except Exception:
                return ['NO_DATA', answer]
        
