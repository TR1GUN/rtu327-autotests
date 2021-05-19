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
def test_GETAUTOREAD(Ap: bool = True, Am: bool = True, Rp: bool = True, Rm: bool = True,
                     count_timestamp: int = 1, ):
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
    RecordTypeId: list = ['ElDayEnergy']
    Kk = 1

    # assert ('ElMomentEnergy' in RecordTypeId) or ('ElDayEnergy' in RecordTypeId) or ('ElMonthEnergy' in RecordTypeId), \
    #     'НЕ ВЕРНО ЗАДАН ТИП ДАННЫХ '
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
    print('Timestamp --->', Timestamp)


    print('Serial', Serial)
    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)
    print_bytes(string='NSH ===>', byte_string=NSH)
    # Формируем Признаки заказываемых измерений.
    Kanal = str(int(Rm)) + str(int(Rp)) + str(int(Am)) + str(int(Ap))
    # print_bytes(string='Kanal ===>', byte_string=Kanal)
    # Время запроса показаний счетчика TIME_T
    Tday = int(Timestamp).to_bytes(length=4, byteorder='little')

    print(Kanal)
    # # Признаки заказываемых измерений. INT8
    Kanal = int(str(Kanal), 2)
    Kanal = int(Kanal).to_bytes(length=1, byteorder='little', signed=True)

    Kk = int(Kk).to_bytes(length=1, byteorder='little', signed=True)
    # ---------- ФОРМИРУЕМ КОМАНДУ ----------
    data_request = NSH + Tday + Kanal + Kk
    command = FormCommand(type_command=type_command, data=data_request).command

    # ---------- ФОРМИРУЕМ ПРЕДПОЛАГАЕМЫЙ ОТВЕТ ----------
    # answer_data_expected = {
    #     'Rm': None,
    #     'Rp': None,
    #     'Am': None,
    #     'Ap': None,
    # }
    # if Rm:
    #     answer_data_expected['Rm'] = Generate_data_SHPRM_dict.get(Timestamp).get('Rm')
    # if Rp:
    #     answer_data_expected['Rp'] = Generate_data_SHPRM_dict.get(Timestamp).get('Rp')
    # if Am:
    #     answer_data_expected['Am'] = Generate_data_SHPRM_dict.get(Timestamp).get('Am')
    # if Ap:
    #     answer_data_expected['Ap'] = Generate_data_SHPRM_dict.get(Timestamp).get('Ap')
    # # Формируем байтовую строку нагрузочных байтов
    # data = code_data_to_GETPOK(answer_data_expected)
    # # Формируем предполагаемый ответ
    # Answer_expected = Constructor_Answer(data)
    # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
    Answer = Setup(command=command).answer

    # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------
    #
    # # ДЕКОДИРУЕМ ПОЛЕ ДАТА
    # Answer['answer_data'] = decode_data_to_GETPOK(answer_data=Answer['answer_data'],
    #                                               Chnl={"Rm": Rm, "Rp": Rp, "Am": Am, "Ap": Ap, })
    # # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    # Answer_expected['answer_data'] = answer_data_expected
    #
    # # ------------------->
    # print(Answer_expected['answer_data'])
    # print(Answer['answer_data'])
    # # ------------------->
    #
    # # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    # assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])
    #
    # # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    # total_assert(answer_uspd=Answer, answer_normal=Answer_expected)
# -------------------------------------------------------------------------------------------------------------------
#                            Запрос замеров параметров электросети.
# -------------------------------------------------------------------------------------------------------------------

test_GETAUTOREAD()