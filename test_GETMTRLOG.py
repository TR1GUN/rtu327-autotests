from Service.Setup import Setup
from Service.Former_Command import FormCommand
from Service.Constructor_Answer import Constructor_Answer
from Service.Service_function import total_assert, assert_answer_data
from copy import deepcopy


# -------------------------------------------------------------------------------------------------------------------
#                                       GETMTRLOG
#
#                            Запрос журнала событий по счетчикам
# -------------------------------------------------------------------------------------------------------------------
def test_GETMTRLOG(RecordTypeId: list =
                   ["ElJrnlPwr", "ElJrnlTimeCorr", "ElJrnlReset", "ElJrnlOpen",
                    "ElJrnlPwrA", "ElJrnlPwrB", "ElJrnlPwrC"],
                   count_timestamp: int = 2):
    """
    Получение значений ЖУРНАЛОВ

    Крайне важная штука

    НЕОБХОДИМО ЗАДАТЬ ОДИН ЖУРНАЛ
    """
    import struct
    # Определяем тип команды
    type_command = 'GETMTRLOG'


    # ПРОВЕРЯЕМ ТИП ДАННЫХ ДА
    assert ('ElJrnlPwr' in RecordTypeId) or ('ElJrnlTimeCorr' in RecordTypeId) or ('ElJrnlReset' in RecordTypeId) or \
           ('ElJrnlOpen' in RecordTypeId) or \
           ('ElJrnlPwrA' in RecordTypeId) or ('ElJrnlPwrB' in RecordTypeId) or ('ElJrnlPwrC' in RecordTypeId), \
        'НЕ ВЕРНО ЗАДАН ТИП ДАННЫХ '
    # Первое что делаем - генерируем необходимые нам данные
    from Service.Generator_Data import GenerateGETMTRLOG

    ElectricEnergyValues = GenerateGETMTRLOG(Count_timestamp=count_timestamp, RecordTypeId=RecordTypeId)
    # получаем данные
    Generate_data_dict = deepcopy(ElectricEnergyValues.GETMTRLOG)
    Serial = deepcopy(ElectricEnergyValues.Serial)


    # Формируем команду
    from Service.Service_function import get_form_NSH, decode_data_to_GETMTRLOG, code_data_to_GETMTRLOG

    # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
    # БЕРЕМ ТАЙМШТАМП
    Timestamp = []
    for i in Generate_data_dict:
        Timestamp.append(Generate_data_dict[i].get('Timestamp'))
    Timestamp = min(Timestamp)

    print('Timestamp --->', Timestamp)

    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)

    # Запросить события с отметками времени  больше Tstart TIME_T
    Tstart = int(Timestamp).to_bytes(length=4, byteorder='little')

    # Максимальное кол-во запрашиваемых событий INT16
    Cnt = count_timestamp * len(RecordTypeId)
    Cnt = int(Cnt).to_bytes(length=2, byteorder='little', signed=True)
    # ---------- ФОРМИРУЕМ КОМАНДУ ----------
    data_request = NSH + Tstart + Cnt
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
    Answer['answer_data'] = decode_data_to_GETMTRLOG(answer_data=Answer['answer_data'])
    # # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    # Answer_expected['answer_data'] = answer_data_expected
    #
    # # ------------------->
    # print(Answer_expected['answer_data'])
    print(Answer['answer_data'])
    # # ------------------->
    #
    # # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    # assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])
    #
    # # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    # total_assert(answer_uspd=Answer, answer_normal=Answer_expected)

test_GETMTRLOG()
