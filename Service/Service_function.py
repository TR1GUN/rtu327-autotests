# Здесь расположим сервиснаые функции


# //-----------------------------------------------------------------------------------------------------------------
#                       # Вынесем проверку элементов в отдельную функцию
# //-----------------------------------------------------------------------------------------------------------------

def total_assert(answer_uspd, answer_normal):
    """
    ФУНКЦИЯ ПОЭЛЕМЕНТНЙО ПРОВЕРКИ ПАКЕТА ОТВЕТА НА ОСНОВЕ УЖЕ СМГЕНЕРИРОВАННОГО ПРЕДПОЛОГАЕМОГО ОТВЕТА
    """
    assert answer_normal['prefix_byte'] == answer_uspd['prefix_byte'], \
        'Не правильно определен префексный байт\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['prefix_byte']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['prefix_byte'])

    assert answer_normal['package_size'] == answer_uspd['package_size'], \
        'Не правильно определена длина\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['package_size']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['package_size'])

    assert answer_normal['prefix_byte_ww'] == answer_uspd['prefix_byte_ww'], \
        'Не правильно определен номер пакета\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['prefix_byte_ww']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['prefix_byte_ww'])

    assert answer_normal['reserve_one'] == answer_uspd['reserve_one'], \
        'Не правильно определены резервные байты\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['reserve_one']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['reserve_one'])

    assert answer_normal['reserve_two'] == answer_uspd['reserve_two'], \
        'Не правильно определены резервные байты\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['reserve_two']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['reserve_two'])

    assert answer_normal['result_code'] == answer_uspd['result_code'], \
        'Не правильно определен байт результата\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['result_code']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['result_code'])

    # assert answer_normal['answer_data'] == answer_uspd['answer_data'], \
    #     'ОШИБКА В ДАННЫХ ответа\n' + \
    #     '\n ПОЛУЧЕННО \n' + str(answer_uspd['answer_data']) \
    #     + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['answer_data'])

    assert answer_normal['crc'] == answer_uspd['crc'], \
        'ОШИБКА В КОНТРОЛЬНОЙ СУММЕ\n' + \
        '\n ПОЛУЧЕННО \n' + str(answer_uspd['crc']) \
        + '\nДОЛЖНЫ БЫЛИ ПОЛУЧИТЬ\n' + str(answer_normal['crc'])


# //-----------------------------------------------------------------------------------------------------------------
#                       # функция которая переводит С_TYPE в нужную длину Байтовой строки
# //-----------------------------------------------------------------------------------------------------------------


def bytes_from_c_types(value):
    """
    Итак - функция которая переводит С_TYPE в нужную длину Байтовой строки.
    """
    import ctypes

    c_types_bytes = {
        ctypes.c_float: 8,
        ctypes.c_int8: 1,
        ctypes.c_int16: 2,
        ctypes.c_int32: 4,

    }

    # сначала переводим в байты
    value_bytes = bytes(value)
    # В начале надо сгенерировать команду для запроса версии

    # Достраиваем нашу команду до нужной длины
    value_bytes = value + (b'\x00' * (c_types_bytes[type(value)] - len(value)))

    return value_bytes


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для запроса системного времени
# //-----------------------------------------------------------------------------------------------------------------


def get_sys_time():
    """
    Функция для запроса системного времени
    """

    # для начала импортируем наш модуль конекта
    from Service.Connect_to_SSH import ConnectSSH

    SSH = ConnectSSH()
    result = SSH.Exec_command_return_result('date +%s')
    return int(result)


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для подготовки данных конфига
# //-----------------------------------------------------------------------------------------------------------------

def decode_data_to_GETSHPRM(answer_data):
    """
    Здесь Дешифруем данные команды GETSHPRM - запрос конфига
    """
    import struct
    # ТЕПЕРЬ НАРЕЗАЕМ
    Vers = b''
    Typ_Sh = b''
    Kt = ''
    Kn = ''
    M = ''
    Interv = b''
    Syb_Rnk = b''
    N_Ob = b''
    N_Fid = b''

    # ТЕПЕРЬ ПО БАЙТОВО СЧИТЫВАЕМ

    for i in range(2):
        Vers = Vers + bytes.fromhex(answer_data[i])
    answer_data = answer_data[2:]
    Vers = int.from_bytes(Vers, byteorder='little')

    for i in range(1):
        Typ_Sh = Typ_Sh + bytes.fromhex(answer_data[i])
    answer_data = answer_data[1:]
    Typ_Sh = int.from_bytes(Typ_Sh, byteorder='little')

    for i in range(8):
        Kt = Kt + answer_data[i]
    answer_data = answer_data[8:]
    Kt = struct.unpack('<d', bytes.fromhex(Kt))

    for i in range(8):
        Kn = Kn + answer_data[i]
    answer_data = answer_data[8:]
    Kn = struct.unpack('<d', bytes.fromhex(Kn))

    for i in range(8):
        M = M + answer_data[i]
    M = struct.unpack('<d', bytes.fromhex(M))
    answer_data = answer_data[8:]

    for i in range(1):
        Interv = Interv + bytes.fromhex(answer_data[i])
    answer_data = answer_data[1:]
    Interv = int.from_bytes(Interv, byteorder='little')

    for i in range(4):
        Syb_Rnk = Syb_Rnk + bytes.fromhex(answer_data[i])
    answer_data = answer_data[4:]
    Syb_Rnk = int.from_bytes(Syb_Rnk, byteorder='little')

    for i in range(4):
        N_Ob = N_Ob + bytes.fromhex(answer_data[i])
    answer_data = answer_data[4:]
    N_Ob = int.from_bytes(N_Ob, byteorder='little')

    for i in range(4):
        N_Fid = N_Fid + bytes.fromhex(answer_data[i])
    answer_data = answer_data[4:]
    N_Fid = int.from_bytes(N_Fid, byteorder='little')

    GETSHPRM = {

        'Vers': Vers,
        'Typ_Sh': Typ_Sh,
        'Kt': Kt,
        'Kn': Kn,
        'M': M,
        'Interv': Interv,
        'Syb_Rnk': Syb_Rnk,
        'N_Ob': N_Ob,
        'N_Fid': N_Fid,
    }

    # ТЕПЕРЬ ПРОХОДИМСЯ ПО КАЖДОМУ ЭЛЕМЕНТУ
    for key in GETSHPRM:
        # Если у нас это список - вытаскиваем данные из него
        if type(GETSHPRM[key]) == tuple:
            GETSHPRM[key] = list(GETSHPRM[key]).pop()

    return GETSHPRM


# Вспомомгательная функция для проведения соответсвия МЕЖДУ ИНДЕКСАМИ RTU и нашими индексами
def MeterId_from_USPD_to_RTU(MeterId):
    """
    Вспомомгательная функция для проведения соответсвия МЕЖДУ ИНДЕКСАМИ RTU и нашими индексами
    """
    from Service.Constant_Value_Bank import MeterId_To_RTU327_dict, MeterId_conformity_RTU_to_RTU, MeterId_To_USPD_dict

    MeterId = MeterId_To_RTU327_dict.get(MeterId_conformity_RTU_to_RTU.get(MeterId_To_USPD_dict.get(MeterId)))
    # MeterId = MeterId_To_USPD_dict.get(MeterId_conformity_RTU_to_RTU.get(MeterId_To_RTU327_dict.get(MeterId)))

    return MeterId


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для Кодирования Данных счетчика
# //-----------------------------------------------------------------------------------------------------------------


def code_data_to_GETSHPRM(data_SHPRM_dict: dict):
    """
    Получаем нашу байтовую строку из словаря значений
    """
    import struct

    # Версия параметров ( текущее значение 1) INT16
    Vers = data_SHPRM_dict['Vers'].to_bytes(2, byteorder='little', signed=True)
    # Тип счетчика INT8
    Typ_Sh = data_SHPRM_dict['Typ_Sh'].to_bytes(1, byteorder='little', signed=True)
    # здесь надо будет уже упаковывать флоат , и это делается по-другому
    # Коэффициент трансформации по току FLOAT8
    Kt = struct.pack("<d", data_SHPRM_dict['Kt'])
    # Коэффициент трансформации по напряжению FLOAT8
    Kn = struct.pack("<d", data_SHPRM_dict['Kn'])
    # Множитель FLOAT8
    M = struct.pack("<d", data_SHPRM_dict['M'])
    # Интервал профиля нагрузки INT8
    Interv = data_SHPRM_dict['Interv'].to_bytes(1, byteorder='little', signed=True)
    # Тип объекта INT32
    Syb_Rnk = data_SHPRM_dict['Syb_Rnk'].to_bytes(4, byteorder='little', signed=True)
    # Номер объекта INT32
    N_Ob = data_SHPRM_dict['N_Ob'].to_bytes(4, byteorder='little', signed=True)
    # Номер фидера INT32
    N_Fid = data_SHPRM_dict['N_Fid'].to_bytes(4, byteorder='little', signed=True)

    # собираем в единую строку
    # data = [Vers, Typ_Sh, Kt, Kn, M, Interv, Syb_Rnk, N_Ob, N_Fid]
    data = Vers + Typ_Sh + Kt + Kn + M + Interv + Syb_Rnk + N_Ob + N_Fid

    return data


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для формирования нужной команды запроса по серийнику
# //-----------------------------------------------------------------------------------------------------------------


def get_form_NSH(Serial):
    # Serial = 43982388

    # NSH Номер счетчика BCD5
    NSH = int(str(Serial), 16).to_bytes(length=5, byteorder='big')

    # NSH = str(Serial).encode()

    # print(NSH)

    # import binascii
    # NSH = binascii.hexlify(NSH)

    # print(NSH)
    # 0x00 0x43 0x98 0x23 0x88

    return NSH


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция проверки поля Data в ответе
# //-----------------------------------------------------------------------------------------------------------------

def assert_answer_data(answer_data: dict, answer_data_expected: dict):
    """
    Эта функцуия нужна для проверки значений - предпологаемого ответа и ответа реального

    """
    error = []
    # перебираем по элементам ответа предпологаемый ответ
    for filed in answer_data_expected:
        # Берем два элемента ответа
        value_answer_data_expected = answer_data_expected.get(filed)
        value_answer_data = answer_data.get(filed)
        # Если у нас ожидается float - сравниваем флоат
        if type(value_answer_data_expected) == float:
            epsilon = 5.96e-08
            if abs(value_answer_data_expected - value_answer_data) > epsilon:
                error.append({
                    "Не верное значение поля ": str(filed),
                    'Значение что ожидали в ответе': value_answer_data_expected,
                    'Значение что получили': value_answer_data,
                })
        else:
            if value_answer_data_expected != value_answer_data:
                error.append({
                    "Не верное значение поля ": str(filed),
                    'Значение что ожидали в ответе': value_answer_data_expected,
                    'Значение что получили': value_answer_data,
                })

    # Теперь все это ассертаем

    assert len(error) == 0, error


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для подготовки данных Энергии
# //-----------------------------------------------------------------------------------------------------------------

def decode_data_to_GETPOK(answer_data, Chnl):
    """
    Данная функция деалет чо - она распаковывает поле data команды GETPOK относительно параметров и
    и возвращает словарь - ЦЕ ВАЖНО
    """

    # Итакп - у нас есть ответ и есть каналы - Это важно
    import struct

    # Теперь что делаем - Парсим байты относительно наших битовых флагов

    Val_Rm = None
    Val_Rp = None
    Val_Am = None
    Val_Ap = None
    # ТЕПЕРЬ ЕСЛИ ЕСТЬ ЭТОТ ФЛАГ ТО ЕГО ПАРСИМ
    if Chnl.get('Ap'):
        Val_Ap = ''
        for i in range(8):
            Val_Ap = Val_Ap + answer_data[i]
        Val_Ap = struct.unpack('<d', bytes.fromhex(Val_Ap))
        answer_data = answer_data[8:]

        Val_Ap = normalize_data_float_from_kW_to_W(extract_value_from_tuple(Val_Ap))

    if Chnl.get('Am'):
        Val_Am = ''
        for i in range(8):
            Val_Am = Val_Am + answer_data[i]
        Val_Am = struct.unpack('<d', bytes.fromhex(Val_Am))
        answer_data = answer_data[8:]

        Val_Am = normalize_data_float_from_kW_to_W(extract_value_from_tuple(Val_Am))

    if Chnl.get('Rp'):
        Val_Rp = ''
        for i in range(8):
            Val_Rp = Val_Rp + answer_data[i]
        Val_Rp = struct.unpack('<d', bytes.fromhex(Val_Rp))
        answer_data = answer_data[8:]
        Val_Rp = normalize_data_float_from_kW_to_W(extract_value_from_tuple(Val_Rp))

    if Chnl.get('Rm'):
        Val_Rm = ''
        for i in range(8):
            Val_Rm = Val_Rm + answer_data[i]
        Val_Rm = struct.unpack('<d', bytes.fromhex(Val_Rm))
        answer_data = answer_data[8:]

        Val_Rm = normalize_data_float_from_kW_to_W(extract_value_from_tuple(Val_Rm))

    # ТЕПЕРЬ СОСТАВЛЯЕМ СЛОВАРЬ ИЗ НОРМАЛЬНЫХ КРАССИВЫХ ЗНАЧЕНИЙ И ВОЗВРАЩАЕМ ЕГО

    answer_data_dict = {
        'Rm': Val_Rm,
        'Rp': Val_Rp,
        'Am': Val_Am,
        'Ap': Val_Ap,
    }

    return answer_data_dict


def normalize_data_float_from_kW_to_W(value):
    """
    Вспомогательная функция для нормализации данных -

    ПЕРЕВОДИТ ИЗ КИЛЛОВАТТ в ВАТТЫ

    работает только с  Float

    Иначе - ОШИБКА
    """

    assert type(value) == float, 'ЗНАЧЕНИЕ НЕ float , полученное значение : ' + str(type(value)) + 'ПЕРЕМЕННАЯ ' + str(
        value)

    value = value * 1000.0

    return value


def extract_value_from_tuple(value_tuple):
    """
    ВСПОМОМГАТЕЛЬНАЯ ФУНКЦИЯ ПО ВЫТАСКИВАНИЮ FLOAT

    при распаковки байтов float вытаскивается в tuple

    ПОЭТОМУ

    эта функция вытаскивает данные FLOAT из списка

    ТОЛЬКО ПЕРВОЕ ЗНАЧЕНИЕ
    """

    assert type(value_tuple) == tuple, 'ЗНАЧЕНИЕ НЕ tuple , полученное значение : ' + str(type(value_tuple)) + \
                                       ' , ПЕРЕМЕННАЯ ' + str(value_tuple)

    value = list(value_tuple).pop()

    return value


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для кодирвоки  данных Энергии
# //-----------------------------------------------------------------------------------------------------------------

def code_data_to_GETPOK(answer_data_expected: dict = {}):
    """
    ДЕЛАЕМ ПРЕДПОЛОАГЕМУЮ КОМАНДУ ОТВЕТА НА КОМАНДУ
    """

    import struct
    data_expected = b''
    # ТЕПЕРЬ БЕРЕМ И ПО ПОРЯДКУ плюсуем
    if answer_data_expected.get('Ap') is not None:
        value = struct.pack("<d", answer_data_expected.get('Ap') / 1000.0)
        data_expected = data_expected + value
    if answer_data_expected.get('Am') is not None:
        value = struct.pack("<d", answer_data_expected.get('Am') / 1000.0)
        data_expected = data_expected + value
    if answer_data_expected.get('Rp') is not None:
        value = struct.pack("<d", answer_data_expected.get('Rp') / 1000.0)
        data_expected = data_expected + value
    if answer_data_expected.get('Rm') is not None:
        value = struct.pack("<d", answer_data_expected.get('Rm') / 1000.0)
        data_expected = data_expected + value

    return data_expected


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для подготовки данных профиля мощности
# //-----------------------------------------------------------------------------------------------------------------
def normalize_data_float_from_kWh_to_W(value, cTime):
    """
    ПЕРЕВОД из КИЛЛОВАТ ЧАС В ВАТТЫ - ЭТО ВАЖНО
    """
    Val = value * cTime * 1000.0
    return Val


def normalize_data_float_from_W_to_kWh(value, cTime):
    """
    ПЕРЕВОД из ВАТТОВ В КИЛЛОВАТ ЧАС - ЭТО ВАЖНО
    """
    # Val = value * cTime * 1000.0
    Val = value / 1000.0
    Val = Val * cTime
    return Val


def decode_data_to_GETLP(answer_data, Kanal, cTime=30):
    """
    Здесь Дешифруем данные команды GETLP - запрос конфига
    """

    # Сначала переводим CTime в ЧАСЫ
    cTime = float(60 / cTime)
    import struct
    # ТЕПЕРЬ НАРЕЗАЕМ

    Cnt = b''

    Status = b''

    TLast = b''

    # Количество передаваемых интервалов - UINT16,биты 0-14 –количество интервалов,15 установлен в 1
    for i in range(2):
        Cnt = Cnt + bytes.fromhex(answer_data[i])
    answer_data = answer_data[2:]
    Cnt = int.from_bytes(Cnt, byteorder='little')

    # КОЛИЧЕТВО ИНТЕРВАЛОВ - НАМ НУЖОНО - для определенения дальнейшей длины
    # сначала переводим в двоичную систему, обрезаем 15 байт и кодирвоку , переводим обратно
    from copy import deepcopy
    Cnt_element = int(deepcopy(bin(Cnt))[3:], 2)

    # Статус передаваемых данных , бит 0 – признак отсутствия показаний счетчика ,бит 1- переход показаний через 0 INT8
    for i in range(1):
        Status = Status + bytes.fromhex(answer_data[i])
    answer_data = answer_data[1:]
    Status = int.from_bytes(Status, byteorder='little')

    # Время окончания последнего переданного интервала TIME_T
    for i in range(4):
        TLast = TLast + bytes.fromhex(answer_data[i])
    answer_data = answer_data[4:]
    TLast = int.from_bytes(TLast, byteorder='little')

    # Пока составляем наш словарь
    GETLP = {
        'Cnt': Cnt,
        'Status': Status,
        'TLast': TLast,
    }

    # Теперь что делаем - мы указанное количество раз парсим данные
    for x in range(Cnt_element):

        Val_Qp = None
        Val_Qm = None
        Val_Pm = None
        Val_Pp = None
        # Далее повторяется в соответствии с количеством передаваемых интервалов
        # Значение расхода (кВтч) на интервале по одному типу измерений FLOAT8

        # ТЕПЕРЬ ЕСЛИ ЕСТЬ ЭТОТ ФЛАГ ТО ЕГО ПАРСИМ
        if Kanal.get('Pp'):
            Val_Pp = ''
            for i in range(8):
                Val_Pp = Val_Pp + answer_data[i]
            Val_Pp = struct.unpack('<d', bytes.fromhex(Val_Pp))
            answer_data = answer_data[8:]
            Val_Pp = normalize_data_float_from_kWh_to_W(value=extract_value_from_tuple(Val_Pp), cTime=cTime)

        if Kanal.get('Pm'):
            Val_Pm = ''
            for i in range(8):
                Val_Pm = Val_Pm + answer_data[i]
            Val_Pm = struct.unpack('<d', bytes.fromhex(Val_Pm))
            answer_data = answer_data[8:]

            Val_Pm = normalize_data_float_from_kWh_to_W(value=extract_value_from_tuple(Val_Pm), cTime=cTime)

        if Kanal.get('Qp'):
            Val_Qp = ''
            for i in range(8):
                Val_Qp = Val_Qp + answer_data[i]
            Val_Qp = struct.unpack('<d', bytes.fromhex(Val_Qp))
            answer_data = answer_data[8:]
            Val_Qp = normalize_data_float_from_kWh_to_W(value=extract_value_from_tuple(Val_Qp), cTime=cTime)

        if Kanal.get('Qm'):
            Val_Qm = ''
            for i in range(8):
                Val_Qm = Val_Qm + answer_data[i]
            Val_Qm = struct.unpack('<d', bytes.fromhex(Val_Qm))
            answer_data = answer_data[8:]

            Val_Qm = normalize_data_float_from_kWh_to_W(value=extract_value_from_tuple(Val_Qm), cTime=cTime)

        # Значения VAL повторяются по количеству запрошенных каналов профиля
        # Статус интервала ПН INT8
        Stat = b''
        for i in range(1):
            Stat = Stat + bytes.fromhex(answer_data[i])
        answer_data = answer_data[1:]
        Stat = int.from_bytes(Stat, byteorder='little')

        # Теперь что делаем - создаем словарь из значений - ЦЕ ВАЖНО
        GETLP_element_dict = {
            'Qp': Val_Qp,
            'Qm': Val_Qm,
            'Pm': Val_Pm,
            'Pp': Val_Pp,
            'Stat': Stat
        }

        # И ЭТИМ ОБНОВЛЯЕМ СЛОВАРЬ

        GETLP[x] = GETLP_element_dict

    return GETLP


def code_data_to_GETLP(answer_data, Kanal, cTime=30):
    """
    Здесь формируем байтовую строку для того чтоб сформировать предпологаемую команду , чо
    """

    # Сначала переводим CTime в ЧАСЫ
    cTime = float(60 / cTime)

    from copy import deepcopy
    import struct

    answer_data = deepcopy(answer_data)

    data = b''
    # ИТАК - с самого начала -  вытаскиваем первые клчюи в команде

    Cnt = answer_data.pop('Cnt')
    Status = answer_data.pop('Status')
    TLast = answer_data.pop('TLast')

    # Количество передаваемых интервалов UINT16,биты 0-14 –количество интервалов,15 установлен в 1
    Cnt = int.to_bytes(Cnt, length=2, byteorder='little')

    #  Статус передаваемых данных , бит 0 – признак  отсутствия показаний счетчика ,
    # бит 1- переход  показаний через 0 INT8
    Status = int.to_bytes(Status, length=1, byteorder='little')

    #  Время окончания последнего переданного интервала TIME_T

    TLast = int.to_bytes(TLast, length=4, byteorder='little')

    # ТЕПЕРЬ - Перебираем все таймштампы

    data = data + Cnt + Status + TLast

    answer_data_list = sorted(answer_data.keys())

    for timestamp in range(len(answer_data_list)):
        Val_Pp = b''
        Val_Pm = b''
        Val_Qp = b''
        Val_Qm = b''
        # Далее повторяется в соответствии с количеством передаваемых интервалов
        # Значение расхода (кВтч) на интервале по одному типу измерений FLOAT8

        # ТЕПЕРЬ ЕСЛИ ЕСТЬ ЭТОТ ФЛАГ ТО ЕГО ПАРСИМ
        if Kanal.get('Pp'):
            Val_Pp = answer_data.get(answer_data_list[timestamp]).get('Pp')
            # ПЕРЕВОДИм из ваттов в киловатт часы
            Val_Pp = normalize_data_float_from_W_to_kWh(value=Val_Pp, cTime=cTime)
            # Теперь упаковываем в байты
            Val_Pp = struct.pack("<d", Val_Pp)

        if Kanal.get('Pm'):
            Val_Pm = answer_data.get(answer_data_list[timestamp]).get('Pm')
            # ПЕРЕВОДИм из ваттов в киловатт часы
            Val_Pm = normalize_data_float_from_W_to_kWh(value=Val_Pm, cTime=cTime)
            # Теперь упаковываем в байты
            Val_Pm = struct.pack("<d", Val_Pm)

        if Kanal.get('Qp'):
            Val_Qp = answer_data.get(answer_data_list[timestamp]).get('Qp')
            # ПЕРЕВОДИм из ваттов в киловатт часы
            Val_Qp = normalize_data_float_from_W_to_kWh(value=Val_Qp, cTime=cTime)
            # Теперь упаковываем в байты
            Val_Qp = struct.pack("<d", Val_Qp)

        if Kanal.get('Qm'):
            Val_Qm = answer_data.get(answer_data_list[timestamp]).get('Qm')
            # ПЕРЕВОДИм из ваттов в киловатт часы
            Val_Qm = normalize_data_float_from_W_to_kWh(value=Val_Qm, cTime=cTime)
            # Теперь упаковываем в байты
            Val_Qm = struct.pack("<d", Val_Qm)

        Stat = 0
        Stat = int.to_bytes(Stat, length=1, byteorder='little')

        # ТЕПЕРЬ СОБИАРЕМ ЭТО ВОЕДИНО

        data = data + Val_Pp + Val_Pm + Val_Qp + Val_Qm + Stat

    return data


def form_data_to_GETLP(answer_data, Kanal):
    """
    Итак - ТУТ очень важно - формируем словарь из значений для сравнивания декодирвоанных элементов
    """

    # Количество передаваемых интервалов UINT16,биты 0-14 –количество интервалов,15 установлен в 1
    Cnt = len(answer_data)

    Cnt = bin(Cnt)[2:]
    # Добавляем 15 бит
    Cnt = '1' + str('0' * (15 - len(Cnt))) + Cnt

    Cnt = int(Cnt, 2)

    #  Статус передаваемых данных , бит 0 – признак  отсутствия показаний счетчика ,
    # бит 1- переход  показаний через 0 INT8
    Status = 0
    # Status = int.to_bytes(Status, length=1, byteorder='little')
    #  Время окончания последнего переданного интервала TIME_T
    TLast = int(max(answer_data.keys()))
    # TLast = int.to_bytes(TLast, length=4, byteorder='little')
    # Пока составляем наш словарь
    GETLP = {
        'Cnt': Cnt,
        'Status': Status,
        'TLast': TLast,
    }

    # ТЕПЕРЬ СОРТИРУЕМ НАШ СЛОВАРЬ ПО УБЫВАНИЮ

    answer_data_list = sorted(answer_data.keys())

    for timestamp in range(len(answer_data_list)):
        GETLP_element_dict = {}
        # Далее повторяется в соответствии с количеством передаваемых интервалов
        # Значение расхода (кВтч) на интервале по одному типу измерений FLOAT8

        # ТЕПЕРЬ ЕСЛИ ЕСТЬ ЭТОТ ФЛАГ ТО ЕГО ПАРСИМ
        if Kanal.get('Pp'):
            Val_Pp = answer_data.get(answer_data_list[timestamp]).get('Pp')
            # Добаеляем
            GETLP_element_dict['Pp'] = Val_Pp

        if Kanal.get('Pm'):
            Val_Pm = answer_data.get(answer_data_list[timestamp]).get('Pm')
            # Добаеляем
            GETLP_element_dict['Pm'] = Val_Pm

        if Kanal.get('Qp'):
            Val_Qp = answer_data.get(answer_data_list[timestamp]).get('Qp')
            # Добаеляем
            GETLP_element_dict['Qp'] = Val_Qp

        if Kanal.get('Qm'):
            Val_Qm = answer_data.get(answer_data_list[timestamp]).get('Qm')
            # Добаеляем
            GETLP_element_dict['Qm'] = Val_Qm

        Stat = 0
        # Добаеляем
        GETLP_element_dict['Stat'] = Stat

        # И ЭТИМ ОБНОВЛЯЕМ СЛОВАРЬ
        GETLP[timestamp] = GETLP_element_dict

    return GETLP


# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для подготовки данных  замеров параметров электросети.
# //-----------------------------------------------------------------------------------------------------------------

def decode_data_to_GETTESTS(answer_data):
    """
    Функция для подготовки данных  замеров параметров электросети.
    """
    from copy import deepcopy
    import struct
    BITSTATS = b''
    Realint = b''
    Elm = b''

    Vals_dict_bit_mask = \
        {
            # 0: None
            1: 'Wa',
            2: 'Wb',
            3: 'Wc',
            4: 'VAa',
            5: 'VAb',
            6: 'VAc',
            7: 'FREQ',
            8: 'Ia',
            9: 'Ib',
            10: 'Ic',
            11: 'Ua',
            12: 'Ub',
            13: 'Uc',
            14: 'PFangA',
            15: 'PFangB',
            16: 'PFangC',
            17: 'PHangB',
            18: 'PhangC',

        }

    Vals_by_BITSTATS = \
        {
            # 0 Не задействован
            # 1 Активная мощность фазы A, кВт (если установлен 1)
            'Wa': False,
            # 2 Активная мощность фазы B, кВт. Wb
            'Wb': False,
            # 3 Активная мощность фазы C, кВт Wc
            'Wc': False,
            # 4 Полная мощность фазы A, кВA. VAa
            'VAa': False,
            # 5 Полная мощность фазы B, кВA VAb
            'VAb': False,
            # 6 Полная мощность фазы C, кВA VAc
            'VAc': False,
            # 7 Частота сети, Гц FREQ
            'FREQ': False,
            # 8 Ток фазы A, A Ia
            'Ia': False,
            # 9 Ток фазы B, A Ib
            'Ib': False,
            # 10 Ток фазы C, A Ic
            'Ic': False,
            # 11 Напряжение фазы A, В. Ua
            'Ua': False,
            # 12 Напряжение фазы B, В. Ub
            'Ub': False,
            # 13 Напряжение фазы C, В. Uc
            'Uc': False,
            # 14 Угол между векторами U I, фазы A, Град. PFangA
            'PFangA': False,
            # 15 Угол между векторами U I, фазы B, Град. PFangB
            'PFangB': False,
            # 16 Угол между векторами U I, фазы C, Град. PFangC
            'PFangC': False,
            # 17 Угол между векторами напряжений фаз A B PHangB
            'PHangB': False,
            # 18 Угол между векторами напряжений фаз A С PhangC
            'PhangC': False,
        }

    # BITSTATS Массив битовых признаков измеряемых величин (см. ниже) INT32
    for i in range(4):
        BITSTATS = BITSTATS + bytes.fromhex(answer_data[i])
    answer_data = answer_data[4:]
    BITSTATS = int.from_bytes(BITSTATS, byteorder='little')
    # Теперь смотрим битовые маски - ЭТО ВАЖНО
    BITSTATS_bin = bin(BITSTATS)[2:]
    # ПЕРЕВОРАЧИВАЕМ
    BITSTATS_bin = BITSTATS_bin[::-1]

    # ТЕПЕРЬ ПЕРЕОПРЕДЕЛЯЕМ БИТОВЫЕ МАСКИ
    for i in range(len(BITSTATS_bin)):
        Vals_by_BITSTATS[Vals_dict_bit_mask.get(i)] = bool(int(BITSTATS_bin[i]))

    # Realint Количество возвращаемых измерений INT8
    for i in range(1):
        Realint = Realint + bytes.fromhex(answer_data[i])
    answer_data = answer_data[1:]
    Realint = int.from_bytes(Realint, byteorder='little')

    # Elm Количество элементов напряжения счетчика(cм. Ниже) INT8
    for i in range(1):
        Elm = Elm + bytes.fromhex(answer_data[i])
    answer_data = answer_data[1:]
    Elm = int.from_bytes(Elm, byteorder='little')

    GETTESTS = {
        'BITSTATS': BITSTATS,
        'Realint': Realint,
        'Elm': Elm,
    }

    # ТЕПЕРЬ ПОЙДЕТ ЖАРИШКА - БУДЕИ ДЕЛАТЬ ДЕШЕВРАЦИЮ НАГРУЗОЧНЫХ БАЙТОВ
    for i in range(Realint):
        Vals_element = deepcopy(Vals_by_BITSTATS)
        Vals_element.pop(None)

        # Сначала декодируем таймштамп
        Time = b''
        if BITSTATS > 0:
            for i in range(4):
                Time = Time + bytes.fromhex(answer_data[i])
            answer_data = answer_data[4:]
            Time = int.from_bytes(Time, byteorder='little')
            Vals_element['Time'] = Time
        # ТЕПЕРЬ ПЕРЕБИРАЕМ ФЛОАТ
        if Vals_by_BITSTATS['Wa']:
            Wa = ''
            for i in range(8):
                Wa = Wa + answer_data[i]
            Wa = struct.unpack('<d', bytes.fromhex(Wa))
            answer_data = answer_data[8:]
            Wa = extract_value_from_tuple(Wa)

            Vals_element['Wa'] = Wa / 1000.0

        if Vals_by_BITSTATS['Wb']:
            Wb = ''
            for i in range(8):
                Wb = Wb + answer_data[i]
            Wb = struct.unpack('<d', bytes.fromhex(Wb))
            answer_data = answer_data[8:]
            Wb = extract_value_from_tuple(Wb)

            Vals_element['Wb'] = Wb / 1000.0

        if Vals_by_BITSTATS['Wc']:
            Wc = ''
            for i in range(8):
                Wc = Wc + answer_data[i]
            Wc = struct.unpack('<d', bytes.fromhex(Wc))
            answer_data = answer_data[8:]
            Wc = extract_value_from_tuple(Wc)

            Vals_element['Wc'] = Wc / 1000.0

        if Vals_by_BITSTATS['VAa']:
            VAa = ''
            for i in range(8):
                VAa = VAa + answer_data[i]
            VAa = struct.unpack('<d', bytes.fromhex(VAa))
            answer_data = answer_data[8:]
            VAa = extract_value_from_tuple(VAa)

            Vals_element['VAa'] = VAa / 1000.0

        if Vals_by_BITSTATS['VAb']:
            VAb = ''
            for i in range(8):
                VAb = VAb + answer_data[i]
            VAb = struct.unpack('<d', bytes.fromhex(VAb))
            answer_data = answer_data[8:]
            VAb = extract_value_from_tuple(VAb)

            Vals_element['VAb'] = VAb / 1000.0

        if Vals_by_BITSTATS['VAc']:
            VAc = ''
            for i in range(8):
                VAc = VAc + answer_data[i]
            VAc = struct.unpack('<d', bytes.fromhex(VAc))
            answer_data = answer_data[8:]
            VAc = extract_value_from_tuple(VAc)

            Vals_element['VAc'] = VAc / 1000.0

        if Vals_by_BITSTATS['FREQ']:
            FREQ = ''
            for i in range(8):
                FREQ = FREQ + answer_data[i]
            FREQ = struct.unpack('<d', bytes.fromhex(FREQ))
            answer_data = answer_data[8:]
            FREQ = extract_value_from_tuple(FREQ)

            Vals_element['FREQ'] = FREQ

        if Vals_by_BITSTATS['Ia']:
            Ia = ''
            for i in range(8):
                Ia = Ia + answer_data[i]
            Ia = struct.unpack('<d', bytes.fromhex(Ia))
            answer_data = answer_data[8:]
            Ia = extract_value_from_tuple(Ia)

            Vals_element['Ia'] = Ia

        if Vals_by_BITSTATS['Ib']:
            Ib = ''
            for i in range(8):
                Ib = Ib + answer_data[i]
            Ib = struct.unpack('<d', bytes.fromhex(Ib))
            answer_data = answer_data[8:]
            Ib = extract_value_from_tuple(Ib)

            Vals_element['Ib'] = Ib

        if Vals_by_BITSTATS['Ic']:
            Ic = ''
            for i in range(8):
                Ic = Ic + answer_data[i]
            Ic = struct.unpack('<d', bytes.fromhex(Ic))
            answer_data = answer_data[8:]
            Ic = extract_value_from_tuple(Ic)

            Vals_element['Ic'] = Ic

        if Vals_by_BITSTATS['Ua']:
            Ua = ''
            for i in range(8):
                Ua = Ua + answer_data[i]
            Ua = struct.unpack('<d', bytes.fromhex(Ua))
            answer_data = answer_data[8:]
            Ua = extract_value_from_tuple(Ua)

            Vals_element['Ua'] = Ua

        if Vals_by_BITSTATS['Ub']:
            Ub = ''
            for i in range(8):
                Ub = Ub + answer_data[i]
            Ub = struct.unpack('<d', bytes.fromhex(Ub))
            answer_data = answer_data[8:]
            Ub = extract_value_from_tuple(Ub)

            Vals_element['Ub'] = Ub

        if Vals_by_BITSTATS['Uc']:
            Uc = ''
            for i in range(8):
                Uc = Uc + answer_data[i]
            Uc = struct.unpack('<d', bytes.fromhex(Uc))
            answer_data = answer_data[8:]
            Uc = extract_value_from_tuple(Uc)

            Vals_element['Uc'] = Uc

        if Vals_by_BITSTATS['PFangA']:
            PFangA = ''
            for i in range(8):
                PFangA = PFangA + answer_data[i]
            PFangA = struct.unpack('<d', bytes.fromhex(PFangA))
            answer_data = answer_data[8:]
            PFangA = extract_value_from_tuple(PFangA)

            Vals_element['PFangA'] = PFangA

        if Vals_by_BITSTATS['PFangB']:
            PFangB = ''
            for i in range(8):
                PFangB = PFangB + answer_data[i]
            PFangB = struct.unpack('<d', bytes.fromhex(PFangB))
            answer_data = answer_data[8:]
            PFangB = extract_value_from_tuple(PFangB)

            Vals_element['PFangB'] = PFangB

        if Vals_by_BITSTATS['PFangC']:
            PFangC = ''
            for i in range(8):
                PFangC = PFangC + answer_data[i]
            PFangC = struct.unpack('<d', bytes.fromhex(PFangC))
            answer_data = answer_data[8:]
            PFangC = extract_value_from_tuple(PFangC)

            Vals_element['PFangC'] = PFangC

        if Vals_by_BITSTATS['PHangB']:
            PHangB = ''
            for i in range(8):
                PHangB = PHangB + answer_data[i]
            PHangB = struct.unpack('<d', bytes.fromhex(PHangB))
            answer_data = answer_data[8:]

            # print('PHangB', PHangB)
            PHangB = extract_value_from_tuple(PHangB)

            Vals_element['PHangB'] = PHangB

        if Vals_by_BITSTATS['PhangC']:
            PhangC = ''
            for i in range(8):
                PhangC = PhangC + answer_data[i]
            PhangC = struct.unpack('<d', bytes.fromhex(PhangC))
            answer_data = answer_data[8:]

            # print('PhangC', PhangC)
            PhangC = extract_value_from_tuple(PhangC)

            Vals_element['PhangC'] = PhangC

        # ТЕПЕРЬ ЧТО ДЕЛАЕМ - ОЧИЩАЕМ ОТ БУДЕВЫХ ЗНАЧЕНИЙ
        keys_to_delete = []

        for keys in Vals_element:
            if type(Vals_element[keys]) == bool:
                keys_to_delete.append(keys)

        for x in keys_to_delete:
            Vals_element.pop(x)

        # И помещаем в общий список
        GETTESTS[i] = Vals_element

    return GETTESTS


def form_data_to_GETTESTS(answer_data):
    """
    Итак - ТУТ очень важно - формируем словарь из значений для сравнивания декодирвоанных элементов
    """

    # ТЕПЕРЬ ОЧЕНЬ ВАЖНЫЙ МОМЕНТ - ФОРМИРУЕМ ДЕКОДИРОВАННЫЙ ВАРИАНТ ОТВЕТА

    Vals_dict_bit_mask = {
        0: None,
        1: 'Wa',
        2: 'Wb',
        3: 'Wc',
        4: 'VAa',
        5: 'VAb',
        6: 'VAc',
        7: 'FREQ',
        8: 'Ia',
        9: 'Ib',
        10: 'Ic',
        11: 'Ua',
        12: 'Ub',
        13: 'Uc',
        14: 'PFangA',
        15: 'PFangB',
        16: 'PFangC',
        17: 'PHangB',
        18: 'PhangC',

    }

    Vals_by_BITSTATS = \
        {
            # 0 Не задействован
            None: False,
            # 1 Активная мощность фазы A, кВт (если установлен 1)
            'Wa': True,
            # 2 Активная мощность фазы B, кВт. Wb
            'Wb': True,
            # 3 Активная мощность фазы C, кВт Wc
            'Wc': True,
            # 4 Полная мощность фазы A, кВA. VAa
            'VAa': True,
            # 5 Полная мощность фазы B, кВA VAb
            'VAb': True,
            # 6 Полная мощность фазы C, кВA VAc
            'VAc': True,
            # 7 Частота сети, Гц FREQ
            'FREQ': True,
            # 8 Ток фазы A, A Ia
            'Ia': True,
            # 9 Ток фазы B, A Ib
            'Ib': True,
            # 10 Ток фазы C, A Ic
            'Ic': True,
            # 11 Напряжение фазы A, В. Ua
            'Ua': True,
            # 12 Напряжение фазы B, В. Ub
            'Ub': True,
            # 13 Напряжение фазы C, В. Uc
            'Uc': True,
            # 14 Угол между векторами U I, фазы A, Град. PFangA
            'PFangA': False,
            # 15 Угол между векторами U I, фазы B, Град. PFangB
            'PFangB': False,
            # 16 Угол между векторами U I, фазы C, Град. PFangC
            'PFangC': False,
            # 17 Угол между векторами напряжений фаз A B PHangB
            'PHangB': True,
            # 18 Угол между векторами напряжений фаз A С PhangC
            'PhangC': True,
        }

    # ФОРМИРУЕМ БИТОВЫЕ МАСКИ
    BITSTATS_bin = ''
    for keys in Vals_dict_bit_mask:
        BITSTATS_bin = BITSTATS_bin + str(int(Vals_by_BITSTATS[Vals_dict_bit_mask[keys]]))
    # ПЕРЕВОРАЧИВАЕМ
    BITSTATS_bin = BITSTATS_bin[::-1]
    # Массив битовых признаков измеряемых величин (см. ниже)
    BITSTATS = int(BITSTATS_bin, 2)

    answer_data_key_list = sorted(answer_data.keys())

    # Количество возвращаемых измерений INT8
    Realint = len(answer_data_key_list)
    # Количество элементов напряжения счетчика(cм. Ниже) INT8

    Elm = 2

    answer_data_dict = \
        {
            'BITSTATS': BITSTATS,
            'Realint': Realint,
            'Elm': Elm,
        }

    # ТЕПЕРЬ ПЕРЕБИРАЕМ НУЖНЫЕ НАМ В СПИСКЕ ВЕЩИ
    for timestamp in range(len(answer_data_key_list)):
        # сначала  формируем общий словарь -
        answer_data_dict_eliment = {}
        # Если длина не нулевая - то ставим время
        if BITSTATS > 0:
            answer_data_dict_eliment['Time'] = answer_data[answer_data_key_list[timestamp]]['Timestamp']

        # дальше проходимся по всем тегам
        for tag in Vals_by_BITSTATS:
            if Vals_by_BITSTATS[tag]:
                answer_data_dict_eliment[tag] = answer_data[answer_data_key_list[timestamp]][tag]

        answer_data_dict[timestamp] = answer_data_dict_eliment

    return answer_data_dict


def code_data_to_GETTESTS(answer_data):
    """
    Здесь формируем байтовую строку для того чтоб сформировать предпологаемую команду , чо
    """

    from copy import deepcopy
    import struct

    # ТЕПЕРЬ формируем строку

    answer_data_dict = deepcopy(answer_data)
    # ТЕПЕРЬ формируем байтовую строку

    data = b''
    # ИТАК - с самого начала -  вытаскиваем первые клчюи в команде

    BITSTATS = answer_data_dict.pop('BITSTATS')
    Realint = answer_data_dict.pop('Realint')
    Elm = answer_data_dict.pop('Elm')

    # Массив битовых признаков измеряемых величин (см. ниже) INT32
    BITSTATS = int.to_bytes(BITSTATS, length=4, byteorder='little')
    # Количество возвращаемых измерений INT8
    Realint = int.to_bytes(Realint, length=1, byteorder='little')
    # Количество элементов напряжения счетчика(cм. Ниже) INT8
    Elm = int.to_bytes(Elm, length=1, byteorder='little')

    # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ ЧТО ЕСТЬ
    data = BITSTATS + Realint + Elm

    for element in answer_data_dict:
        Time = answer_data_dict[element].pop('Time')
        Time = int.to_bytes(Time, length=4, byteorder='little')

        data = data + Time
        # ТЕПЕРЬ ПЕРЕБИРАЕМ ФЛОАТ

        Vals_dict_bit_mask = \
            {
                # 0: None
                1: 'Wa',
                2: 'Wb',
                3: 'Wc',
                4: 'VAa',
                5: 'VAb',
                6: 'VAc',
                7: 'FREQ',
                8: 'Ia',
                9: 'Ib',
                10: 'Ic',
                11: 'Ua',
                12: 'Ub',
                13: 'Uc',
                14: 'PFangA',
                15: 'PFangB',
                16: 'PFangC',
                17: 'PHangB',
                18: 'PhangC',
            }
        for tag in Vals_dict_bit_mask:

            value = answer_data_dict[element].get(Vals_dict_bit_mask[tag])
            if value is not None:
                # ТЕПЕРЬ - СМОТРИМ НАДО ЛИ ПЕРЕВОДИТЬ
                if Vals_dict_bit_mask[tag] in ['Wa', 'Wb', 'Wc', 'VAa', 'VAb', 'VAc']:
                    value = struct.pack("<d", value * 1000.0)
                else:
                    value = struct.pack("<d", value)

                data = data + value

    return data

# //-----------------------------------------------------------------------------------------------------------------
#                       # Функция для декодирования данных команды GETMTRLOG
# //-----------------------------------------------------------------------------------------------------------------

def decode_data_to_GETMTRLOG(answer_data):

    """
    ЗДЕСЬ ПРОИСХОДИТ ДЕ КОДИРОВКА В ЧЕЛОВЕЧЕСКИЙ ВИД ЗНАЧЕНИЙ КОМАНДЫ
    """

    # ПЕРВОЕ ЧТО ДЕЛАЕМ - измеряем длину
    len_data_answer = len(answer_data)
    # теперь делим на длину коректного ответа evTime + evType
    len_data_answer = len_data_answer // (2 + 4)

    # ТЕПЕРЬ ДЕКОДИРУЕМ
    answer_data_dict = {}
    for x in range(len_data_answer):
        evTime = b''
        evType = b''
        # evTime Время события TIME_T
        for i in range(4):
            evTime = evTime + bytes.fromhex(answer_data[i])
        answer_data = answer_data[4:]
        evTime = int.from_bytes(evTime, byteorder='little')

        # evType Тип (код) события INT16
        for i in range(2):
            evType = evType + bytes.fromhex(answer_data[i])
        answer_data = answer_data[2:]
        evType = int.from_bytes(evType, byteorder='little')

        # формируем словарь
        answer_data_element_dict = {
            'evTime': evTime,
            'evType': evType,
                                    }
        # Добавляем
        answer_data_dict[x] = answer_data_element_dict

    return answer_data_dict


def code_data_to_GETMTRLOG(data_answer):
    pass