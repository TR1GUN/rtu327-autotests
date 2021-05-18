# Здесь расположим класс котоый составляет нужные нам команды
from work_with_device import send_command, get_result_request , get_crc
from copy import deepcopy


class FormCommand:
    type_command = ''

    data = b''

    command = b''

    def __init__(self, type_command, data=b''):
        self.type_command = ''
        self.command = b''
        self.data = b''
        self.type_command = type_command
        if data is not None:
            self.data = data

        # СТАРЫЙ СПОСОБ
        # self.command = send_command(
        #                             command_number=self._find_command_id(),
        #                             command_params=self.data
        #                             )

        # Формируем нашу команду
        # Постоянные :

        # Префиксионный байт
        prefix = b'\x02'
        ## пароль
        password = b'\x00\x00\x00\x00'
        ## резерв
        # reserve = b'\x00\x00'
        reserve = 0
        reserve = reserve.to_bytes(2, byteorder='little')

        # Номер пакета
        number_packet = 1
        number_packet = number_packet.to_bytes(2, byteorder='little')

        # Номер команды
        number_command = self._find_command_id()
        number_command = number_command.to_bytes(1, byteorder='little')

        # ФОРМИРУЕМ НАГРУЗОЧНЫЕ ДАННЫЕ КОМАНДЫ
        request = number_packet + password + reserve + number_command + deepcopy(self.data)
        # длина пакета
        len_packet = len(request)
        len_packet = len_packet.to_bytes(2, byteorder='big')

        command = prefix + len_packet + request + get_crc(request)
        # command = prefix + len_packet + request + b'\x00\x00'
        self.command = command

        # import binascii
        # self.command = binascii.hexlify(self.command)

        print('COMMAND , bytes --->', self.command)
        print('COMMAND , bytes --->', ' '.join(hex(x) for x in self.command))


        # command_number = struct.pack("<h",self._find_command_id())
        #
        # # Порядковый номер пакета
        # ordinal_number = 1
        # ordinal_number = ordinal_number.to_bytes(2, byteorder='big')
        # # ordinal_number = b'\x01\x00'  ## порядковый номер
        #
        # # self._find_command_id()
        #

        #
        # # ТЕПЕРЬ ПЫТАЕМСЯ УПАКОВАТЬ ПРАВИЛЬНО КОМАНДУ
        #
        #
        # command_params = self.data
        # self.command = get_result_request(ordinal_number + password + reserve + command_number + command_params)

    def _find_command_id(self):
        """
        Здесь Пытаемся найти индекс команды
        """
        from Service.Constant_Value_Bank import command_bank

        command_id = command_bank.get(self.type_command)

        return command_id
