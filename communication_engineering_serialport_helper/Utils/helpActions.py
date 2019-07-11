import datetime
import json
import os
import sys
import time
import unittest

from dateutil.relativedelta import relativedelta

from communication_engineering_serialport_helper.Drivers import serialPort, port
from communication_engineering_serialport_helper.Proto.CRC16RTU import Crc16
import random

unittest = unittest.TestCase()
serialPort_instance = serialPort.SerialPort()

def get_command(password, command, args_list=None):
    """
    :param password: 8-ми значный Пароль Например: 00000000
    :param command: Команда для УСПД. Например : WRITEITEMPARAM
    :param args_list: Необязательный параметр - аргументы для команды. Например: [1]
                      Передается в виде списка(liat)
    :return: Возвращает готовый запрос, для отправки в УСПД
    """

    print(str(args_list))

    crc16 = Crc16()
    result_command = str(password) + ',' + str(command)
    if args_list:
        result_command += '='

        # Проверка первого значения на 0
        # Если 0, значит ставим пропуск
        count = 0
        for x in args_list:
            if count == 0:
                count += 1
                # if x == 0:
                #     result_command += ';'
                #     continue
                if x is None:
                    if len(args_list) > 1:
                        result_command += ';'
                    else:
                        continue

            result_command += str(x) + ';'
        result_command = result_command[:-1]  # Удаляем последний знак ';'

    crc = crc16.makeCRC16(result_command)
    result_command += crc.hex()
    print(result_command)
    result_command = result_command.encode('ascii') + b'\x0a\x0a'
    return result_command


def send_command(password=None, command=None, serial_port=None, tcp_ip=None, tcp_port=None,
                 answer_size=65536, logger=None, args_list=None, result_command=None, tcp_timeout=None):
    """
    Запись вывода УСПД в указанный logger.
    Возможно работать с COM(serial_port is not None) или с TCP/IP(serial_port is None)
    Добавить описание.
    """

    # + считать время для tcp коннекта??
    # + считать время для tcp коннекта??
    # + считать время для tcp коннекта??

    if serial_port is None and (tcp_ip is None or tcp_port is None):
        raise Exception('Ни один из способов подключения не доступен')

    if result_command is None:
        result_command = get_command(password=password, command=command, args_list=args_list)
    # print(str(result_command))
    success = False  # command done
    retry = 0  # retry counter
    while not success and retry < 3:
        retry += 1
        time.sleep(0.03)

        if tcp_ip is not None and tcp_port is not None:
            answer = serialPort_instance.tcp_connect_read(
            uspd_server_ip=tcp_ip, uspd_server_port=tcp_port, command=result_command, answer_size=answer_size,
            timeout=tcp_timeout)
            first_byte_time = str(datetime.datetime.now()) # Пока возвращает текущее время
        else: # Тогда прогнать через COM-порт
            """ Надо открывать/ закрывать COM-порт !!! """
            port.portopen(serial_port)
            serial_port.write(result_command)
            answer, first_byte_time = serial_port.read_data_return_text(5, firstNotNullByteGetTime=True)  # read answer
            port.portclose(serial_port)

        # Проверка что ответ не пустой
        if len(answer) != 0:
            success = True
        else:
            print('\r\n\r\nWARNING! Retry has been used!')

    # Если ответ в итоге был пустой
    if retry >= 2:
        raise Exception('Ответ в send_command был пустой')

    if logger:
        logger.write_log_info('\ntime : ' + str(first_byte_time) + '\n'
                              + 'command : ' + result_command.decode('utf-8').replace('\n', '') + '\n'
                              + 'answer : ' + answer.replace('\n', '') + '\n')
    return answer


def get_random_args(counter_number=0, tuple=False, quality_meters=True):
    """
    counter_number -- Количество счетчиков
    tuple -- Вернуть кортеж
    Собирает рандомные параметры тегов.
    Например, используется для передачи аргументов в метод -- WRITEITEMPARAM
    :return: Список параметров
    """

    if counter_number is None:
        counter_number = 0

    if tuple:  # Кортеж
        args = (counter_number,  # N – количество электросчетчиков
                random.randrange(1, 5),  # t:=[1..4] – количество тарифов;
                random.randrange(0, 2),  # A+
                random.randrange(0, 2),  # A-
                random.randrange(0, 2),  # R+
                random.randrange(0, 2))  # R-
        if quality_meters:
            args = (*args, random.randrange(0, 2))  # All other tags

    else:  # Простой список
        args = [counter_number,  # N – количество электросчетчиков
                random.randrange(1, 5),  # t:=[1..4] – количество тарифов;
                random.randrange(0, 2),  # A+
                random.randrange(0, 2),  # A-
                random.randrange(0, 2),  # R+
                random.randrange(0, 2)]  # R-
        if quality_meters:
            args.append(random.randrange(0, 2))  # All other tags

    return args


def get_normal_text(array_of_string):
    """
    Преобразование ответа UM в удобочитаемый вариант.
    :param array_of_string: Ответ UM уже в виде array.
    :return: Возвращает в виде строки, без знаков '<'
    """

    count = 0
    result_string = ''
    for cur_line in array_of_string:
        if cur_line.count('<') == 2:
            result_string += (cur_line.replace('<', '') + '\n')
        elif cur_line.count('<') == 1:
            count += 1
            if count == 1:
                result_string += (cur_line.replace('<', '') + ' ')
            else:
                result_string += (cur_line.replace('<', ''))

        if count == 2:
            result_string += ('\n')
            count = 0
    # Добавляем в конец END + Контрольную сумму
    result_string += array_of_string[-4] + ' ' + array_of_string[-3]
    return result_string


def get_line_from_array(array, string):
    """
    Получить линию из list полученного с помощью get_normal_text
    String - в данном случае является подстрокой.
    Например string == 'ID', чтобы найти строку - ID 0003;60;0;3;10184760

    :param array: list из get_normal_text
    :param string: Искомая строка
    :return: Возвращает найденную строку
    """
    for cur_line in array:
        if cur_line.lower().startswith(string.lower()):
            return cur_line


def get_string_position_in_array(array, string):
    """
    Получить <i>Номер</i> линии из list полученного с помощью get_normal_text
    String - в данном случае является подстрокой.
    Например string == 'ID', чтобы найти строку - ID 0003;60;0;3;10184760

    :param array: list из get_normal_text
    :param string: Искомая строка
    :return: Возвращает номер найденной строки в list
    """
    index = 0
    for cur_line in array:
        if cur_line.lower().startswith(string.lower()):
            return index
        index += 1


def get_amount_of_present_tag(tag_name, array, start_amount=0, check_values=False):
    """
    Поиск всех строк с указанным тегом.
    При check_values==True : проверяем что значение является либо числом, дибо знаком вопроса(?).
    Возможно следует дописать проверку == null

    :param tag_name: Имя тега. Например tag_name == 'ID'
    :param array: list в котором будут искаться все строки с данным тегом.
    :param start_amount: Необязательный параметр. Стартовое значение счетчика.
    :return: Возвращает количество найденных строк.
    """
    for current_line in array:
        if current_line.count(tag_name + str(start_amount)):
            start_amount += 1

            # Проверка значений если check_values=True
            if check_values:
                current_line_array = current_line.split(' ')
                try:
                    try:
                       unittest.assertTrue(float(current_line_array[1]))
                    except:
                        unittest.assertTrue(int(current_line_array[1]) == 0)
                except Exception:
                    unittest.assertEqual('?', current_line_array[1])

    return start_amount

def check_present_single_tag(array, tag_name, check_values=False):
    """
    Проверка наличия одного тега в list. Т.е. не A+0,A+1 и т.д., а например F.
    При check_values==True : проверяем что значение является либо числом, дибо знаком вопроса(?).

    :param expected_amount: Ожидаемое количество тегов в list
    :param array: list в котором будут искаться все строки с данным тегом.
    :param tag_name: Искомый tag


    --- Объединить с helpActions.get_amount_of_present_tag() ??
    """
    count = 0
    for current_line in array:
        if current_line.split()[0] == tag_name:
            count += 1

            if check_values:
                current_line_array = current_line.split(' ')
                try:
                    unittest.assertTrue(float(current_line_array[1]))
                except Exception:
                    unittest.assertEqual('?', current_line_array[1])

    unittest.assertEqual(1, count, msg="Can't find : " + tag_name + " in : " + str(array))

def check_present_tags(expected_amount, array, tag_name, check_values=False):
    """
    Проверка ожидаемого количества тегов, найденных в list.

    :param expected_amount: Ожидаемое количество тегов в list
    :param array: list в котором будут искаться все строки с данным тегом.
    :param tag_name: Искомый tag
    """
    count = get_amount_of_present_tag(tag_name, array, check_values=check_values)
    unittest.assertEqual(expected_amount, count, msg="Can't find : " + tag_name + " in : " + str(array))


def get_count_positions_in_file_text_array(array, count_tag):
    """
    Нахождение всех позиций счетчиков в ответе УСПД.
    Т.е. выявление вхождение строк с подстрокой 'ID'. (Начало значений счетчика)

    :param array: list в котором будут искаться все строки с тегом 'ID'.
    :return: list значений с позициями.
    """

    positions = []
    count = 0
    for x in array:
        if str(x).count(count_tag) > 0:
            positions.append(count)
        count += 1
    return positions

def check_cmd_option(cmd_option):
    """
    Захватить значение аргумента из cmd.
    Чтобы использовать новый аргумент, нужно прописать его в conftest.py(Файл находится в самой верхней папке)
    :param cmd_option: cmd аргумент
    :return: Возвращает значение указанное в аргументе.
    """

    for x in sys.argv:
        if x.lower().count(cmd_option) > 0:
            return x.split('=')[1]

def check_cmd_option_int(cmd_option):
    """
    Захватить число аргумента из cmd.
    Чтобы использовать новый аргумент, нужно прописать его в conftest.py(Файл находится в самой верхней папке)
    :param cmd_option: cmd аргумент
    :return: Возвращает int указанный в аргументе, или 1 если был указан int меньше 1/ Неправильно указан int
    """

    for x in sys.argv:
        if x.lower().count(cmd_option) > 0:
            # print('sys argv - ' + str(sys.argv))
            number = int(x.split('=')[1])
            if number > 1:
                return number
    return 1  # Если не нашел аргумент или его значение равно 1


def get_random_date_string(startDate, endDate, reverse=False, separation_mark='.', get_only_month_date=False):
    """
    !!! В данном случае год возращает 2 последние цифры !!!

    :param startDate: Дата начала. Формат datetime.datetime
    :param endDate: Дата окончания. Формат datetime.datetime
    :param reverse: Переворачивать. Т.е. вместо дд.мм.гг, возвратить гг.мм.дд
    :param separation_mark: Разделитель. По умолчанию - '.'(точка)
    :param get_only_month_date: Вернуть дату в формате мм.гг.
    :return: Возвращает дату в string формате.
    """
    delta = endDate - startDate
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    date = startDate + datetime.timedelta(seconds=random_second)

    if get_only_month_date:
        if reverse == False:
            return str(date.month) + separation_mark + str(date.year)[2:]
        else:
            return str(date.year)[2:] + separation_mark + str(date.month)
    else:
        if reverse == False:
            return str(date.day) + separation_mark + str(date.month) + separation_mark + str(date.year)[2:]
        else:
            return str(date.year)[2:] + separation_mark + str(date.month) + separation_mark + str(date.day)


def read_all_strings_from_file(file):  # Возвращает все стркои/символы ? Нужна переменная(буфер), для сохравнения?
    """
    Считывает все стркои с файла, при этом открывая/ файл.

    :param file: Файл, с которого нужно считать.
    :return: Возвращает итоговую строку.
    """
    with open(file, 'r') as text_from_file:
        return text_from_file.read()


def get_random_multiple_to_30_minutes_time(zero_seconds=False):
    """
    Получить любое время кратное 30 мин.
    :return: Возвращает время в строковом формате
    """

    year = str(random.randrange(0, 24))
    month = str(str(int(random.randrange(0, 2)) * 30))
    if month == '0':
        month = '00'

    result = year + ':' + month
    if zero_seconds == True:
        result += ':00'
    else:
        result += ':'+str(random.randrange(0, 60))

    return result

def parse_str_date_to_datetime(date, full_date=False, only_date=False,
                               full_date_format='%d.%m.%y %H:%M:%S', only_date_format='%d.%m.%Y'):
   """
    Парсер - преобразовывает строковую дату в datetime.
    Кидает ошибку, если result_datetime остался None

   :param date: Дату в формате строки
   :param full_date: При True - проверить полную дату(дата + время)
   :param only_date:  При True - проверить только дату(без времени)
   :param full_date_format: Формат даты
   :param only_date_format: Формат даты
   :return: Возвращает дату объектом datetime
   """
   result_datetime = None
   if full_date:
       result_datetime = datetime.datetime.strptime(date, full_date_format)
   if only_date:
       result_datetime = datetime.datetime.strptime(date, only_date_format)

   if result_datetime is None:
        raise Exception('result_datetime still is None')
   return result_datetime

def get_difference_in_dates(fromDate, toDate):
    """
    Возвращает разницу в датах(Дни, чамы, минуты).
    Переписать чтобы возвращало что-то еще??

    :param fromDate: Дата От(начало временного отрезка)
    :param toDate: Дата До(конец временного отрезка)
    :return: Возвращает разницу дат(в массиве)
             Может возвращать словарем??
    """
    delta = relativedelta(toDate, fromDate)
    return [delta.days, delta.hours, delta.minutes]

def get_arch_depth_param(arch_depth_param_name):
    """
    Возвращает arch_depth_param по ключу arch_depth_param_name.
    Параметры хранятся в виде словаря(map) -- Settings/arch_depth.json

    :param arch_depth_param_name: Ключ поиска в словаре.
    Возможные ключи : <daydepth>;<dayconsdepth>;<mondepth>;<monconsdepth>;<hhconsdepth>;<aqualdepth>
    :return: Значение из словаря по данному ключу
    """

    with open(os.path.join('Settings', 'arch_depth.json'), 'r') as json_file:
        json_file_text = json_file.read()
        map = json.loads(json_file_text)
        return map[arch_depth_param_name]
