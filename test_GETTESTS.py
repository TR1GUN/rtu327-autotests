from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import total_assert, assert_answer_data
from copy import deepcopy


# -------------------------------------------------------------------------------------------------------------------
#                                        GETTESTS
#
#                   Запрос на передачу профиля расходов коммерческого интервала.
# -------------------------------------------------------------------------------------------------------------------
def test_GETTESTS(NumTests: int = 1):
    """
    Получение Профиля мощности?
    """
    import struct
    # Определяем тип команды
    type_command = 'GETTESTS'

    cTime = 60
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETTESTS

    ElectricPowerValues = GenerateGETTESTS(Count_timestamp=NumTests)
    # # получаем данные
    Generate_data_GETLP_dict = deepcopy(ElectricPowerValues.GETTESTS)
    Serial = deepcopy(ElectricPowerValues.Serial)

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    from Service.Service_function import get_form_NSH, decode_data_to_GETTESTS, code_data_to_GETTESTS, \
        form_data_to_GETTESTS
    Timestamp_list = []
    for i in Generate_data_GETLP_dict:
        Timestamp_list.append(Generate_data_GETLP_dict[i].get('Timestamp'))
    print(Timestamp_list)
    Timestamp = min(Timestamp_list)
    print('-->Timestamp--->', Timestamp)
    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)

    # ФОРМИРУЕМ КОЛИЧЕСТВО ЗАПРАШИВАЕМЫХ ИЗМЕРЕНИЙ
    # Время запроса показаний счетчика TIME_T
    Tstart = int(Timestamp).to_bytes(length=4, byteorder='little')

    #  ФОРМИРУЕМ КОЛИЧЕСТВО ЗАПРАШИВАЕМЫХ ИЗМЕРЕНИЙ
    NumTests = int(NumTests).to_bytes(length=1, byteorder='little')

    #
    # # ---------- ФОРМИРУЕМ КОМАНДУ ----------
    data_request = NSH + Tstart + NumTests
    command = FormCommand(type_command=type_command, data=data_request).command

    # ---------- ФОРМИРУЕМ ПРЕДПОЛАГАЕМЫЙ ОТВЕТ ----------
    answer_data_expected = form_data_to_GETTESTS(answer_data=Generate_data_GETLP_dict)

    # Формируем байтовую строку нагрузочных байтов
    data = code_data_to_GETTESTS(answer_data=answer_data_expected)
    # Формируем предполагаемый ответ
    Answer_expected = Constructor_Answer(data)
    # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
    Answer = Setup(command=command).answer

    print('Answer------------>', Answer)
    # # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------
    # # ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА
    Answer['answer_data'] = decode_data_to_GETTESTS(
        answer_data=Answer['answer_data']
    )

    print(Answer['answer_data'])
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
test_GETTESTS(NumTests=1)
