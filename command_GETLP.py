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
def command_GETLP(Qp: bool = True, Qm: bool = True, Pp: bool = True, Pm: bool = True, Kk: int = 1):
    """
    Получение Профиля мощности?
    """
    # Определяем тип команды
    type_command = 'GETLP'

    cTime = 30
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
                                              Kanal={"Qp": Qp, "Qm": Qm, "Pm": Pm, "Pp": Pp, })

    # Формируем байтовую строку нагрузочных байтов
    data = code_data_to_GETLP(answer_data=answer_data_expected,
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
    print('Answer_expected',Answer_expected['answer_data'])
    print('Answer',Answer['answer_data'])
    # ------------------->
    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)

# -------------------------------------------------------------------------------------------------------------------
#                            Запрос замеров параметров электросети.
# -------------------------------------------------------------------------------------------------------------------
command_GETLP(Kk=50, Qp=False, Qm=True, Pm=True, Pp=True)

