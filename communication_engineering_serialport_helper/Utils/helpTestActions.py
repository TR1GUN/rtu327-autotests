import datetime

from communication_engineering_serialport_helper.Drivers.logger import Log
from communication_engineering_serialport_helper.Proto.CRC16RTU import Crc16
from communication_engineering_serialport_helper.Settings import setup
from communication_engineering_serialport_helper.Utils import helpActions
from dateutil.relativedelta import relativedelta


def get_common_tags_availability(config_array, replace_sign_with_letter=False):
    """
    Теги должны идти в определенном порядке.
    Пример - метод helpActions.get_random_args()
    :param config_array: Принимает конфиг параметров данного теста. Конфиг собирается из выше указанного метода
    :return: Возвращает собранный массив основных тегов
    """

    result_array = []
    if config_array[2] == 1:
        if replace_sign_with_letter:
            result_array.append('Ap')
        else:
            result_array.append('A+')
    if config_array[3] == 1:
        if replace_sign_with_letter:
            result_array.append('Am')
        else:
            result_array.append('A-')
    if config_array[4] == 1:
        if replace_sign_with_letter:
            result_array.append('Rp')
        else:
            result_array.append('R+')
    if config_array[5] == 1:
        if replace_sign_with_letter:
            result_array.append('Rm')
        else:
            result_array.append('R-')

    return result_array


def check_common_tags(array, tags_amount, tags):
    """ Проверка основных тегов:  A+; A-; R+; R-
    :param array: Список в котором находится ответ/ часть ответа УСПД
    """
    for x in tags:
        helpActions.check_present_tags(expected_amount=1 if tags_amount == 1 else tags_amount + 1
                                       , tag_name=x, array=array, check_values=True)


def check_tags(tags_array, searching_array):
    """ Проверка тегов без добавления позиций(так реализовано в helpTestActions.check_common_tags)
    :param array: Список в котором находится ответ/ часть ответа УСПД

    !!! Добавить описание !!!
    """

    tags_counter = 0

    for x in tags_array:
        for y in searching_array:
            if y.count(x) > 0:
                tags_counter += 1
                continue

    assert tags_counter == len(tags_array)


def check_additional_tags(array,
                          check_additional_tags=False,
                          check_FL_tag=False,
                          check_JRNL_tag=False,
                          check_JRNL_USPD_tag=False):
    """Проверка наличия/количества остальных тегов
    :param array: Список в котором находится ответ/ часть ответа УСПД
    """

    if check_additional_tags:
        helpActions.check_present_tags(expected_amount=3, tag_name='U',
                                   array=array, check_values=True)
        helpActions.check_present_tags(expected_amount=3, tag_name='I'
                                   , array=array, check_values=True)
        helpActions.check_present_tags(expected_amount=4, tag_name='CF',
                                   array=array, check_values=True)
        helpActions.check_present_tags(expected_amount=4, tag_name='P', array=array)
        helpActions.check_present_tags(expected_amount=4, tag_name='Q', array=array)
        helpActions.check_present_tags(expected_amount=4, tag_name='S', array=array)
        helpActions.check_present_tags(expected_amount=3, tag_name='Ang',
                                   array=array, check_values=True)

        helpActions.check_present_single_tag(tag_name='F', array=array, check_values=True)

    if check_FL_tag:
        fl_string = helpActions.get_line_from_array(array=array, string='FL')
        fl_parameters_array = fl_string.split()[1].split(';')

        assert len(fl_parameters_array) == 4
        assert fl_parameters_array[0] in ['S','W','']
        assert fl_parameters_array[1] in ['P','']
        assert fl_parameters_array[2] in ['O','']
        assert fl_parameters_array[3] in ['M','']

    if check_JRNL_tag:
        jrnl_string = helpActions.get_line_from_array(array=array, string='JRNL')
        jrnl_value = jrnl_string.split()[1]

        assert str(jrnl_value).strip() in ['0','1','128']

    if check_JRNL_USPD_tag:
        jrnl_string = helpActions.get_line_from_array(array=array, string='JRNL')
        jrnl_number = jrnl_string.split()[0][4:].strip()
        jrnl_value = jrnl_string.split()[1]
        if jrnl_number in ['1','3','4','6','10','14','15','23','24','26','27','28']: assert str(jrnl_value).strip() in ['0','1']
        if jrnl_number == '2': assert str(jrnl_value).strip() in ['0','1','2','3','4','5','6','7']
        if jrnl_number == '11': assert str(jrnl_value).strip() in ['0','1','2','3','4','5']
        if jrnl_number == '12': assert str(jrnl_value).strip() in ['0','1','2','3','4','5','6']
        if jrnl_number == '13': assert str(jrnl_value).strip() in ['0','1','2','3','4']
        if jrnl_number == '16': assert str(jrnl_value).strip() in ['0','1','2']
        if jrnl_number == '17': assert str(jrnl_value).strip() in ['0','1','2','3']
        if jrnl_number == '18': assert str(jrnl_value).strip() in ['0','1','2','3']
        if jrnl_number == '19': assert str(jrnl_value).strip() in ['0','1','2']
        if jrnl_number == '20': assert str(jrnl_value).strip() in ['0','1','2','3','4','5']
        if jrnl_number == '21': assert str(jrnl_value).strip() in ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']
        if jrnl_number == '22': assert str(jrnl_value).strip() in ['0','1','2','3','4']
        if jrnl_number == '25': assert str(jrnl_value).strip() in ['0','1','2','3','4','5','6','7','8','9','10','11','12']

def check_tag_position(searching_array, tag_array, expected_position, searching_tag):
    """
    Поиск позиции строки тега в searching_array.

    :param searching_array: Список в котором находится ответ/ часть ответа УСПД
    :param tag_array: Строка с искомым тегом, взятая из массива searching_array
    :param expected_position: Ожидаемая позиция tag_array в searching_array
    :param searching_tag: Искомый тег
    :return:
    """
    # try:
    #     assert searching_array.index(tag_array) == expected_position, "can't find " + searching_tag + " line"
    # except:
    #     assert searching_array.index(tag_array) == expected_position - 2, "can't find " + searching_tag + " line"
    assert searching_array.index(tag_array) == expected_position, "can't find " + searching_tag + " line"


def check_device(settings, all_strings_answer_array, searching_array):
    """
    Проверка первой строки - типа : <UM-40RTU.2 Ver.30<
    :param settings: Файл настроек УСПД. Данные читаются из Settings / settings.xml
    :param all_strings_answer_array: Список всех строк ответа УСПД
    :param searching_array: Список в котором находится ответ/ часть ответа УСПД
    """

    new_uspd_version = False
    if str(settings.dev).count('USPD UM-RTUMP') > 0:
        new_uspd_version = True

    device = str(settings.dev) + ' Ver.'
    if new_uspd_version is False:
        device += str(settings.swver)

    assert all_strings_answer_array.count(device) > 0, "can't find device line"
    if new_uspd_version is False:
        assert searching_array.index(device) == 0, "device line have other name/version"
    else:
    # Временный костыль - просмотр позиции УСПД
        uspd_name_ver_line_position = 0
        for x in searching_array:
            if x.strip().startswith('USPD UM-RTUMP'):
                assert uspd_name_ver_line_position == 0, "device line have other name/version"
                break
        uspd_name_ver_line_position += 1


def check_control_summ(all_strings_for_conrtoll_sum, expected_conrtoll_sum):
    """
    Проверка контрольной суммы, пришедшей от УСПД.
    Ответ превадрительно надо отформатировать. Пример - all_strings.replace('\n', '')[:-4].
    В данном примере удалили все переносы строк('\n'), а также саму контрольную сумму(
    чтобы посчитать и сравнить контрольные суммы).
    :param all_strings_for_conrtoll_sum: Ответ УСПД.
    """
    all_strings_controll_sum = str(Crc16().makeCRC16(all_strings_for_conrtoll_sum).hex())
    assert expected_conrtoll_sum.lower() == all_strings_controll_sum.lower(), "different control summ"


def check_end_line(searching_array):
    """
    Проверка последней строки - (END)
    :param searching_array: Список в котором находится ответ/ часть ответа УСПД
    """
    end_and_controll_summ_string = helpActions.get_line_from_array(array=searching_array, string='END')
    assert searching_array.index(end_and_controll_summ_string) == len(
        searching_array) - 1, "can't find END line"
    assert len(end_and_controll_summ_string.split(' ')[1]) == 4, "control summ not composed of 4 characters"


def check_ID_line(searching_array, expected_position=0):
    """
    Проверка ID строки
    :param expected_position: Ожидаемое место в списке searching_array
    :param searching_array: Список в котором находится ответ/ часть ответа УСПД
    """
    id_string_array = helpActions.get_line_from_array(array=searching_array, string='ID')
    id_string_array_values = id_string_array.split()[1].split(';')
    assert (len(id_string_array_values) == 5), "ID line arguments not equal 5"
    check_tag_position(searching_array=searching_array,
                       tag_array=id_string_array,
                       expected_position=expected_position,
                       searching_tag='ID')


def check_DT_line(searching_array, expected_position=3):
    """
    Проверка DT строки
    :param expected_position: Ожидаемое место в списке searching_array
    :param searching_array: Список в котором находится ответ/ часть ответа УСПД
    """
    dt_string_array = helpActions.get_line_from_array(array=searching_array, string='DT')
    dt_string_array_values = str(dt_string_array.split()[1:]).replace(':', ' ').replace('.', ' ').split(' ')
    assert (len(dt_string_array_values) == 8), "DT line arguments not equal 5"
    check_tag_position(searching_array=searching_array,
                       tag_array=dt_string_array,
                       expected_position=expected_position,
                       searching_tag='DT')


def check_TD_line(searching_array, expected_position=4):
    """
    Проверка TD строки
    :param expected_position: Ожидаемое место в списке searching_array
    :param searching_array: Список в котором находится ответ/ часть ответа УСПД
    """
    td_string = helpActions.get_line_from_array(array=searching_array, string='TD')
    # Проверка что в теге значение это цифра
    float(td_string.split(' ')[1])
    check_tag_position(searching_array=searching_array,
                       tag_array=td_string,
                       expected_position=expected_position,
                       searching_tag='TD')

def compare_time(fromDate, toDate):
    """
    Сравнение времени.
    Формат времени чч:мм:сс
    :param firstTime: Первое время
    :param secondTime: Второе время
    :return: Возвращает(в виде массива) время.
    """

    fromDate_array = [int(x) for x in str(fromDate).split(':')]
    toDate_array = [int(x) for x in str(toDate).split(':')]

    if fromDate_array[0] >= toDate_array[0] and fromDate_array[1] >= toDate_array[1]:
        if len(fromDate_array) == 3 and len(toDate_array) == 3:
             if fromDate_array[2] >= toDate_array[2]:
                 return [toDate, fromDate]
        return [toDate, fromDate]
    else:
        return [toDate, toDate]


def get_from_to_between_date(toDate, fromDate, not_include_current_day=False):
    """
    Проврека дат toDate,fromDate.
    Если fromDate > toDate , даты меняются местами.

    Пример использования метода - тест : READDAY_RANDOMRANGE
    :param toDate: время С
    :param fromDate: время По
    :return: Возвращает список где, [0]- toDate, [1]-fromDate, [2]-difference_between_days
    """
    fromDateArray = [int(x) for x in fromDate.split('.')]
    toDateArray = [int(x) for x in toDate.split('.')]
    fromDateTime = datetime.datetime(year=2000 + fromDateArray[0], month=fromDateArray[1], day=fromDateArray[2])
    toDateTime = datetime.datetime(year=2000 + toDateArray[0], month=toDateArray[1], day=toDateArray[2])

    if fromDateTime > toDateTime:
        fromDate, toDate = toDate, fromDate
        difference_between_days = (fromDateTime - toDateTime).days
    else:
        difference_between_days = (toDateTime - fromDateTime).days

    if not_include_current_day:
        current_day = datetime.datetime.now()
        fromDateArray = [int(x) for x in fromDate.split('.')]
        toDateArray = [int(x) for x in toDate.split('.')]
        fromDateTime = datetime.datetime(year=2000 + fromDateArray[0], month=fromDateArray[1], day=fromDateArray[2])
        toDateTime = datetime.datetime(year=2000 + toDateArray[0], month=toDateArray[1], day=toDateArray[2])

        if fromDateTime.month == current_day.month \
                and fromDateTime.year == current_day.year \
                and fromDateTime.day == current_day.day:
            fromDateTime = fromDateTime + datetime.timedelta(days=-1)
            fromDate = str(fromDateTime.year)[2:] + '.' + str(fromDateTime.month) + '.' + str(fromDateTime.day)
            # Работаем с 2 последними цифрами года

        if toDateTime.month == current_day.month \
                and toDateTime.year == current_day.year \
                and toDateTime.day == current_day.day:
            toDateTime = toDateTime + datetime.timedelta(days=-1)
            toDate = str(toDateTime.year)[2:] + '.' + str(toDateTime.month) + '.' + str(toDateTime.day)
            # Работаем с 2 последними цифрами года

    return [fromDate, toDate, difference_between_days]


def get_from_to_between_date_only_months(toDate, fromDate, not_include_current_month=False):
    """
    Проврека дат toDate,fromDate.
    Если fromDate > toDate , даты меняются местами.

    Пример использования метода - тест : READMONTH_RANDOMRANGE
    :param toDate: время С
    :param fromDate: время По
    :return: Возвращает список где, [0]- toDate, [1]-fromDate, [2]-difference_between_months
    """
    fromDateArray = [int(x) for x in fromDate.split('.')]
    toDateArray = [int(x) for x in toDate.split('.')]
    fromDateTime = datetime.datetime(year=2000 + fromDateArray[1], month=fromDateArray[0], day=1)
    toDateTime = datetime.datetime(year=2000 + toDateArray[1], month=toDateArray[0], day=1)
    if fromDateTime > toDateTime:
        fromDate, toDate = toDate, fromDate
        difference_between_months = relativedelta(months=(fromDateArray[1] * 12 + fromDateArray[0]) -
                                                         (toDateArray[1] * 12 + toDateArray[0])).months
    else:
        difference_between_months = relativedelta(months=(toDateArray[1] * 12 + toDateArray[0]) -
                                                         (fromDateArray[1] * 12 + fromDateArray[0])).months

    if not_include_current_month:
        current_day = datetime.datetime.now()
        fromDateArray = [int(x) for x in fromDate.split('.')]
        toDateArray = [int(x) for x in toDate.split('.')]
        fromDateTime = datetime.datetime(year=2000 + fromDateArray[1], month=fromDateArray[0], day=1)
        toDateTime = datetime.datetime(year=2000 + toDateArray[1], month=toDateArray[0], day=1)

        if fromDateTime.month == current_day.month and fromDateTime.year == current_day.year:
            fromDateTime = fromDateTime + relativedelta(months=-1)
            fromDate = str(fromDateTime.month) + '.' + str(fromDateTime.year)[
                                                       2:]  # Работаем с 2 последними цифрами года

        if toDateTime.month == current_day.month and toDateTime.year == current_day.year:
            toDateTime = toDateTime + relativedelta(months=-1)
            toDate = str(toDateTime.month) + '.' + str(toDateTime.year)[2:]  # Работаем с 2 последними цифрами года

    return [fromDate, toDate, difference_between_months]


def is_only_one_of_date_has_current_month(fromDate, toDate):
    """
    Проверка, присутствует ли текущий месяц, только в одной из дат.
    Формат даты мм.гг

    :return: Возвращает boolean
    """
    fromDateArray = [int(x) for x in fromDate.split('.')]
    toDateArray = [int(x) for x in toDate.split('.')]
    current_date = datetime.datetime.now()

    """ Год приходит с последними 2-мя цифрами. Нужно добавить 2000 """
    two_thousand_year = 2000
    fromDateArray[1] = fromDateArray[1] + two_thousand_year
    toDateArray[1] = toDateArray[1] + two_thousand_year

    fromDate_is_currentDay = fromDateArray[0] == current_date.month and fromDateArray[1] == current_date.year
    toDate_is_not_currentDay = toDateArray[0] != current_date.month or toDateArray[1] != current_date.year
    toDate_is_currentDay = toDateArray[0] == current_date.month and toDateArray[1] == current_date.year
    fromDate_is_not_currentDay = fromDateArray[0] != current_date.month or fromDateArray[1] != current_date.year

    return (fromDate_is_currentDay and toDate_is_not_currentDay) or (
                toDate_is_currentDay and fromDate_is_not_currentDay)


def send_writeItemParam_command(args, logger, serial_port=None,
                                tcp_ip=None, tcp_port=None,tcp_timeout=None, answer_size=65536):
    """ Комманда для записи параметров"""
    answer = helpActions.send_command(
        password=setup.Settings().pwd3, command='WRITEITEMPARAM', args_list=args,
        serial_port=serial_port,
        tcp_ip=tcp_ip, tcp_port=tcp_port, answer_size=answer_size,
        logger=logger,
        tcp_timeout=tcp_timeout)
    return answer


def send_readItemParam_command(logger, serial_port=None,
                               tcp_ip=None, tcp_port=None,tcp_timeout=None, answer_size=65536):
    """ Комманда для считывания параметров"""
    item_param = helpActions.send_command(
        password=setup.Settings().pwd3, command='READITEMPARAM',
        serial_port=serial_port,
        tcp_ip=tcp_ip, tcp_port=tcp_port, answer_size=answer_size,
        logger=logger,
        tcp_timeout=tcp_timeout)
    return item_param


def send_rarchDepth_command(serial_port=None,
                            tcp_ip=None, tcp_port=None, answer_size=65536):
    """ Комманда для считывания настроек глубины хранимых данных """
    rarch_depth = helpActions.send_command(
        password=setup.Settings().pwd3, command='RARCHDEPTH',
        serial_port=serial_port,
        tcp_ip=tcp_ip, tcp_port=tcp_port, answer_size=answer_size)
    return rarch_depth


def get_formatted_time_inString(joiner='-', date=datetime.datetime.now(), deep_date=6):
    """ Добавить описание """
    return joiner.join(str(date).replace(':', ' ').
             replace('.', ' ').replace('-', ' ').split()[:deep_date])


def get_logger_with_testArgs(log_file_name,check_args):
    """ Добавить описание """
    logger = Log(log_file_name + ' ', get_formatted_time_inString())
    logger.write_log_info('Start test time : ' + str(datetime.datetime.now()) + '\n'
                              + 'Test arguments : ' + str(check_args) + '\n')
    return logger