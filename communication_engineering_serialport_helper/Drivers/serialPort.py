import datetime

__author__ = 'm.shabynin'

import serial
import time
import platform
import socket


class SerialPort(serial.Serial):

    def __init__(self, baudrate=9600, portnum='5', timeout=0.3):
        super().__init__()
        self._baudrate = baudrate
        current_os = platform.system()
        if current_os == 'Windows':
            self.port = 'COM' + portnum
        elif current_os == 'Darwin':
            self.port = '/dev/cu.' + portnum
        self.timeout = timeout
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE

    def read_data(self, answer_timeout=5):
        buf = b''
        timeout = time.time() + answer_timeout
        # waiting data for 15 seconds
        while (len(buf) == 0) and (time.time() < timeout):
            buf = self.read()
            data = b''
        # reading all data if there is something
        while len(buf) > 0:
            data = data + buf
            buf = self.read()
        return data

    def read_data_flush(self, answer_timeout=5):
        """
        For clean clipboard?
        :param answer_timeout: cutom timeout. Method will work until current timeout
        """
        buf = b''
        timeout = time.time() + answer_timeout
        # waiting data for 15 seconds
        while time.time() < timeout:
            buf = self.read()
            data = b''
        return

    def read_data_return_text(self, answer_timeout=15, decoder="utf-8", logger=None, firstNotNullByteGetTime=False):
        """
        count_of_null счетчик ожидания появления байтов
        При count_of_null > 10 прекращается ожидание появления байтов

        :param firstNoNullByteGetTime: Если True, то получить время считывания первого, не пустого, байта с УСПД.
        :return Либо просто ответ, либо если firstNoNullByteGetTime == True, тогда массив, где:
                [0] - ответ УСПД, [1] - время считывания первого не пустого байта.
        """

        buf = b''
        timeout = time.time() + answer_timeout
        count_of_firstNotNullByte = 0
        first_firstNotNullByteGetTime = None
        count_of_n = 0
        count_of_empty_line = 0

        # while time.time() < timeout or count_of_n < 2:
        # while count_of_n < 2 or count_of_empty_line < 15:
        while count_of_n < 2:
            if count_of_empty_line >= 15: break

            temp = self.read()
            buf += temp
            print(str(temp))

            # if temp == b'\n':
            if temp == b'\n' or b'\r': ##для модема, ответ заканчивается на \r\n
                count_of_n += 1
                print(str(count_of_n))
            elif temp == b'':
                print(str(count_of_empty_line))
                count_of_empty_line += 1
                # if count_of_empty_line >= 15: print('too many empty line in answer')
            else:
                count_of_n = 0
                count_of_empty_line = 0
                if count_of_firstNotNullByte == 0:
                    first_firstNotNullByteGetTime = datetime.datetime.now()
                    count_of_firstNotNullByte += 1
                if logger:
                    logger.write_log_info(temp.decode(decoder))

        if firstNotNullByteGetTime:
            return [buf.decode(decoder), str(first_firstNotNullByteGetTime)]
        else:
            return buf.decode(decoder)

    def read_data_write_instant_in_file(self, path_to_file, answer_timeout=5, decoder="utf-8", logger=None
                                        , firstNoNullByteGetTime=False):
        """
        Запись ответа в файл (path_to_file) и в logger(Если он указан)
        count_of_null счетчик ожидания появления байтов
        При count_of_null > 10 прекращается ожидание появления байтов

        :param firstNoNullByteGetTime: Если True, то получить время считывания первого, не пустого, байта с УСПД.
        :return Либо просто ответ, либо если firstNoNullByteGetTime == True, тогда массив, где:
                [0] - ответ УСПД, [1] - время считывания первого не пустого байта.

                # !!! Надо декодить из byte в String.!!!
        """

        with open(path_to_file, 'w') as file:
            timeout = time.time() + answer_timeout
            # if firstNoNullByteGetTime:
            count_of_firstNotNullByte = 0
            count_of_n = 0

            # while time.time() < timeout or count_of_n < 2:
            while count_of_n < 2:
                temp = self.read()
                # print('read_data_write_instant_in_file :: ' + str(count_of_n))
                if temp == b'\n':
                    count_of_n += 1
                else:
                    count_of_n = 0
                    if firstNoNullByteGetTime:
                        if count_of_firstNotNullByte == 0:
                            logger.write_log_info('\nfirst byte time : ' + str(datetime.datetime.now()) + '\n')
                            count_of_firstNotNullByte += 1

                # !!! Надо декодить из byte в String.!!!
                file.write(temp.decode(decoder))
                if logger:
                    logger.write_log_info(temp.decode(decoder))

                # print(temp)

    def check_answer_status(self, expected, decoder="utf-8"):
        """
        Проверка статуса OK|ERROR чтобы не ждать дальше ответа.

        !!! Работает только с COM !!!(по идеи)

        :param expected: Статус - OK или ERROR
        :param decoder: Декодер
        """
        if expected == 'OK':
            assert self.read(2).decode(decoder) == 'OK'
        elif expected == 'ERROR':
            assert self.read(5).decode(decoder) == 'ERROR'
        else:
            raise Exception('wrong status : ' + str(expected))

    def tcp_connect_read(self, uspd_server_ip, uspd_server_port, command,
                         decoder='utf-8', logger=None, answer_size=65536, timeout=600):
        """
        Отправление запроса по TCP/IP и получение ответа.

        Возможно следует побайтово читать(чтобы узнать время первого байта)?

        :param uspd_server_ip: TCP/IP сервер к которому подключаемся
        :param uspd_server_port: порт TCP/IP сервера, к которому подключаемся
        :param command: команда, которую отправляем на сервер
        :param answer_size: буффер ответа, можно сделать больше. Если ответ меньше по размеру, все равно возвращается.
        :return: возвращает byte ответ
        """
        sock = socket.socket()
        # sock.setblocking(True)
        sock.settimeout(timeout) ##?? По идеи отключение через 1200 секунд общения !!! Может оборвать связь !!!
        # sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 3000))
        try:
            sock.connect((uspd_server_ip, int(uspd_server_port)))
            sock.send(command)
            count_of_n = 0
            buf = b''
            while count_of_n < 2:
                data = sock.recv(1)  # 1 - размер ответа, можно ставить и больше, вернет сколько получил
                # print('socket :: ' + str(data))
                buf += data
                if data == b'\n': #\x0A
                    count_of_n += 1
                else:
                    count_of_n = 0

            if logger:
                logger.write_log_info(buf.decode(decoder))
            sock.close()
            return buf.decode(decoder)
        except Exception as exc:
            print('tcp_connect_readmethod has exception' + str(exc))
        finally:
            sock.close()
