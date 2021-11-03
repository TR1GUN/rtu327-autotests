from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import total_assert, assert_answer_data
from copy import deepcopy


# -------------------------------------------------------------------------------------------------------------------
#                                       GETPOK
#
#               Запрос расчетных показаний счетчика по указанным измерениям на указанное время.
# -------------------------------------------------------------------------------------------------------------------


def command_GETPOK(Ap: bool = True, Am: bool = True, Rp: bool = True, Rm: bool = True,
                count_timestamp: int = 1, RecordTypeId: list = ['ElDayEnergy']):
    """
    Получение Профиля мощности

    ПО сумме тарифов за КОНКРЕТНЫЙ таймшитамп

    сюда можно пихать

    'ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'
    """
    import struct
    # Определяем тип команды
    type_command = 'GETPOK'
    # 'ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'
    assert ('ElMomentEnergy' in RecordTypeId) or ('ElDayEnergy' in RecordTypeId) or ('ElMonthEnergy' in RecordTypeId), \
        'НЕ ВЕРНО ЗАДАН ТИП ДАННЫХ '
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETPOK

    ElectricEnergyValues = GenerateGETPOK(Count_timestamp=count_timestamp, RecordTypeId=RecordTypeId, Redefine_tag = {'Valid':0})
    # получаем данные

    # Generate_data_SHPRM_dict = deepcopy(ElectricEnergyValues.GETPOK)
    # Serial = deepcopy(ElectricEnergyValues.Serial)
    #
    # print('->',Generate_data_SHPRM_dict)
    # print('->',Serial)

    Generate_data_SHPRM_dict = {1634850000: {'Id': 1, 'Ap': 410.083, 'Am': 953.153, 'Rp': 333.235, 'Rm': 848.687, 'DeviceIdx': 1, 'Timestamp': 1634850000},
                                # 1634936400: {'Id': 2, 'Ap': 410.083, 'Am': 953.153, 'Rp': 333.235, 'Rm': 848.687, 'DeviceIdx': 1, 'Timestamp': 1634936400},
                                1635022800: {'Id': 3, 'Ap': 410.083, 'Am': 953.153, 'Rp': 333.235, 'Rm': 848.687, 'DeviceIdx': 1, 'Timestamp': 1635022800},
                                }
    Serial = '0110188597'
    # Формируем команду

    from Service.Service_function import get_form_NSH, decode_data_to_GETPOK, code_data_to_GETPOK

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    # БЕРЕМ ТАЙМШТАМП
    Timestamp = 0
    for i in Generate_data_SHPRM_dict:
        Timestamp = Generate_data_SHPRM_dict[i].get('Timestamp')
    print('Timestamp --->', Timestamp)

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
    print('Answer_expected',Answer_expected['answer_data'])
    print('Answer',Answer['answer_data'])
    # ------------------->

    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)

# -------------------------------------------------------------------------------------------------------------------
#                            Запуск тестов - Если идет прогон по Pytest - Закоментировать
# -------------------------------------------------------------------------------------------------------------------
command_GETPOK()

[b'\x02', b'\x00', b')', b'\x01', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00']

[b'\x02', b'\x00', b')', b'\x01', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\xb8', b'\x1e', b'\x85', b'\xeb', b'Q', b'\xd8', b'@', b'@', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'q', b'=', b'\n', b'\xd7', b'\xa3', b'p', b'\x05', b'@', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\xd2', b'!']
