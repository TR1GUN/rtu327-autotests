from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import total_assert, assert_answer_data
from copy import deepcopy
from work_with_device import print_bytes


# -------------------------------------------------------------------------------------------------------------------
#                                       GETAUTOREAD
#
#               Получение зафиксированных показаний счетчика ( показаний авточтения)
# -------------------------------------------------------------------------------------------------------------------
def command_GETAUTOREAD(Kanal: str = 'Ap'):
    """
    Получение Профиля мощности

    ПО сумме тарифов за КОНКРЕТНЫЙ таймшитамп

    сюда можно пихать

    'ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'
    """
    import struct
    # Определяем тип команды
    type_command = 'GETAUTOREAD'
    # 'ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'
    RecordTypeId: list = ['ElDayEnergy', 'ElMonthEnergy']
    count_timestamp: int = 3
    Kk = 1

    # assert ('ElMomentEnergy' in RecordTypeId) or ('ElDayEnergy' in RecordTypeId) or ('ElMonthEnergy' in RecordTypeId), \
    #     'НЕ ВЕРНО ЗАДАН ТИП ДАННЫХ '
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETAUTOREAD

    ElectricEnergyValues = GenerateGETAUTOREAD(Count_timestamp=count_timestamp, RecordTypeId=RecordTypeId)
    # получаем данные

    Generate_data_dict_full = deepcopy(ElectricEnergyValues.GETAUTOREAD)

    Serial = deepcopy(ElectricEnergyValues.Serial)

    # Формируем команду
    from Service.Service_function import get_form_NSH, decode_data_to_GETAUTOREAD, form_data_to_GETAUTOREAD, \
        code_data_to_GETAUTOREAD

    # выбираем все типы данных которые у нас есть
    data_type = set()
    for Idx in Generate_data_dict_full:
        data_type.add(Generate_data_dict_full[Idx].get('RecordTypeId'))

    # Теперь выбираем этот тип данных
    data_type = list(data_type)
    from random import randint
    RecordTypeId = data_type[randint(0, (len(data_type)- 1))]
    # и вытаскиваем ТОЛЬКО ЭТОТ ТИП ДАННЫХ
    Generate_data_dict = {}
    for Idx in Generate_data_dict_full:
        if Generate_data_dict_full[Idx].get('RecordTypeId') == RecordTypeId :
            Generate_data_dict.update({Generate_data_dict_full[Idx].get('Timestamp') : Generate_data_dict_full[Idx]})

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    # БЕРЕМ ТАЙМШТАМП
    Timestamp = []
    for i in Generate_data_dict:
        Timestamp.append(Generate_data_dict[i].get('Timestamp'))
    # print('ЧТО ЕСТЬ ',Timestamp)
    Timestamp.remove(max(Timestamp))
    Timestamp.remove(min(Timestamp))
    Timestamp = Timestamp.pop()


    # print('Данные ',Generate_data_dict.get(Timestamp))
    print('Timestamp --->', Timestamp)

    # Serial = '39902651'
    print('Serial', Serial)
    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)
    # print_bytes(string='NSH ===>', byte_string=NSH)
    # Формируем Признаки заказываемых измерений.
    Kanal_dict = \
        {
            'Rm': 4,
            'Rp': 3,
            'Am': 2,
            'Ap': 1,
        }
    if type(Kanal) != int:
        Kanal = Kanal_dict.get(Kanal)

    # ---------- ФОРМИРУЕМ ПРЕДПОЛАГАЕМЫЙ ОТВЕТ ----------
    answer_data_expected = form_data_to_GETAUTOREAD(answer_data=Generate_data_dict.get(Timestamp),
                                                    Serial=Serial,
                                                    Kanal=Kanal)


    # Формируем байтовую строку нагрузочных байтов
    data = code_data_to_GETAUTOREAD(answer_data_expected)
    # Формируем предполагаемый ответ
    Answer_expected = Constructor_Answer(data)
    # Время запроса показаний счетчика TIME_T
    Tday = Timestamp - 1
    Tday = int(Tday).to_bytes(length=4, byteorder='little')

    # # Признаки заказываемых измерений. INT8

    Kanal = int(Kanal).to_bytes(length=1, byteorder='little', signed=True)

    Kk = int(Kk).to_bytes(length=1, byteorder='little', signed=True)
    # ---------- ФОРМИРУЕМ КОМАНДУ ----------
    data_request = NSH + Tday + Kanal + Kk
    command = FormCommand(type_command=type_command, data=data_request).command

    # # Формируем предполагаемый ответ
    Answer_expected = Constructor_Answer(data)
    # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
    Answer = Setup(command=command).answer

    # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------
    # print(Answer)
    # # ДЕКОДИРУЕМ ПОЛЕ ДАТА
    Answer['answer_data'] = decode_data_to_GETAUTOREAD(answer_data=Answer['answer_data'], )
    # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    Answer_expected['answer_data'] = answer_data_expected

    # ------------------->
    print('Answer_expected',Answer_expected['answer_data'])
    # print(Answer)
    print('Answer',Answer['answer_data'])
    # ------------------->

    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)


# -------------------------------------------------------------------------------------------------------------------
#                            Запуск тестов - Если идет прогон по Pytest - Закоментировать
# -------------------------------------------------------------------------------------------------------------------

#
# command_GETAUTOREAD()
