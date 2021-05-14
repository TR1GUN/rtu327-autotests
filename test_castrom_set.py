from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import total_assert, assert_answer_data
from copy import deepcopy


# -------------------------------------------------------------------------------------------------------------------
#                                       GETSHPRM
#
#                     Получение основных параметров точки учета (счетчика).
# -------------------------------------------------------------------------------------------------------------------
def test_GETSHPRM():
    """
    Получение основных параметров точки учета (счетчика).

    """
    # Определяем тип команды
    type_command = 'GETSHPRM'

    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GeneratorDataConfig
    # Генерируем конфиг
    Config = GeneratorDataConfig()
    # получаем данные
    data_SHPRM_dict = deepcopy(Config.GETSHPRM)
    Serial = deepcopy(Config.Serial)

    from Service.Service_function import get_form_NSH, decode_data_to_GETSHPRM, code_data_to_GETSHPRM

    # Формируем предполагаемый ответ
    data = code_data_to_GETSHPRM(data_SHPRM_dict=data_SHPRM_dict)
    Answer_expected = Constructor_Answer(data)

    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)
    # ФОРМИРУЕМ КОМАНДУ
    command = FormCommand(type_command=type_command, data=NSH).command
    # Отправляем ее
    Answer = Setup(command=command).answer

    # print('Answer\n', Answer)
    # print('Answer_expected\n', Answer_expected)

    # ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА
    Answer['answer_data'] = decode_data_to_GETSHPRM(answer_data=Answer['answer_data'])
    # Answer_expected['answer_data'] = decode_data_to_GETSHPRM(answer_data=Answer_expected['answer_data'])
    # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    Answer_expected['answer_data'] = data_SHPRM_dict

    # ------------------->
    print(Answer_expected['answer_data'])
    print(Answer['answer_data'])
    # ------------------->

    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)


# test_GETSHPRM()

# -------------------------------------------------------------------------------------------------------------------
#                                       GETPOK
#
#               Запрос расчетных показаний счетчика по указанным измерениям на указанное время.
# -------------------------------------------------------------------------------------------------------------------
def test_GETPOK(Ap: bool = True, Am: bool = True, Rp: bool = True, Rm: bool = True,
                count_timestamp: int = 1, RecordTypeId: list = ['ElDayEnergy']):
    """
    Получение Профиля мощности

    ПО сумме тарифов за КОНКРЕТНЫЙ таймшитамп

    сюда можно пихать

    'ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'
    """
    import struct
    from copy import deepcopy
    # Определяем тип команды
    type_command = 'GETPOK'
    # 'ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'
    assert ('ElMomentEnergy' in RecordTypeId) or ('ElDayEnergy' in RecordTypeId) or ('ElMonthEnergy' in RecordTypeId), \
        'НЕ ВЕРНО ЗАДАН ТИП ДАННЫХ '
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETPOK

    ElectricEnergyValues = GenerateGETPOK(Count_timestamp=count_timestamp, RecordTypeId=RecordTypeId)
    # получаем данные
    Generate_data_SHPRM_dict = deepcopy(ElectricEnergyValues.GETPOK)
    Serial = deepcopy(ElectricEnergyValues.Serial)

    # Формируем команду
    from Service.Service_function import get_form_NSH, decode_data_to_GETPOK, code_data_to_GETPOK

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    # БЕРЕМ ТАЙМШТАМП
    Timestamp = 0
    for i in Generate_data_SHPRM_dict:
        Timestamp = Generate_data_SHPRM_dict[i].get('Timestamp')
    # print('Timestamp --->', Timestamp)

    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)

    # Формируем Признаки заказываемых измерений.
    Chnl = str(int(Rm)) + str(int(Rp)) + str(int(Am)) + str(int(Ap))

    print(Chnl)
    # # Признаки заказываемых измерений. INT8
    Chnl = int(str(Chnl), 2).to_bytes(length=1, byteorder='little')

    # Время запроса показаний счетчика TIME_T
    Time = int(Timestamp).to_bytes(length=4, byteorder='little')

    # ---------- ФОРМИРУЕМ КОМАНДУ ----------
    data_request = NSH + Chnl + Time
    command = FormCommand(type_command=type_command, data=data_request).command

    # ---------- ФОРМИРУЕМ ПРЕДПОЛАГАЕМЫЙ ОТВЕТ ----------
    answer_data_expected = {
        'Rm': None,
        'Rp': None,
        'Am': None,
        'Ap': None,
                            }
    if Rm:
        answer_data_expected['Rm'] = Generate_data_SHPRM_dict.get(Timestamp).get('Rm')
    if Rp:
        answer_data_expected['Rp'] = Generate_data_SHPRM_dict.get(Timestamp).get('Rp')
    if Am:
        answer_data_expected['Am'] = Generate_data_SHPRM_dict.get(Timestamp).get('Am')
    if Ap:
        answer_data_expected['Ap'] = Generate_data_SHPRM_dict.get(Timestamp).get('Ap')
    # Формируем байтовую строку нагрузочных байтов
    data = code_data_to_GETPOK(answer_data_expected)
    # Формируем предполагаемый ответ
    Answer_expected = Constructor_Answer(data)
    # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
    Answer = Setup(command=command).answer

    # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------

    # ДЕКОДИРУЕМ ПОЛЕ ДАТА
    Answer['answer_data'] = decode_data_to_GETPOK(answer_data=Answer['answer_data'],
                                                  Chnl={"Rm": Rm, "Rp": Rp, "Am": Am, "Ap": Ap, })
    # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    Answer_expected['answer_data'] = answer_data_expected

    # ------------------->
    print(Answer_expected['answer_data'])
    print(Answer['answer_data'])
    # ------------------->

    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)


# -------------------------------------------------------------------------------------------------------------------
#                                        GETLP
#
#                   Запрос на передачу профиля расходов коммерческого интервала.
# -------------------------------------------------------------------------------------------------------------------
def test_GETLP(Qp: bool = True, Qm: bool = True, Pp: bool = True, Pm: bool = True, Tstart: int = 1, Kk: int = 1):
    """
    Получение Профиля мощности?
    """
    import struct
    from copy import deepcopy
    # Определяем тип команды
    type_command = 'GETLP'

    cTime = 60
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETLP

    ElectricPowerValues = GenerateGETLP(Count_timestamp=Kk, cTime=cTime)
    # получаем данные
    Generate_data_SHPRM_dict = deepcopy(ElectricPowerValues.GETLP)
    Serial = deepcopy(ElectricPowerValues.Serial)
    print('----->', Generate_data_SHPRM_dict)

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    from Service.Service_function import get_form_NSH, decode_data_to_GETLP
    Timestamp_list = []
    for i in Generate_data_SHPRM_dict:
        Timestamp_list.append(Generate_data_SHPRM_dict[i].get('Timestamp'))
    Timestamp = min(Timestamp_list)
    print('Timestamp', Timestamp)
    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)

    print(Generate_data_SHPRM_dict)
    # Формируем Признаки заказываемых измерений.
    Kanal = str(int(Qm)) + str(int(Qp)) + str(int(Pm)) + str(int(Pp))
    # # Признаки заказываемых измерений. INT8
    Kanal = int(str(Kanal), 2).to_bytes(length=1, byteorder='little')

    # Время запроса показаний счетчика TIME_T
    Tstart = int(Timestamp).to_bytes(length=4, byteorder='little')

    # Время запроса показаний счетчика TIME_T
    Kk = int(Kk).to_bytes(length=2, byteorder='little')

    # ---------- ФОРМИРУЕМ КОМАНДУ ----------
    data_request = NSH + Kanal + Tstart + Kk
    command = FormCommand(type_command=type_command, data=data_request).command

    # ---------- ФОРМИРУЕМ ПРЕДПОЛАГАЕМЫЙ ОТВЕТ ----------

    # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
    Answer = Setup(command=command).answer

    print(Answer)

    # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------

    # ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА
    Answer['answer_data'] = decode_data_to_GETLP(answer_data=Answer['answer_data'],
                                                 Kanal={"Qp": Qp, "Qm": Qm, "Pm": Pm, "Pp": Pp, },
                                                 cTime= cTime
                                                )
    # Answer_expected['answer_data'] = decode_data_to_GETSHPRM(answer_data=Answer_expected['answer_data'])
    # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    # Answer_expected['answer_data'] = data_SHPRM_dict

    # ------------------->
    # print(Answer_expected['answer_data'])
    print(Answer['answer_data'])
    # ------------------->


# -------------------------------------------------------------------------------------------------------------------
#                            Запрос замеров параметров электросети.
# -------------------------------------------------------------------------------------------------------------------
test_GETLP(Kk=10, Qp=True, Qm=True, Pm=True, Pp=True)

# test_GETSHPRM()
# test_GETPOK(count_timestamp=[6], Ap=True, Am=True, Rp=True, Rm=True, RecordTypeId = ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'])
