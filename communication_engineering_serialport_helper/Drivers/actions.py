from Drivers import port, serialPort
from Drivers import logger
from Drivers.port import settings
from Proto import txtProto
from datetime import datetime
import time

from Utils import helpActions


class Action:
    def     __init__(self, answer_command, test_name, pwd, write_command=None, read_command=None, timeout=5):
        self.answer_command = answer_command
        self.test_name = test_name
        self.pwd = pwd
        self.write_command = write_command
        self.read_command = read_command
        self.log = logger.Log(self.answer_command, self.test_name)        
        self.proto = txtProto.TxtProto(pwd = self.pwd)
        self.timeout = timeout
        
    def __write_read__(self, request,tcp_connect=None):
        success = False #command done
        retry = 0 #retry counter
        while not success and retry < 3:
            retry += 1
            time.sleep(0.03)            
            rqtime = str(datetime.now().time().isoformat())
            raw_data = None
            if tcp_connect:
                old_request_for_logger = request # for log
                request = request.encode('ASCII') + b'\x0a\x0a'
                tcp_connect_array = tcp_connect.split(':')

                # Костыль
                # На данный момент timeout для всех архивных(ARCHPRM, ARCHDEPTH) тестов поставлено 600 сек
                # Для остальных по 30 сек
                #
                # Желательно timeout протянут из вызывающего метода
                #
                # old_request_for_logger берется т.к. работаем со строкой


                while not success and retry < 3:
                    # print(old_request_for_logger)
                    try:
                         if old_request_for_logger.count('ARCHPRM') > 0 or old_request_for_logger.count('ARCHDEPTH') > 0:
                            # print('Архивный тест')
                            raw_data = helpActions.send_command(result_command=request,
                                               tcp_ip=tcp_connect_array[0], tcp_port=tcp_connect_array[1])
                         else:
                            # print('Не архивный тест')
                            raw_data = helpActions.send_command(result_command=request,
                                               tcp_ip=tcp_connect_array[0], tcp_port=tcp_connect_array[1]
                                                        , timeout=30)
                    except:
                        print('TCP RETRY. Number of retry : ' + str(retry))
                    if raw_data is None:
                        retry += 1
                        # continue
                    else:
                        success = True
                request = old_request_for_logger # for log
            else:
                port.sendcommand(request)
                raw_data = port.readanswer(self.timeout)

            answtime = str(datetime.now().time().isoformat())
            self.log.write_log(request, raw_data, rqtime, answtime)
            if len(raw_data) != 0:
                success = True
            else:
                print('\r\n\r\nWARNING! Retry has been used!')
        return raw_data

    def __write_custom__ (self, cmd,*params):
        tcp_connect = None
        if len(params) > 1:
            if params[0].count('--tcp_connect=') > 0:
                tcp_connect = params[0].split('=')[1]
                request = self.proto.make(cmd, *params[1:])
            else:
                request = self.proto.make(cmd, *params)
        else:
            request = self.proto.make(cmd, params[0])

        if tcp_connect: # tcp connect
            raw_data = self.__write_read__(request, tcp_connect)
        else:
            raw_data = self.__write_read__(request) #using internal method for retry attempts
        answer = self.proto.parse(raw_data)

        try:
            return [self.proto.codes[answer[0]], answer]
        except Exception:
            try:
                return [self.proto.ecodes[answer[0]], answer]
            except Exception:
                return ['NO_DATA', answer]

    def write_to_device (self, *params):
        return self.__write_custom__(self.write_command, *params)

    def write_to_device_counter (self, type, *params):
        if len(params) > 1 and params[0].count('--tcp_connect=') > 0:
            transopen = self.__write_custom__('TRANSOPEN', params[0], None)
            if transopen[0] != 'OK':
                return transopen
            transadd = self.__write_custom__(type, *params)
            if transadd[0] != 'OK':
                transrollback = self.__write_custom__('TRANSROLLBACK', params[0],None)
                if transrollback[0] != 'OK':
                    closesession = self.__write_custom__('CLOSESESSION',params[0], None)
                    return transadd
                else:
                    return transadd
            transcommit = self.__write_custom__('TRANSCOMMIT',params[0], None)
            if transcommit[0] != 'OK':
                transrollback = self.__write_custom__('TRANSROLLBACK',params[0], None)
                if transrollback[0] != 'OK':
                    closesession = self.__write_custom__('CLOSESESSION',params[0], None)
                    return transcommit
                else:
                    return transcommit
            else:
                return transcommit
        else:
            transopen = self.__write_custom__('TRANSOPEN', None)
            if transopen[0] != 'OK':
                return transopen
            transadd = self.__write_custom__(type, *params)
            if transadd[0] != 'OK':
                transrollback = self.__write_custom__('TRANSROLLBACK', None)
                if transrollback[0] != 'OK':
                    closesession = self.__write_custom__('CLOSESESSION', None)
                    return transadd
                else:
                    return transadd
            transcommit = self.__write_custom__('TRANSCOMMIT', None)
            if transcommit[0] != 'OK':
                transrollback = self.__write_custom__('TRANSROLLBACK', None)
                if transrollback[0] != 'OK':
                    closesession = self.__write_custom__('CLOSESESSION', None)
                    return transcommit
                else:
                    return transcommit
            else:
                return transcommit




    def write_to_device_counters (self, num, commit, type, *params):        
        #transopen
        write_params = [*params]
        if len(params) > 1 and params[0].count('--tcp_connect=') > 0:
            # transopen = self.__write_custom__('TRANSOPEN', params[0], None)
            transopen = self.__write_custom__('TRANSOPEN',params[0], None)
            if transopen[0] != 'OK':
                return transopen
            i = 0 #counter

            while i < int(num):
                write_params[1] = int(write_params[1]) + i
                transadd = self.__write_custom__(type, *write_params)
                i+=1
                if transadd[0] != 'OK':
                    transrollback = self.__write_custom__('TRANSROLLBACK',params[0], None)
                    if transrollback[0] != 'OK':
                        closesession = self.__write_custom__('CLOSESESSION',params[0], None)
                        return transadd
                    else:
                        return transadd

            if commit == True:
                transcommit = self.__write_custom__('TRANSCOMMIT',params[0], None)
                if transcommit[0] != 'OK':
                    transrollback = self.__write_custom__('TRANSROLLBACK',params[0], None)
                    if transrollback[0] != 'OK':
                        closesession = self.__write_custom__('CLOSESESSION',params[0], None)
                        return transcommit
                    else:
                        return transcommit
                else:
                    return transcommit
            else:
                return transadd
        else:
            transopen = self.__write_custom__('TRANSOPEN', None)
            if transopen[0] != 'OK':
                return transopen
            i = 0 #counter
            while i < int(num):
                write_params[0] = int(write_params[0]) + i
                transadd = self.__write_custom__(type, *write_params)
                i+=1
                if transadd[0] != 'OK':
                    transrollback = self.__write_custom__('TRANSROLLBACK', None)
                    if transrollback[0] != 'OK':
                        closesession = self.__write_custom__('CLOSESESSION', None)
                        return transadd
                    else:
                        return transadd

            if commit == True:
                transcommit = self.__write_custom__('TRANSCOMMIT', None)
                if transcommit[0] != 'OK':
                    transrollback = self.__write_custom__('TRANSROLLBACK', None)
                    if transrollback[0] != 'OK':
                        closesession = self.__write_custom__('CLOSESESSION', None)
                        return transcommit
                    else:
                        return transcommit
                else:
                    return transcommit
            else:
                return transadd


    def read_from_device(self, *params):
        tcp_connect = None
        if len(params) > 1:
            if params[0].count('--tcp_connect=') > 0:
                tcp_connect = params[0].split('=')[1]
                request = self.proto.make(self.read_command, *params[1:])
            else:
                request = self.proto.make(self.read_command, *params)
        else:
            request = self.proto.make(self.read_command, params[0])

        # raw_data = self.__write_read__(request)
        if tcp_connect:  # tcp connect
            raw_data = self.__write_read__(request, tcp_connect)
        else:
            raw_data = self.__write_read__(request)

        answer = self.proto.parse(raw_data)
        if answer[0] == self.answer_command:
            return ['OK', answer]
        else:
            try:
                return [self.proto.ecodes[answer[0]], answer]
            except Exception:
                return ['NO_DATA', answer]

    def read_from_device_old (self, *params):
        tcp_connect = None
        if len(params) > 1:
            if params[0].count('--tcp_connect=') > 0:
                tcp_connect = params[0].split('=')[1]
                request = self.proto.make(self.read_command, *params[1:])
            else:
                request = self.proto.make(self.read_command, *params)
        else:
            request = self.proto.make(self.read_command, params[0])

                # raw_data = self.__write_read__(request)
        if tcp_connect:  # tcp connect
            raw_data = self.__write_read__(request, tcp_connect)
        else:
            raw_data = self.__write_read__(request)

        answer = self.proto.parse_old(raw_data)        
        if answer[0] == self.answer_command:
            return ['OK', answer]
        else:
           try:
               return [self.proto.ecodes[answer[0]], answer]
           except Exception:
                return ['NO_DATA', answer]

    def read_from_device_rdiagn (self, *params):
        #default_timeout = self.timeout
        #port.com.timeout = 1
        tcp_connect = None
        if len(params) > 1:
            if params[0].count('--tcp_connect=') > 0:
                tcp_connect = params[0].split('=')[1]
                request = self.proto.make(self.read_command, *params[1:])
            else:
                request = self.proto.make(self.read_command, *params)
        else:
            request = self.proto.make(self.read_command, params[0])
        if tcp_connect:  # tcp connect
            raw_data = self.__write_read__(request, tcp_connect)
        else:
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
            defaults = self.__write_custom__('DEFAULTCONFIG', *params)
        else:
            defaults = self.__write_custom__('DEFAULTCONFIG', params[0])
        if defaults[0] == 'OK':
            self.proto.pwd = '00000000'
            self.port_flush()
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
        spass1 = self.__write_custom__('SPASS1', port.settings.pwd1)            
        spass2 = self.__write_custom__('SPASS2', port.settings.pwd2)            
        spass3 = self.__write_custom__('SPASS3', port.settings.pwd3)
        self.proto.pwd = pwd_backup
        if spass1[0] == 'OK' and spass2[0] == 'OK' and spass3[0] == 'OK':               
           print('\n\nPWD RESET OK')               
           return ['OK']
        else:
           print('\n\nPWD RESET ERROR')
           return ['ERROR']

    def end_session(self):
        port.portclose()

    def port_flush(self):
        port.com.read_data_flush(20)

    def reboot_to_fw(self):
        port.com.baudrate = 115200
        port.com.timeout = 0.8
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
            port.com.write(commands[i])
            answ = port.com.read_data()
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
            
        port.com.baudrate = 9600
        port.com.timeout = 0.3
        return [status]
              

    def tranzit_off (self, speed='6', length='8', parity='0', stop='0', tcp_connect=None):
        speed_dict = {'1':300, '2':600, '3': 1200, '4':2400, '5':4800, '6': 9600, '7':19200, '8':38400, '9':57600, '10':115200}
        length_dict = {'5':5, '6':6, '7':7, '8':8}
        parity_dict = {'0':'N', '1':'E', '2':'O'}
        stop_dict = {'0':1, '1':2}
        port.com.baudrate = speed_dict[speed]
        port.com.bytesize = length_dict[length]
        port.com.parity = parity_dict[parity]
        port.com.stopbits = stop_dict[stop]
        port.com.timeout = 0.8
        success = False
        retry = 0
        while retry < 15 and not success:
            print('retry ' + str(retry))
            time.sleep(0.03)
            rqtime = str(datetime.now().time().isoformat())

            if tcp_connect:
                request = 'TRANZIT_OFF'.encode('ASCII') + b'\x0a\x0a'
                tcp_connect_array = tcp_connect.split(':')
                try:
                    print('tranzit : new socket was open')
                    raw_data = serialPort.SerialPort().tcp_connect_read(
                        uspd_server_ip=tcp_connect_array[0], uspd_server_port=tcp_connect_array[1],
                        command=request, timeout=30)
                except:
                    raw_data = ['CRC_ERROR']
                    print('was error on connect')
            else:
                port.sendcommand('TRANZIT_OFF')
                raw_data = port.readanswer(self.timeout)

            answtime = str(datetime.now().time().isoformat())
            self.log.write_log('TRANZIT_OFF', raw_data, rqtime, answtime)
            if tcp_connect is None:
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

        port.com.baudrate = 9600
        port.com.bytesize = 8
        port.com.parity = 'N'
        port.com.stopbits = 1
        port.com.timeout = 0.3        
        
        try:
            return [self.proto.codes[answer[0]], answer]
        except Exception:
            try:
                return [self.proto.ecodes[answer[0]], answer]
            except Exception:
                return ['NO_DATA', answer]
        