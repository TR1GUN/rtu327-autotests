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


def command_GETSHPRM():
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

    Serial = deepcopy(Config.Serial)

    from Service.Service_function import get_form_NSH, decode_data_to_GETSHPRM, code_data_to_GETSHPRM , form_data_to_GETSHPRM

    # Формируем предполагаемый ответ
    data_SHPRM_dict = form_data_to_GETSHPRM(deepcopy(Config.GETSHPRM))

    data = code_data_to_GETSHPRM(data_SHPRM_dict=data_SHPRM_dict)
    Answer_expected = Constructor_Answer(data)

    # NSH Номер счетчика BCD5
    NSH = get_form_NSH(Serial=Serial)
    # ФОРМИРУЕМ КОМАНДУ
    command = FormCommand(type_command=type_command, data=NSH).command
    # Отправляем ее
    Answer = Setup(command=command).answer

    print('Answer , bytes\n', Answer)
    print('Answer_expected, bytes\n', Answer_expected)

    # ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА
    Answer['answer_data'] = decode_data_to_GETSHPRM(answer_data=Answer['answer_data'])
    # Answer_expected['answer_data'] = decode_data_to_GETSHPRM(answer_data=Answer_expected['answer_data'])
    # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
    Answer_expected['answer_data'] = data_SHPRM_dict

    # ------------------->
    print('Answer_expected ==>', Answer_expected['answer_data'])
    print('Answer          ==>', Answer['answer_data'])
    # ------------------->

    # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
    assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])

    # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
    total_assert(answer_uspd=Answer, answer_normal=Answer_expected)

# -------------------------------------------------------------------------------------------------------------------
#                            Запуск тестов - Если идет прогон по Pytest - Закоментировать
# -------------------------------------------------------------------------------------------------------------------
command_GETSHPRM()
