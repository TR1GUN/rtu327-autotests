from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import total_assert, assert_answer_data
from copy import deepcopy


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
    # Определяем тип команды
    type_command = 'GETLP'

    cTime = 60
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETLP

    ElectricPowerValues = GenerateGETLP(Count_timestamp=Kk, cTime=cTime)
    # получаем данные
    Generate_data_GETLP_dict = deepcopy(ElectricPowerValues.GETLP)
    Serial = deepcopy(ElectricPowerValues.Serial)

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    from Service.Service_function import get_form_NSH, decode_data_to_GETLP, code_data_to_GETLP , form_data_to_GETLP
    Timestamp_list = []
    for i in Generate_data_GETLP_dict:
        Timestamp_list.append(Generate_data_GETLP_dict[i].get('Timestamp'))
    Timestamp = min(Timestamp_list)
    print('-->Timestamp--->', Timestamp)
    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)

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
    answer_data_expected = form_data_to_GETLP(answer_data=Generate_data_GETLP_dict,
                                              Kanal= {"Qp": Qp, "Qm": Qm, "Pm": Pm, "Pp": Pp, })

    # Формируем байтовую строку нагрузочных байтов
    data = code_data_to_GETLP(answer_data=answer_data_expected ,
                              Kanal={"Qp": Qp, "Qm": Qm, "Pm": Pm, "Pp": Pp, },
                              cTime=cTime)
    # Формируем предполагаемый ответ
    Answer_expected = Constructor_Answer(data)
    # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
    Answer = Setup(command=command).answer



    # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------
    # ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА
    Answer['answer_data'] = decode_data_to_GETLP(
        answer_data=Answer['answer_data'],
        Kanal={"Qp": Qp, "Qm": Qm, "Pm": Pm, "Pp": Pp, },
        cTime=cTime
    )
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
#                            Запрос замеров параметров электросети.
# -------------------------------------------------------------------------------------------------------------------
test_GETLP(Kk=10, Qp=True, Qm=True, Pm=True, Pp=True)

# test_GETSHPRM()
# test_GETPOK(count_timestamp=[6], Ap=True, Am=True, Rp=True, Rm=True, RecordTypeId = ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'])

# lol = {1620964800: {'Id': 8, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620964800}, 1620968400: {'Id': 9, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620968400}, 1620972000: {'Id': 10, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620972000}, 1620975600: {'Id': 11, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620975600}, 1620979200: {'Id': 12, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620979200}, 1620982800: {'Id': 13, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620982800}, 1620986400: {'Id': 14, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620986400}, 1620990000: {'Id': 15, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620990000}, 1620993600: {'Id': 16, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620993600}, 1620997200: {'Id': 17, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620997200}}
#
# lol_2 = sorted(lol.keys())
#
# print(lol)
# print(lol_2)

#
# print(min(lol.keys()))
#
# Timestamp_list = []
# for i in lol:
#     Timestamp_list.append(lol[i].get('Timestamp'))
# Timestamp = min(Timestamp_list)
#
# print(Timestamp)