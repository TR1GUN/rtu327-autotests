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
import subprocess
import threading
import time

import numpy as np

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

def char_bytes_str_to_array(request):
    # print(parse_bytes_str_to_array(request))
    return hex_bytes_array_to_string([bytes.hex(_) for _ in parse_bytes_str_to_array(request)])

def parse_bytes_str_to_array(request,add_x_prefix=True):
    """ Кидать b'' команды . НЕ STR
    ??? Просто разбитые, не в Char представлении ???
    """
    result_array = []
    for _ in str(request).split(r'\x')[1:]:  ## Не учтен вариант если спереди уже байтовое представление
        # Первый и последний убираем, т.к. они не нужны. -- "b'" и b"'" соответственно.
        if _[0] == 'x' and len(_) > 2: _ = _[1:]  ## Проверяем x00
        if len(_) == 2:
            if add_x_prefix : result_array.append(bytes.fromhex(_))
            else : result_array.append(_)
        elif len(_) <= 1:
            raise Exception("Can't be 1 symbol")
        else:
            if add_x_prefix : first_byte =bytes.fromhex(_[:2])
            else : first_byte = _[:2]
            other_bytes = [_[2:]]
            result_array.append(first_byte)
            temp_arr = [x.encode() for x in list(' '.join(other_bytes))]
            for _ in temp_arr: result_array.append(_)
    return result_array[:-1]  ## последний ' остался от b''


# def _crc_by_int(resquest):
#     separate = hex_bytes_array_to_string(resquest)
#     res = []
#     for _ in sss :
#         res.append(int(_, 16))

def crc16_calc_tab_rtu(buf):
    """
    Вычисление контрольной суммы.
    """
    crc = 0xffff  ##Стартовое число -- объявить в глобальных(статических) переменных ?*
    for x in buf:
        crc = np.uint16(((np.uint16(TableCRC[crc >> 8])) ^ (crc << 8) ^ (np.uint16((np.uint8(x))))))
    return crc


def get_crc(request):
    """
    Получение контрольной суммы.
    ??Иногда?? высчитывается контрольная сумма как 3da, из-за этого hex() метод не работает корректно.
    ??Надо?? использовать get_right_hex() метод
    """
    res = crc16_calc_tab_rtu(request)
    return bytes.fromhex(get_right_hex(hex(res)[2:]))


def decode_hex_to_str_hex(hex_message):
    hex_message = hex_message.split('0x')
    if len(hex_message[1]) == 1: hex_message[1] = '0' + hex_message[1]
    message = r'\x' + hex_message[1]
    return message.encode('utf-8').decode('unicode_escape').encode('utf-8')  ## пока так топорно


def get_number_of_request(request):
    number_of_bytes = hex(len(parse_bytes_str_to_array(request)))[2:]
    if len(number_of_bytes) == 1: number_of_bytes = '0' + number_of_bytes  # Если меньше 10, то нужен 0 - т.к. должно отражаться 2 символа , т.е. 09,10,01,00,99
    return bytes.fromhex(number_of_bytes)


def hex_bytes_to_string(hex_bytes):
    return bytes.hex(hex_bytes)


def hex_bytes_array_to_string(hex_bytes_array):
    return [hex_bytes_to_string(_) for _ in hex_bytes_array]


def divide_bytes_string_per_byte(bytes_string):  ## Может не правильно работать с \t,\r и т.д.
    # return [x != '' for x in str(bytes_string)[2:-1].split(r'\x')]
    return [x for x in str(bytes_string)[2:-1].split('\\') if x != '']


# def bytes_string_to_hex_array(bytes_string):
#     return hex_bytes_array_to_string(divide_bytes_string_per_byte(bytes_string))

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


def check_answer_crc(result):
    """ Проверка crc команды, которая пришла от успд """
    pass


def get_result_request(request):
    prefix = b'\x02'  ## префикс
    first_part_of_package_size = b'\x00'  ## \x00 ++ <тут мы подсчитываем \\x > - Длина пакета \
    return prefix + first_part_of_package_size + get_number_of_request(request) + request + get_crc(request)


def create_command(prefix, first_part_of_package_size, ordinal_number, password, reserve, command_number,
                   command_params=None, crc=None):
    print(type(ordinal_number))
    print(type(password))
    print(type(reserve))
    print(type(decode_hex_to_str_hex(hex(command_number))))
    print(type(command_params))
    request = ordinal_number + password + reserve + decode_hex_to_str_hex(hex(command_number)) + (
        command_params if command_params else b'')
    if crc:
        return prefix + first_part_of_package_size + get_number_of_request(
            request) + request + crc  ## В тестах нужно использовать неправильный crc
    else:
        return prefix + first_part_of_package_size + get_number_of_request(request) + request + get_crc(request)


def send_command(command_number, command_params=b''):
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
    res = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res.connect(('192.168.205.10', 14101))  ##тестовая
    res.settimeout(5) ## Пока такое решение, на отключение ожидания ответа.
    # Но надо сделать отключение через цикл со временм. Например 20 сек с последнего байта - отключаемся.
    if command_number:
        bb = send_command(command_number=command_number, command_params=command_params)
    elif send_command_raw:  ## Не работает корректно ?
        bb = send_command_raw  ##не работает правильно
    print(bb, 'to_send')
    print(res.sendall(bb))
    answer_bytes = []
    while True:
        try:
            temp_char = res.recv(1)
            print(temp_char, '--')
            answer_bytes.append(temp_char)
        except Exception as ex:
            if str(ex) == 'timed out':
                break
            else:
                raise Exception(ex)
    res.close()

    hex_normal_view_answer_array = hex_bytes_array_to_string(answer_bytes)
    print(hex_normal_view_answer_array,'parsed_answer')
    """ Проверить crc """
    if answer_bytes[-3:] == ['3c', 'a0', '2f']: print('bad answer')
    return parse_answer(hex_normal_view_answer_array)


# print(get_crc(b'\x01\x00\x00\x00\x00\x00\x00\x00s\x00\x00\x00\x39'))
# print(parse_bytes_str_to_array(b'\x01\x00\x00\x00\x00\x00\x00\x00s9\x00\x00\x00'))
# print(char_bytes_str_to_array(b'\x01\x00\x00\x00\x00\x00\x00\x00s9\x00\x00\x00'))
