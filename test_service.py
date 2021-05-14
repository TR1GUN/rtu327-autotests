# десь расположим готовые прогоны сервисных функций
from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import bytes_from_c_types, get_sys_time, total_assert


# //-----------------------------------------------------------------------------------------------------------------
#                       # Тест на команду запроса версии
# //-----------------------------------------------------------------------------------------------------------------
def test_get_version():
    """
    Тест на команду запроса версии
    USPD_RETURN :
        Описание версии, состоящее из 6 символов:
            2 байта – старший номер версии
            2 байта – средний номер версии
            2 байта – младший номер версии
    """
    # В начале надо сгенерировать команду для запроса версии
    type_command = 'GETVERSION'

    # Составляем наш список корректной команды

    command = FormCommand(type_command=type_command, data=None).command

    answer = Setup(command=command).answer

    # ПОЛУЧИЛИ ОТВЕТ - ТЕПЕРЬ ЕГО МОЖНО СРАВНИВАТЬ
    # print(answer)

    # Генерируем предпологаемый ответ
    data_bytes_list = b'0'+ b'2'+ b'0' + b'1' + b'0'+ b'2'

    normal_answer = Constructor_Answer(data_bytes=data_bytes_list)
    #
    # print(normal_answer)

    assert normal_answer == answer, 'НЕТ СООТВЕТСВИЯ ПАКЕТОВ , ' + '\nПОЛУЧИЛИ :\n' + str(answer) + \
                                    '\n Должно быть :\n' + str(normal_answer)
    # result_answer_map = send_command_and_get_answer(3)
    # self.assertEqual('0x' ,result_answer_map['result_code'])

    # assert 0x00
    #
    # Проверка правильного выполнения команды -- result_answer_map

    # answer_data = result_answer_map['answer_data']
    # self.assertEqual(6, len(answer_data))
    # ## Ожидаемый ответ железки -- ['0x30','0x32','0x30','0x31','0x30','0x32']
    # self.assertEqual(['30', '32', '30', '31', '30', '32'], result_answer_map['answer_data'])


# //-----------------------------------------------------------------------------------------------------------------
#                       # Тест на команду запроса времени
# //-----------------------------------------------------------------------------------------------------------------
def test_get_time():
    """
        Тест на команду запроса времени
    """
    # В начале надо сгенерировать команду для запроса версии
    type_command = 'GETTIME'

    # Составляем наш список корректной команды
    command = FormCommand(type_command=type_command, data=None).command
    # Теперь отправляем нашу команду
    answer = Setup(command=command).answer

    # ТЕПЕРЬ НА ОСНОВЕ ДАННОГО ВРЕМЕНИ ФОРМИРУЕМ ПРЕДПОЛООГАЕМУЮ КОМАНДУ
    data_bytes_list = b''
    for i in range(len(answer['answer_data'])):
        # ДЕЛАЕМ БАЙТ ИЗ HEX
        data_bytes_list = data_bytes_list + bytes.fromhex(answer['answer_data'][i])
    # отправляем в конструктор
    normal_answer = Constructor_Answer(data_bytes=data_bytes_list)
    # ПОЛУЧИЛИ ОТВЕТ - ТЕПЕРЬ ЕГО МОЖНО СРАВНИВАТЬ
    total_assert(answer_uspd=answer, answer_normal=normal_answer)

    # ПОЛУЧИЛИ ОТВЕТ - ТЕПЕРЬ ЕГО МОЖНО СРАВНИВАТЬ

    # ТЕПЕРЬ - НАДО ПРОВЕРИТЬ САМО ВРЕМЯ -
    # реверсируем список
    answer['answer_data'].reverse()
    # слепливаем нормальное число
    unix_time_hex = ''
    for i in range(len(answer['answer_data'])):
        unix_time_hex = unix_time_hex + answer['answer_data'][i]
    # Получаем числов  10 системе
    unix_time_dec_int = int(unix_time_hex, 16)

    # Получаем системное время
    unix_time_sys = get_sys_time()

    # Теперь конвертируем это в нормальный дата тайм
    from datetime import datetime
    # date_time = datetime.fromtimestamp(unix_time_dec_int)
    # print(date_time)

    # Сравниваем
    assert abs(unix_time_sys - unix_time_dec_int) < 10, 'НЕ КОРЕКТНОЕ ВРЕМЯ \n' + \
                                                        '\nВремя что вернули командой\n' + \
                                                        str(datetime.fromtimestamp(unix_time_dec_int)) + \
                                                        '\nВремя что на устройстве\n' + \
                                                        str(datetime.fromtimestamp(unix_time_sys))


# test_get_time()


# //-----------------------------------------------------------------------------------------------------------------
#                       # Тест на команду коррекции времени
# //-----------------------------------------------------------------------------------------------------------------


def test_set_time(time_correct: int = 60):
    """
            Тест на команду изменения времени
    """

    from work_with_device import get_right_hex
    import ctypes

    # # Итак - Сначала переводим в стандарт int16
    # time_correct_ctypes = ctypes.c_int16(time_correct)
    # # # ПОСЛЕ ЧЕГО ИМЕННО ЕГО - в байты
    # time_correct_bytes = bytes(time_correct_ctypes)
    # # # В начале надо сгенерировать команду для запроса версии
    #
    #
    #
    # # # Достраиваем нашу команду до нужной длины
    # time_correct_bytes = time_correct_bytes + (b'\x00' * (4 - len(time_correct_bytes)))

    time_correct_bytes = time_correct.to_bytes(4, byteorder='little', signed=True)
    print('bytes', time_correct_bytes)
    # Определяем тип команды
    type_command = 'SETTIME'
    # Формируем
    command = FormCommand(type_command=type_command, data=time_correct_bytes).command

    # ПОЛУЧАЕМ ВРЕМЯ ДО изменений
    unix_time_before = get_sys_time()
    # Запускаем
    answer = Setup(command=command).answer




    # Генерируем предпологаемый ответ
    data_bytes_list = b''

    normal_answer = Constructor_Answer(data_bytes=data_bytes_list)
    # ПОЛУЧИЛИ ОТВЕТ - ТЕПЕРЬ ЕГО МОЖНО СРАВНИВАТЬ

    total_assert(answer_uspd=answer, answer_normal=normal_answer)
    # Теперь проверяем записанное время

    # Получаем системное время
    unix_time_after = get_sys_time()

    unix_time_expected = unix_time_before + time_correct
    # Теперь конвертируем это в нормальный дата тайм
    from datetime import datetime
    # date_time = datetime.fromtimestamp(unix_time_dec_int)
    # print(date_time)

    # Сравниваем
    assert abs(unix_time_after - unix_time_expected) < 20, 'НЕ КОРЕКТНОЕ ВРЕМЯ \n' + \
                                                           '\nВремя что на устройстве ДО коррекции\n' + \
                                                           str(datetime.fromtimestamp(unix_time_before)) + \
                                                           '\nВремя что на устройстве ПОСЛЕ коррекции\n' + \
                                                           str(datetime.fromtimestamp(unix_time_after)) + \
                                                           '\nОжидаемое время после коррекции\n' + \
                                                           str(datetime.fromtimestamp(unix_time_expected))


test_set_time(600)





# //-----------------------------------------------------------------------------------------------------------------
#                       # Тест на команду Получение максимального идентификатора секции журнала событий RTU
# //-----------------------------------------------------------------------------------------------------------------

# Не работает?
def test_get_max_log_id():
    """
    Получение максимального идентификатора секции журнала событий RTU. Максимальный
    идентификатор (максимальный номер события) может быть использован для проверки переполнения или
    очистки журнала событий RTU.
    """
    # Определяем тип команды
    type_command = 'GETMAXLOGID'
    # Формируем

    data = b'\x01'
    command = FormCommand(type_command=type_command, data=data).command

    # Запускаем
    answer = Setup(command=command).answer

    data_bytes_list = []

    normal_answer = Constructor_Answer(data_bytes=data)

    # ПОЛУЧИЛИ ОТВЕТ - ТЕПЕРЬ ЕГО МОЖНО СРАВНИВАТЬ
    total_assert(answer_uspd=answer, answer_normal=normal_answer)


# //-----------------------------------------------------------------------------------------------------------------
#                       # Тест на команду Запрос журнала событий RTU
# //-----------------------------------------------------------------------------------------------------------------

def test_get_log():
    """
    Запрос журнала событий RTU.
    """
    # Определяем тип команды
    type_command = 'GETLOG'
    # Формируем команду
    Nsect = b'\x00\x00\x00\x01'
    ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
    Id = b'\x00\x00\x00\x01'
    Num = b'\x00\x01'

    data = Nsect + Id + Num

    command = FormCommand(type_command=type_command, data=data).command

    # Запускаем
    answer = Setup(command=command).answer

    data_bytes_list = []

    normal_answer = Constructor_Answer(data_bytes=data)

    # ПОЛУЧИЛИ ОТВЕТ - ТЕПЕРЬ ЕГО МОЖНО СРАВНИВАТЬ
    total_assert(answer_uspd=answer, answer_normal=normal_answer)

# ---------------------------------------------------------------------------------------------------------------------
