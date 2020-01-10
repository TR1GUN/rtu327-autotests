"""
192.168.205.10:14101 - адрес железки
FFFFFFFF - пароль (только для RTU327)

Запрос --
'\x02\x00\x09\x01\x00\x00\x00\x00\x00\x00\x00\x72\xff\xff \
\x02 - префикс\
\x00\x09 - Длина пакета \
\x01\x00 - порядковый номер\
\x00\x00\x00\x00 - пароль\
\x00\x00 - резерв\
\x72 - код команды\
\xff\xff - контрольная сумма'


Данные для расчет CRC - без Префиксный байт  + Длина пакета
\x01\x00 - порядковый номер\
\x00\x00\x00\x00 - пароль\
\x00\x00 - резерв\
\x72 - код команды\


Ответ --
b'\x02\x00\r\x01\x00\x00\x00\x00\x00\x00\x00\x00E\x97\xf6\\\x1aq'
\x02 - префикс\
\x00\r - Длина пакета \
\x01\x00 - порядковый номер\
\x00\x00\x00\x00 - пароль\
\x00\x00 - резерв\
\x00 - код результата.
\x00E\x97\xf6 - Данные
\x1aq - CRC – контрольная сумма


## 01 00 00 00 00 00 00 00 72 === a0 61

"""
import datetime
import socket
import struct
import time
import ctypes
import numpy as np
from configparser import ConfigParser
from USPD_RTU327ProtoFramework.main_methods.methods import send_read

# from device_tests import RTU327

"""
TODO:

Возможно все операции по переводу чисел в hex и обратно, надо переписать
черезе struct.pack()/struct.unpack() - для простоты работы.
"""
##helpers
def save_settings_in_ini_file(section_name, dictionary):
    """ Создает/ дописывает в конец файла новую настройку.

    Записывается одна настройка.
    Пример:
    save_settings_in_ini_file("RTU-327",
                          {"counter_number":'0010184760',
                           "uspd_tcp_ip":'192.168.205.10',
                           "uspd_tcp_port":'14101',
                           "uspd_password":'00000000'})
    """
    temp_config_parser = ConfigParser()
    temp_config_parser.add_section(section_name)
    for key in dictionary:
        temp_config_parser.set(section_name, key, dictionary[key])
    with open('uspd_settings.ini','a') as config_file:
        temp_config_parser.write(config_file)

def get_settings_dictionary_from_ini_file(file_path, uspd_name):
    temp_config_parser = ConfigParser()
    temp_config_parser.read(file_path)
    dict_schema = temp_config_parser.__dict__['_sections'][uspd_name]
    return dict(dict_schema) ## Кастим OrderDict в обычный



TableCRC = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c,
            0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6, 0x9339, 0x8318,
            0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4,
            0x5485, 0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d, 0x3653, 0x2672, 0x1611, 0x0630,
            0x76d7, 0x66f6, 0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 0x48c4,
            0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823, 0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969,
            0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12, 0xdbfd, 0xcbdc, 0xfbbf,
            0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a, 0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
            0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13,
            0x2e32, 0x1e51, 0x0e70, 0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78, 0x9188, 0x81a9,
            0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f, 0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046,
            0x6067, 0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2,
            0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d, 0x34e2,
            0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e,
            0xc71d, 0xd73c, 0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634, 0xd94c, 0xc96d, 0xf90e,
            0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
            0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a, 0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1,
            0x1ad0, 0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07,
            0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1, 0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9,
            0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0]

# temp_config_parser = ConfigParser()
# temp_config_parser.read('uspd_settings.ini')
uspd_rtu_dict = get_settings_dictionary_from_ini_file('uspd_settings.ini', 'RTU-327')
uspd_counter_number = b''.join(list((bytes.fromhex(uspd_rtu_dict.get('counter_number')[_ * 2:_ * 2 + 2])) for _ in range(int(len(uspd_rtu_dict.get('counter_number')) / 2))))  ## Номер счетчика
uspd_counter_number_as_int = int(uspd_rtu_dict.get('counter_number'))
uspd_tcp_ip = uspd_rtu_dict.get('uspd_tcp_ip')
uspd_rtu_protocol_tcp_port = int(uspd_rtu_dict.get('uspd_rtu_protocol_tcp_port'))
uspd_text_protocol_tcp_port = int(uspd_rtu_dict.get('uspd_text_protocol_tcp_port'))
uspd_password = uspd_rtu_dict.get('uspd_password')

def hex_to_dec(byte_hex_str):
    """Из байтовой hex(Например b'\x01\x00') строки возвращает dec представление/ """
    hex_str_array = byte_request_to_hex_array(byte_hex_str)
    hex_str = hex_str_array[0] + hex_str_array[1]
    return int(hex_str, 16)

def hex_array_to_dec(hex_array):
    """
    Переводим hex_array в число::
    Пример ::
        hex_array == ['5b', '37', 'ef', '50']
    Вывод ::
        1530392400
    """
    return int(''.join(hex_array), 16)

def char_bytes_str_to_array(request):
    # print(parse_bytes_str_to_array(request))
    return hex_bytes_array_to_string([bytes.hex(_) for _ in parse_bytes_str_to_array(request)])

def add_empty_bytes(byte_str, add_number, at_start=True):
    """
    Добавляем пустые байты к выражению.
    Если at_start=True - добавляем спереди --> Пример : \xff ==> \x00\xff.
    Еслм at_start=True - добавляем сзади --> Пример : \xff ==> \xff\x00.
    """
    if at_start:
        for _ in range(add_number):
            byte_str = b'\x00' + byte_str
    else:
        for _ in range(add_number):
            byte_str += b'\x00'
    return byte_str

def dec_from_bytes_array(bytes_array): ## hex_array_to_dec
    """
    Из получаемого ответа(паршеный ответ в виде массива байт) можно кидать прямо сюда куски, чтобы получить число.
    Например:
     -- передаем - ['ba', '34', '00', '00']
     -- получаем - 47668
    """
    print((' '.join(bytes_array).strip()).upper())
    print(bytes.fromhex((' '.join(bytes_array).strip()).upper()))
    print(hex_to_dec(bytes.fromhex((' '.join(bytes_array).strip()).upper())))
    return hex_to_dec(bytes.fromhex((' '.join(bytes_array).strip()).upper()))

def dec_to_hex(number):
    """
    Из числа получаем hex.(Противоположно методу dec_from_bytes_array)
    Например:
     -- передаем - 47668
     -- получаем - b'\xba4'
    """
    temp = get_right_hex(hex(number)[2:])
    result = str_to_byte_symbol_array(temp)
    return bytes.fromhex((' '.join(result).strip()).upper())


def hex_to_double(hex_array):
    """
    Из hex делаем double.
    Минус - много лишних действий.
    """
    return struct.unpack('>d', dec_to_hex(hex_array_to_dec(hex_array)))[0] ##> - прямой порядок , < - обратный порядок


def byte_request_to_int_array(request):
    """
    Возвращает запрос в виде массива чисел.
    Каждый байт это число, так что просто проходимся по запросу.
    :param request: Запрос в виде byte 'строки'. Пример :  b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x84\x0c\x16]'
    :return: массив чисел
    """
    return [x for x in request]


def byte_request_to_hex_array(request):
    """
    Возвращает запрос в виде хексового представления чисел.
    Исплоьзует метод byte_request_to_int_array()
    :return: массив hex чисел
    """
    return [get_right_hex(hex(x)[2:]) for x in byte_request_to_int_array(request)]


def byte_request_to_char_array(request):
    """
    Возвращает запрос в виде char.
    Исплоьзует метод byte_request_to_int_array()
    :return: массив символов(char)
    """
    return [chr((x)) for x in byte_request_to_int_array(request)]


def parse_bytes_str_to_array(request, add_x_prefix=True):
    """
    Разбивает byte строку, по символам.

    Кидать b'' команды . НЕ STR
    ??? Просто разбитые, не в Char представлении ???

    !!! Не работает если спереди уже стоит char передставление !!!
    """
    result_array = []
    for _ in str(request).split(r'\x')[1:]:  ## Не учтен вариант если спереди уже байтовое представление
        # Первый и последний убираем, т.к. они не нужны. -- "b'" и b"'" соответственно.
        if _[0] == 'x' and len(_) > 2: _ = _[1:]  ## Проверяем x00
        if len(_) == 2:
            if add_x_prefix:
                result_array.append(bytes.fromhex(_))
            else:
                result_array.append(_)
        elif len(_) <= 1:
            raise Exception("Can't be 1 symbol")
        else:
            if add_x_prefix:
                first_byte = bytes.fromhex(_[:2])
            else:
                first_byte = _[:2]
            other_bytes = [_[2:]]
            result_array.append(first_byte)
            temp_arr = [x.encode() for x in list(' '.join(other_bytes))]
            for _ in temp_arr: result_array.append(_)
    return result_array[:-1]  ## последний ' остался от b''


def crc16_calc_tab_rtu(buf):
    """
    Вычисление контрольной суммы с помощью библиотеки numpy.

    ## !!! В конце стоят int, вместо uint !!!
    """
    # print(buf, 'buf')

    crc = 0xffff  ##Стартовое число -- объявить в глобальных(статических) переменных ?*
    for x in buf:
        # print(crc, x)
        # crc = np.uint16(np.uint16(TableCRC[crc >> 8]) ^ (crc << 8) ^ np.uint16(np.uint8(x)))
        crc = np.uint16(np.uint16(TableCRC[crc >> 8]) ^ (crc << 8) ^ np.int16(np.int8(x))) ## !!! В конце стоят int, вместо uint !!!
    return crc


def crc16_calc_tab_rtu_ctype(buf):
    """
    Вычисление контрольной суммы с помощью библиотеки ctype.
    """
    # print(buf, 'buf')
    crc = 0xffff  ##Стартовое число -- объявить в глобальных(статических) переменных ?*
    for x in buf:
        crc = ctypes.c_uint16((((ctypes.c_uint16(TableCRC[crc >> 8]).value) ^ (crc << 8) ^ (
            ctypes.c_uint16((ctypes.c_uint8(x).value)).value)))).value
    return crc


def calculate_crcex(buf):
    """
    Вычисление контрольной суммы  с помощью библиотеки numpy(вторая формула).
    """
    # print(buf, 'buf')
    crc = 0xffff  ##Стартовое число -- объявить в глобальных(статических) переменных ?*
    for i in range(len(buf)):
        crc = np.uint16(TableCRC[crc >> 8] ^ (crc << 8) ^ buf[i])
    return crc


def get_crc(request):
    """
    Получение контрольной суммы.
    ??Иногда?? высчитывается контрольная сумма как 3da, из-за этого hex() метод не работает корректно.
    ??Надо?? использовать get_right_hex() метод
    """
    res = crc16_calc_tab_rtu(request)
    return bytes.fromhex(get_right_hex(hex(res)[2:]))


def get_crc_ctype(request):
    """
    Получение контрольной суммы.
    ??Иногда?? высчитывается контрольная сумма как 3da, из-за этого hex() метод не работает корректно.
    ??Надо?? использовать get_right_hex() метод
    """
    res = crc16_calc_tab_rtu_ctype(request)
    return bytes.fromhex(get_right_hex(hex(res)[2:]))


def decode_hex_to_str_hex(hex_message):
    hex_message = hex_message.split('0x')
    if len(hex_message[1]) == 1: hex_message[1] = '0' + hex_message[1]
    message = r'\x' + hex_message[1]
    return message.encode('utf-8').decode('unicode_escape').encode('utf-8')  ## пока так топорно


def get_number_of_request(request):
    """
    Подсчет количества байт(символов) из request.
    """
    number_of_bytes = hex(len(parse_bytes_str_to_array(request)))[2:]
    if len(number_of_bytes) == 1: number_of_bytes = '0' + number_of_bytes  # Если меньше 10, то нужен 0 - т.к. должно отражаться 2 символа , т.е. 09,10,01,00,99
    return bytes.fromhex(number_of_bytes)


def hex_bytes_to_string(hex_bytes):
    return bytes.hex(hex_bytes)


def hex_bytes_array_to_string(hex_bytes_array):
    return [hex_bytes_to_string(_) for _ in hex_bytes_array]


def divide_bytes_string_per_byte(bytes_string):  ## Может не правильно работать с \t,\r и т.д.
    return [x for x in str(bytes_string)[2:-1].split('\\') if x != '']


def get_right_hex(hex_str):
    """
    Если команда нечетная, то по идеи надо добавить спереди 0, чтобы команда была 'полноценной' hex
    Работаем с str.
    Пример: 0102 ==> 0102
            361  ==> 0361
    """
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return hex_str


def reverse_hex(hex_str):
    """
    Перевернуть hex команду. \x01\x02\x03\x04 ==> \x04\x03\x02\x01
    Работаем только с \x00 ??
    """
    return hex_str[::-1]


def get_result_request(request):
    """ Получить запрос который будет отправлен на успд. """
    prefix = b'\x02'  ## префикс
    first_part_of_package_size = b'\x00'  ## \x00 ++ <тут мы подсчитываем \\x > - Длина пакета \
    # print('---get_result_request---','\n',get_crc(request),'\n',get_crc_ctype(request),'\n', calculate_crcex(request) ,'\n', '---get_result_request---' ,'\n','\n')
    print('request',request)
    return prefix + first_part_of_package_size + get_number_of_request(request) + request + get_crc(request)


def create_command(prefix, first_part_of_package_size, ordinal_number, password, reserve, command_number,
                   command_params=None, crc=None):
    """ Кастомный сбор команды. """
    # print(type(ordinal_number))
    # print(type(password))
    # print(type(reserve))
    # print(type(decode_hex_to_str_hex(hex(command_number))))
    # print(type(command_params))
    request = ordinal_number + password + reserve + decode_hex_to_str_hex(hex(command_number)) + (
        command_params if command_params else b'')
    if crc:
        return prefix + first_part_of_package_size + get_number_of_request(
            request) + request + crc  ## В тестах нужно использовать неправильный crc
    else:
        return prefix + first_part_of_package_size + get_number_of_request(request) + request + get_crc(request)


def send_command(command_number, command_params=b''):
    """ Отправка команды. """
    ordinal_number = b'\x01\x00'  ## порядковый номер
    password = b'\x00\x00\x00\x00'  ## пароль
    reserve = b'\x00\x00'  ## резерв

    if command_params:
        return get_result_request(ordinal_number + password + reserve +
                                  decode_hex_to_str_hex(hex(command_number)) + command_params)
    else:
        return get_result_request(ordinal_number + password + reserve +
                                  decode_hex_to_str_hex(hex(command_number)))


# def send_command_raw(command):
#     return get_result_request(command)

def parse_answer(answer_array):  ## Неправильно работает ?
    """
    Парсим ответ(answer_array) с успд.
    """
    result_map = {}
    result_map['prefix_byte'] = answer_array[0]  ##0-индекс пустой??
    result_map['package_size'] = answer_array[1:3]  ##0-индекс пустой??
    result_map['prefix_byte_ww'] = answer_array[3:5]  ##0-индекс пустой??
    result_map['reserve_one'] = answer_array[5:9]  ##0-индекс пустой??
    result_map['reserve_two'] = answer_array[9:11]  ##0-индекс пустой??
    result_map['result_code'] = answer_array[11]
    result_map['answer_data'] = answer_array[12:-2]
    result_map['crc'] = answer_array[-2:]

    return result_map


def send_command_and_get_answer(command_number=None, command_params=b'', send_command_raw=None):
    """
    Главный метод работы с успд - коннектимся к успд, отсылаем строку, получаем ответ.
    """
    res = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res.connect((str(uspd_tcp_ip), uspd_rtu_protocol_tcp_port))   ##тестовая

    res.settimeout(5)  ## Пока такое решение, на отключение ожидания ответа.
    # Но надо сделать отключение через цикл со временм. Например 20 сек с последнего байта - отключаемся.
    if command_number:
        result_command = send_command(command_number=command_number, command_params=command_params)
    elif send_command_raw:  ## Не работает корректно ?
        result_command = send_command_raw  ##не работает правильно

    print(result_command, 'to_send')
    answer_bytes = []

    for i in range(3):  # Успд не вседа отвечает сразу #Работает ?
        print(res.sendall(result_command))
        # Сначала читаем первые 3 байта.
        # Второй и третий байт - это длина пакета.
        for _ in range(3):
            temp_char = res.recv(1)
            answer_bytes.append(temp_char)

        result_byte_str = b''
        for _ in answer_bytes[1:]:
            result_byte_str += _
        answer_length_without_crc = hex_to_dec(result_byte_str)
        for _ in range(answer_length_without_crc + 2):  ##Длина тела пакета + 2 байта на crc
            temp_char = res.recv(1)
            answer_bytes.append(temp_char)

        if answer_bytes != []:
            break
        elif answer_bytes == []:
            print(str(i), 'try to get answer')
            continue
        elif answer_bytes == [] and i == 3:
            res.close()
            raise Exception("USPD didn't answer")
    res.close()

    hex_normal_view_answer_array = hex_bytes_array_to_string(answer_bytes)
    print(hex_normal_view_answer_array, 'parsed_answer')
    """ Проверить crc """
    if answer_bytes[-3:] == ['3c', 'a0', '2f']: print('bad answer')
    result = b''
    for _ in answer_bytes[3:-2]: result += _
    # print([result + _ for _ in answer_bytes[3:-2]])
    # Проверяем crc, который пришел в ответ.
    # assert get_right_hex(hex_bytes_to_string(get_crc(result))) == get_right_hex(hex(crc16_calc_tab_rtu(result))[2:]) ## убираем префикс 0x
    assert get_right_hex(hex_bytes_to_string(get_crc(result))).strip() == get_right_hex(''.join(bytes_string_to_upper_hex_array(b''.join(answer_bytes[-2:]))).lower()).strip()
    return parse_answer(hex_normal_view_answer_array)

def date_to_seconds(date):
    """
    Передаем datetime.datetime - получаем время в секундах от 01.01.1970.
    """
    return int(time.mktime(date.timetuple()))

def date_from_seconds(seconds):
    """
    Возвращаем дату из секунд(Отсчет с 01.01.1970)
    """
    return datetime.datetime.utcfromtimestamp(seconds)

def hex_datetime(date_time):
    """
    Из обычной даты, возвращаем Hex.

    Пример:
    """
    return get_right_hex(hex(date_to_seconds(date_time))[2:])

def bytes_string_to_upper_hex(bytes_string):
    """ Берет байтовую строку, и превращает в строку с hex значениями.
    Пример:
    Ввод :  b'\x10\xf3"]'
    Вывод : 10 F3 22 5D
    """
    result = ''
    for _ in bytes_string:
        result += (hex(_)[2:] + ' ').upper()
    return result.strip()

def bytes_string_to_upper_hex_array(bytes_string):
    """ Берет байтовую строку, и превращает в строку с hex значениями.
    Пример:
    Ввод :  b'\x10\xf3"]'
    Вывод : ['10', 'F3', '22', '5D']
    """
    return bytes_string_to_upper_hex(bytes_string).split()

def get_reversed_bytes_string_byte_ver(bytes_string):
    """ Переворачиваем BYTE!!! строку"""
    result = bytes_string_to_upper_hex_array(bytes_string)
    result.reverse()  ## !!! Переворачиваем быйты !!!
    result = [get_right_hex(_) for _ in result] ## Надо проверять что возвращается, бывает ['5D', '23', 'F', '50'] и надо дописывать до 'правильного' HEX.
    res_str = bytes.fromhex(' '.join(result).upper())
    return res_str

def str_to_byte_symbol_array(string):
    return [string[x * (2): x * (2) + 2] for x in range(int(len(string) / 2))]

def get_reversed_bytes_string_str_ver(bytes_string):
    """ Переворачиваем STR!!!(Строку) """
    result = str_to_byte_symbol_array(bytes_string)
    result.reverse()  ## !!! Переворачиваем быйты !!!
    res_str = bytes.fromhex(' '.join(result).upper())
    return res_str

def get_reversed_time_bytes(datetime_in_seconds):
   """Дату(в секундах) переводим в hex. Дальше переворачиваем эту конструкцию, и возвращаем в байтах"""
   hex_datetime = get_right_hex(hex(datetime_in_seconds)[2:])
   res_str = get_reversed_bytes_string_str_ver(hex_datetime)
   return res_str

def get_reversed_time_bytes_by_datetime(datetime):
   """Дату(в секундах) переводим в hex. Дальше переворачиваем эту конструкцию, и возвращаем в байтах"""
   hex_datetime = get_right_hex(hex(date_to_seconds(datetime))[2:])
   res_str = get_reversed_bytes_string_str_ver(hex_datetime)
   return res_str

# print(byte_request_to_int_array(b'\x01\x00\x00\x00\x00\x00\x00\x00s\x00\x00\x00\x39'))
# print(byte_request_to_char_array(b'\x01\x00\x00\x00\x00\x00\x00\x00s\x00\x00\x00\x39'))
# print(byte_request_to_hex_array(b'\x01\x00\x00\x00\x00\x00\x00\x00s\x00\x00\x00\x39'))
#
# print(hex(crc16_calc_tab_rtu((b'\x01\x00\x00\x00\x00\x00\x00\x00s\x00\x00\x00\xff'))))
# print(hex(crc16_calc_tab_rtu_ctype((b'\x01\x00\x00\x00\x00\x00\x00\x00<'))))
# print(calculate_crcex(b'\x01\x00\x00\x00\x00\x00\x00\x00s\xf0\xf1\xff\xff'))
# print(hex(calculate_crcex(b'\x01\x00\x00\x00\x00\x00\x00\x00s\x00\x00\x00\xff')))


## Utils

# def get_var_name_and_var_value_from_vars(var_prefix):
#     """
#     Ищем (вроде) во всех переменных, переменные с префиксом --var_prefix--
#     """
#     temp_vars = vars().copy()  ## Делаем копию переменных, т.к. список ?почему-то? изменяется в реальном времени.
#     res_array = {}
#     for _ in temp_vars:
#         if _.startswith(var_prefix):
#             res_array[_] = temp_vars[_]
#     return res_array

##unused
def check_ip_args(method):
    def decorator(*args, **kwargs):
        method(*args, **kwargs)
    return decorator
##unused

def get_at_day_start_datetime(amount_of_days=0):
    cur_date = datetime.datetime.now()
    previous_day = (
            datetime.datetime.now() - datetime.timedelta(days=amount_of_days, hours=cur_date.hour, minutes=cur_date.minute,
                                                         seconds=cur_date.second, microseconds=cur_date.microsecond)
        )
    return previous_day


def get_at_day_start_datetime_bytes(amount_of_days=0):
    previous_day = get_reversed_time_bytes(
        date_to_seconds(
            get_at_day_start_datetime(amount_of_days=amount_of_days)
        ))
    return previous_day

# def get_at_day_start_datetime_bytes_from_datetime(amount_of_days=0):
#     previous_day = get_reversed_time_bytes(
#         date_to_seconds(
#             get_at_day_start_datetime(amount_of_days=amount_of_days)
#         ))
#     return previous_day


## text_protocol -- в device_test.py я импорчу все из work_with_device.py --> Получается циклическая рекурсия
def get_uspd_count_number():
    ## TODO
    ## Возможно следует READQUAL следует заменить на другую -- чтобы меньше грузилась успд.
    ## commands_send_helper -- change to this command

    all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_text_protocol_tcp_port,
                            command='READAQUAL', tcp_timeout=5)
    return all_strings.split('\n')[3].split(';')[-1].replace('<','')

def get_str_date_from_datetime(datetime_to_str, format = '%y.%m.%d %H:%M:%S'): ## %y -- последние 2 цифры года
    """
    Возвращает из строки(дата в виде строки) объект datetime.
    """
    return datetime.datetime.strftime(datetime_to_str, format)

def get_datetime_from_string(str_datetime, date_parse_format = '%Y.%m.%d %H:%M:%S'):
    """
    Возвравщает из строки объект datetime.
    :param str_datetime: Сюда передаем str дату --> Пример : '19.07.16 13:00:05'
    :param date_parse_format: Сюда передаем формат даты--> Дефолтный пример : '%y.%m.%d %H:%M:%S'
    :return: Возвращает объект datetime
    """
    return datetime.datetime.strptime(str_datetime, date_parse_format)

##helpers
# def save_settings_in_ini_file(section_name, dictionary):
#     """ Создает/ дописывает в конец файла новую настройку.
#
#     Записывается одна настройка.
#     Пример:
#     save_settings_in_ini_file("RTU-327",
#                           {"counter_number":'0010184760',
#                            "uspd_tcp_ip":'192.168.205.10',
#                            "uspd_tcp_port":'14101',
#                            "uspd_password":'00000000'})
#     """
#
#     temp_config_parser = ConfigParser()
#     temp_config_parser.add_section(section_name)
#     for key in dictionary:
#         temp_config_parser.set(section_name, key, dictionary[key])
#     with open('uspd_settings.ini','a') as config_file:
#         temp_config_parser.write(config_file)
#
# def get_settings_dictionary_from_ini_file(file_path, uspd_name):
#     temp_config_parser = ConfigParser()
#     temp_config_parser.read(file_path)
#     dict_schema = temp_config_parser.__dict__['_sections'][uspd_name]
#     return dict(dict_schema) ## Кастим OrderDict в обычный


def commands_send_helper(uspd_password,uspd_tcp_ip,uspd_tcp_port, command):
    ## В некоторых местах неправильно прокидывает.
    if type(command) is list:
        all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
                                command=command[0], args_list=command[1], tcp_timeout=5) ## ## Как command правильно записать?
    elif type(command) is str:
        all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
                                command=command, tcp_timeout=5)
    else:
        raise Exception('Неизвестный тип')
    return all_strings



#########
#########
#########

def send_read_text_rtu327_protocol(tcp_ip, tcp_port, command_number=None, command_params=b'', send_command_raw=None):
    """
    Главный метод работы с успд - коннектимся к успд, отсылаем строку, получаем ответ.
    """
    res = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res.connect((tcp_ip, tcp_port))  ##тестовая
    res.settimeout(5)  ## Пока такое решение, на отключение ожидания ответа.
    # Но надо сделать отключение через цикл со временм. Например 20 сек с последнего байта - отключаемся.
    if command_number:
        result_command = send_command(command_number=command_number, command_params=command_params)
    elif send_command_raw:  ## Не работает корректно ?
        result_command = send_command_raw  ##не работает правильно
    answer_bytes = []

    for i in range(3):  # Успд не вседа отвечает сразу #Работает ?
        print(res.sendall(result_command))
        # Сначала читаем первые 3 байта.
        # Второй и третий байт - это длина пакета.
        for _ in range(3):
            temp_char = res.recv(1)
            answer_bytes.append(temp_char)

        result_byte_str = b''
        for _ in answer_bytes[1:]:
            result_byte_str += _
        answer_length_without_crc = hex_to_dec(result_byte_str)
        for _ in range(answer_length_without_crc + 2):  ##Длина тела пакета + 2 байта на crc
            temp_char = res.recv(1)
            answer_bytes.append(temp_char)

        if answer_bytes != []:
            break
        elif answer_bytes == []:
            print(str(i), 'try to get answer')
            continue
        elif answer_bytes == [] and i == 3:
            res.close()
            raise Exception("USPD didn't answer")
    res.close()

    hex_normal_view_answer_array = hex_bytes_array_to_string(answer_bytes)
    result = b''
    for _ in answer_bytes[3:-2]: result += _
    return parse_answer(hex_normal_view_answer_array)
#

def send_read_text_protocol(uspd_password,uspd_tcp_ip,uspd_tcp_port,command): ## --> private
        print('result_command ::: ', command)
        if isinstance(command,list):
            all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
                                    command=command[0], args_list=command[1], tcp_timeout=5)
        elif isinstance(command, str):
            all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
                                    command=command, tcp_timeout=5)
        else:
            raise Exception('Неизвестный тип')
        return all_strings