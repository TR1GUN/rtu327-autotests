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
def command_GETTESTS():
    """
    Получение Профиля мощности?
    """
    # Определяем тип команды
    type_command = 'GETTESTS'
    NumTests: int = 1
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETTESTS
    # ГЕНЕРИРУЕМ 3 таймштампа
    ElectricPowerValues = GenerateGETTESTS(Count_timestamp=4)
    # # получаем данные
    Generate_data_dict = deepcopy(ElectricPowerValues.GETTESTS)
    Serial = deepcopy(ElectricPowerValues.Serial)
    # ---------- ОТСИКАЕМ ЛИШНИЕ ДАННЫЕ  ----------

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    from Service.Service_function import get_form_NSH, decode_data_to_GETTESTS, code_data_to_GETTESTS, \
        form_data_to_GETTESTS
    Timestamp_list = []
    for i in Generate_data_dict:
        Timestamp_list.append(Generate_data_dict[i].get('Timestamp'))
    print(Timestamp_list)
    Timestamp = min(Timestamp_list)
    # ОТСИКАЕМ ЛИШНИЕ ДАННЫЕ
    # БЕРЕМ ТАЙМШТАМП
    Timestamp = []
    for i in Generate_data_dict:
        Timestamp.append(Generate_data_dict[i].get('Timestamp'))
    # print('ЧТО ЕСТЬ ',Timestamp)
    Timestamp.remove(max(Timestamp))
    Timestamp.remove(min(Timestamp))
    Timestamp = Timestamp.pop()
    # и вытаскиваем данные

    Generate_data_dict = Generate_data_dict.get(Timestamp)


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
    answer_data_expected = form_data_to_GETTESTS(answer_data={Timestamp:Generate_data_dict})

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


    # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    Answer_expected['answer_data'] = answer_data_expected

    # ------------------->
    print('Answer_expected ==>',Answer_expected['answer_data'])
    print('Answer          ==>',Answer['answer_data'])
    # ------------------->
    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)


# -------------------------------------------------------------------------------------------------------------------
#                            Запуск тестов - Если идет прогон по Pytest - Закоментировать
# -------------------------------------------------------------------------------------------------------------------
command_GETTESTS()
