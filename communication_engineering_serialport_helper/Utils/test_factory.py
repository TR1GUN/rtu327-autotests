import datetime
import random

from dateutil.relativedelta import relativedelta

from Drivers import serialPort, port
from Settings import setup
from Utils import helpActions, helpTestActions

settings = setup.Settings()


def check_common_part(command, args, log_file_name,
                      without_send_writeItemParam_command=False,
                      without_send_send_readItemParam_command=False,
                      fromDate=None, toDate=None,
                      fromDateRandomTime=False, toDateRandomTime=False,
                      fromDateMonth=None, toDateMonth=None,
                      tcp_connection=None,
                      tcp_timeout=None,
                      args_before=None, args_after=None,   #array_only
                      with_counter=True # Проверка ID счетчика. Иногда наличие счетчиков не нужно
                      ):
    """
    :param args:  counters, t, Ap, Am, Rp, Rm, fromDate, toDate - в виде массива
    :return:
    """
    check_args = args
    oneDate = fromDate is not None and toDate is None
    twoDates = fromDate is not None and toDate is not None
    oneDateMonth = fromDateMonth is not None and toDateMonth is None
    twoDatesMonth = fromDateMonth is not None and toDateMonth is not None

    """ Сравнение полученных дат """
    if oneDate:  # Данное условие добавленно чтобы исключить текущий день
        fromDate = helpTestActions.get_from_to_between_date(
            fromDate=fromDate, toDate=fromDate, not_include_current_day=True)[0]
    if twoDates:
        fromDate, toDate, difference_between_days = helpTestActions.get_from_to_between_date(
            fromDate=fromDate, toDate=toDate, not_include_current_day=True)
    if oneDateMonth:  # Данное условие добавленно чтобы исключить текущий месяц
        fromDate = helpTestActions.get_from_to_between_date_only_months(fromDate=fromDateMonth, toDate=fromDateMonth,
                                                                        not_include_current_month=True)[0]
    if twoDatesMonth:
        fromDate, toDate, difference_between_months = \
            helpTestActions.get_from_to_between_date_only_months(fromDate=fromDateMonth, toDate=toDateMonth
                                                                 , not_include_current_month=True)

    if fromDateRandomTime:
        fromDate_time = helpActions.get_random_multiple_to_30_minutes_time(zero_seconds=True)
        fromDate += ' ' + fromDate_time + ' 0'  # 0 - Флаг сезона

        if toDateRandomTime:
            toDate_time = helpActions.get_random_multiple_to_30_minutes_time(zero_seconds=True)
            fromDate_time, toDate_time = helpTestActions.compare_time(fromDate_time,
                                                                      toDate_time)

            """ Удаляем предыдущее записанное значение fromDate """
            fromDate = fromDate[:-11]
            fromDate += ' ' + fromDate_time + ' 0'  # 0 - Флаг сезона
            toDate += ' ' + toDate_time + ' 0'  # 0 - Флаг сезона
            """" ---------------------------------------------- """
            """ Высчитываем разницу в датах. Получаем количество DT строк(+-1).
                Кратно 30 минут - срезы каждые 30 минут """
            """ Вынести в метод? """
            fromDate_arrays = [int(x) for x in fromDate[:-2].replace('.', ' ').replace(':', ' ').split()]
            toDate_arrays = [int(x) for x in toDate[:-2].replace('.', ' ').replace(':', ' ').split()]
            fromDate_datetime = datetime.datetime(year=fromDate_arrays[0], month=fromDate_arrays[1],
                                                  day=fromDate_arrays[2],
                                                  hour=fromDate_arrays[3], minute=fromDate_arrays[4])
            toDate_datetime = datetime.datetime(year=toDate_arrays[0], month=toDate_arrays[1], day=toDate_arrays[2],
                                                hour=toDate_arrays[3], minute=toDate_arrays[4])
            difference_in_dates = relativedelta(toDate_datetime, fromDate_datetime)
            difference_days = difference_in_dates.days
            difference_hours = difference_in_dates.hours
            difference_minutes = difference_in_dates.minutes
            searching_dt_line_number = (
                    difference_days * 48 + difference_hours * 2 + (1 if difference_minutes == 30 else 0))
            # print(str(searching_dt_line_number))
            # print(str(searching_dt_line_number))
            # print(str(searching_dt_line_number))
            # print(str(searching_dt_line_number))


    """ Создание логгера """
    inner_logger = helpTestActions.get_logger_with_testArgs(
        log_file_name=log_file_name, check_args=str(check_args)
                                                + ' date : ' + str(fromDate) + '-' + str(toDate))


    """ COM соединение """
    """ TCP/IP соединение """
    tcp_ip = None
    tcp_port = None
    com = None

    if tcp_connection:
        tcp_ip = tcp_connection.split(':')[0]
        tcp_port = tcp_connection.split(':')[1]
    else:
        com = serialPort.SerialPort(baudrate=9600, portnum=settings.port, timeout=1)
        port.portopen(com)

    """ Комманда для записи параметров. Работает если стоит False(по дефолту)"""
    if without_send_writeItemParam_command is False:
       answer = helpTestActions.send_writeItemParam_command(
               args=check_args, serial_port=com, logger=inner_logger,
               tcp_ip=tcp_ip, tcp_port=tcp_port, tcp_timeout=tcp_timeout)
       assert answer.count('OK') > 0, "there was no OK in answer"

    """ Комманда для считывания параметров. Работает если стоит False(по дефолту)"""
    if without_send_send_readItemParam_command is False:
       item_param = helpTestActions.send_readItemParam_command(
           serial_port=com, logger=inner_logger, tcp_ip=tcp_ip, tcp_port=tcp_port,tcp_timeout=tcp_timeout)
       number_of_counters = int(item_param.split(';')[0].split('=')[1].strip())

       """ Проверка количества счетчиков. Если счетчиков < 1, валим тесты."""
       assert number_of_counters > 0, 'counters number less than 1'

    """ Комманда для считывания ответа"""
    result_send_command = command
    if oneDate or oneDateMonth:
        result_send_command += '=' + fromDate
    elif twoDates or twoDatesMonth:
        result_send_command += '=' + fromDate + ' ' + toDate

    #result command here
    #Удалить???
    if args_before is not None: # Очень топорно
        args_in_front = ''
        for x in args_before: args_in_front += str(x)+';'
        result_send_command_array = result_send_command.split('=') #Разбиваем строк и вставляем перед знаком '='
        result_send_command = result_send_command_array[0] +'=' + args_in_front + result_send_command_array[1] #Добавляем назад знак '='

    if args_after is not None:
        args_after_str=''
        for x in args_after: args_after_str += str(x)+';'
        result_send_command = result_send_command + args_after_str[:-1] # Удаляем последний ;

    command = helpActions.get_command(password=settings.pwd3, command=result_send_command)
    # all_strings = helpActions.send_command(password=settings.pwd3, command=result_send_command,
    #                          tcp_ip=tcp_ip,tcp_port=tcp_port,serial_port=com)
    # first_byte_get_time = datetime.datetime.now() # undone

    if tcp_connection:
        all_strings = serialPort.SerialPort().tcp_connect_read(uspd_server_ip=tcp_ip,
                                                               uspd_server_port=tcp_port,
                                                               command=command,
                                                               timeout=tcp_timeout)
        first_byte_get_time = datetime.datetime.now() # undone
    else:
        com.write(command)
        all_strings, first_byte_get_time = com.read_data_return_text(firstNotNullByteGetTime=True)
        port.portclose(com)



    inner_logger.write_log_info('\ntime : ' + str(first_byte_get_time) + '\n'
          + 'command : ' + command.decode('utf-8').replace('\n', '') + '\n'
          + 'answer:\n' + all_strings + '\n')


    all_strings_for_conrtoll_sum = all_strings.replace('\n', '')[:-4]
    conrtoll_sum = all_strings.replace('\n', '')[-4:].strip()

    # Строки в массив
    array_of_string = all_strings.split('\n')
    result_string = helpActions.get_normal_text(array_of_string)
    file_text_array = result_string.split('\n')  # Убираем в конце \n

    """ Check - is this USPD new ver. or old ver. """
    global new_uspd_version
    new_uspd_version = False
    """ Check - is this USPD new ver. or old ver. """
    if file_text_array[0].count('USPD UM-RTUMP') > 0:
        new_uspd_version = True


    """test_check_first_line"""
    helpTestActions.check_device(settings=settings, all_strings_answer_array=all_strings,
                                 searching_array=file_text_array)

    """test_check_control_summ"""
    helpTestActions.check_control_summ(all_strings_for_conrtoll_sum=all_strings_for_conrtoll_sum,
                                       expected_conrtoll_sum=conrtoll_sum)

    """test_check_end_line"""
    helpTestActions.check_end_line(searching_array=file_text_array)

    """ Узнаем id счетчика - для новых успд - для теста журнала """
    current_counter_id=None
    if with_counter: # Провреяем строчки ID - номер счетчика. Иногда наличие счетчика не нужно, например проверка журналов самого УСПД. По дефолту True
        current_ID_line = file_text_array[2]
        current_counter_id = int(current_ID_line.split()[1].split(';')[0])

    """
    Ключи
    """
    map = {}
    map['file_text_array'] = file_text_array
    if without_send_send_readItemParam_command is False:
        map['number_of_counters'] = number_of_counters
    map['inner_logger'] = inner_logger
    map['new_uspd_version']=new_uspd_version
    map['current_counter_id'] = current_counter_id
    if twoDates:
        map['difference_between_days'] = difference_between_days
    if twoDatesMonth:
        map['difference_between_months'] = difference_between_months
    if toDateRandomTime:
        map['searching_dt_line_number'] = searching_dt_line_number
    return map


""" Работает корретно только с DT """
""" Работает корретно только с DT """
""" Работает корретно только с DT """
def check_meters_full(check_args, number_of_counters, file_text_array,
                      check_entire_period=None,
                      check_previous_and_current_time=True,
                      check_one_month_or_day=False,
                      check_random_period=None,  # ???
                      check_DT_line=False,
                      check_TD_line=False,
                      check_DP_args=False,
                      check_common_tags=None,
                      check_additional_tags=False,
                      check_FL_tags=False,
                      check_JRNL_tags=False,
                      ):
    id_positions = helpActions.get_count_positions_in_file_text_array(array=file_text_array, count_tag='ID')

    for x in range(number_of_counters):
        try:
            """ Если новое успд, считать надо по-другому """
            if check_additional_tags and new_uspd_version is True:
                current_file_text_array = file_text_array[id_positions[(x*2)]: id_positions[(x*2)+1]]
            else:
                current_file_text_array = file_text_array[id_positions[x]: id_positions[x + 1]]

        except:  # последний ID участок
            """ Если новое успд, считать надо по-другому """
            if check_additional_tags and new_uspd_version is True:
                current_file_text_array = file_text_array[id_positions[(x*2)]:]
            else:
                current_file_text_array = file_text_array[id_positions[x]:]


        # print(str(current_file_text_array))

        """check ID line"""
        helpTestActions.check_ID_line(searching_array=current_file_text_array)
        # expected_position == 2 ??

        # """ Узнаем id счетчика - для новых успд - для теста журнала """
        # if new_uspd_version:
        #     current_ID_line = current_file_text_array[0]
        #     current_counter_id = int(current_ID_line.split()[1].split(';')[0])

        """ Нахождение всех позиций DT и прогонка по ним """
        all_dt_lines_for_this_meter = helpActions.get_count_positions_in_file_text_array(
            array=current_file_text_array, count_tag='DT')

        """Весь период"""
        if check_entire_period:
            assert (len(all_dt_lines_for_this_meter) >= helpActions.get_arch_depth_param(check_entire_period)), \
                "wrong number of " + check_entire_period

        """ Один день / месяц """
        if check_one_month_or_day:
            assert (len(all_dt_lines_for_this_meter) == 1), "there more/less than 1 day/month"

        """ За несколько дней / месяцев """
        """ + / - 1 в какой момент добавлять ?? """

        # """
        # # Проверка, присутствует ли текущий месяц, только в одной из дат.
        # # """
        # if helpTestActions.is_only_one_of_date_has_current_month(fromDate=fromDate, toDate=toDate):
        #     additional_number = 0
        # else:
        #     additional_number = 1

        if check_random_period:

            print('all_dt_lines_for_this_meter : ' + str(len(all_dt_lines_for_this_meter)))
            print('check_random_period ' + str(check_random_period))

            try:
                assert (len(all_dt_lines_for_this_meter) == check_random_period + 1), \
                    "there more/less than " + str(check_random_period) + " lines"
            except:
                assert (len(all_dt_lines_for_this_meter) == check_random_period), \
                    "there more/less than " + str(check_random_period) + " lines"

        """ Для проверки текущего и предыдущего времени. (DT line) """
        global previous_date  # static var
        previous_date = None

        for y in range(len(all_dt_lines_for_this_meter)):
            try:
                inner_current_file_text_array = current_file_text_array[
                                                all_dt_lines_for_this_meter[y]: all_dt_lines_for_this_meter[y + 1]]
            except:  # последний ID участок
                inner_current_file_text_array = current_file_text_array[all_dt_lines_for_this_meter[y]:]


            # print(str(inner_current_file_text_array))

            """check DT line"""
            if check_DT_line:
                helpTestActions.check_DT_line(searching_array=inner_current_file_text_array,
                                              expected_position=0)

            """ Проверка текущего и предыдущего времени. Если предыдущее больше - ошибка"""
            if check_previous_and_current_time:
                if previous_date is not None:
                    current_date = helpActions.get_line_from_array(array=inner_current_file_text_array,
                                                                   string='DT').split()[1:3]
                    current_date_datetime = helpActions.parse_str_date_to_datetime(
                        date=str(current_date[0]) + ' ' + str(current_date[1]), full_date=True)
                    previous_date_datetime = helpActions.parse_str_date_to_datetime(
                        date=str(previous_date[0]) + ' ' + str(previous_date[1]), full_date=True)
                    difference_in_dates = helpActions.get_difference_in_dates(fromDate=previous_date_datetime,
                                                                              toDate=current_date_datetime)
                    assert difference_in_dates[0] >= 0, 'toDate day less than fromDate'
                    assert difference_in_dates[1] >= 0, 'toDate hour less than fromDate'
                    assert difference_in_dates[2] >= 0, 'toDate minute less than fromDate'

                    """ Текущая дата = предыдущая дата. Переход в следующий цикл """
                    previous_date = current_date
                else:
                    previous_date = helpActions.get_line_from_array(array=inner_current_file_text_array,
                                                                    string='DT').split()[1:3]

            """check TD line -- Нашли значит ок"""
            if check_TD_line:
                helpTestActions.check_TD_line(searching_array=inner_current_file_text_array,
                                              expected_position=1)

            """Проверка основных тегов - DP TESTS"""
            if check_DP_args:
                helpTestActions.check_tags(
                    tags_array=['DP' + x for x in helpTestActions.get_common_tags_availability(
                        check_args, replace_sign_with_letter=True)],
                    searching_array=inner_current_file_text_array
                )

            """Проверка основных тегов(A+, A-, R+, R-)"""
            if check_common_tags:
                helpTestActions.check_common_tags(
                    array=inner_current_file_text_array, tags_amount=check_args[1],
                    tags=[check_common_tags + x for x in helpTestActions.get_common_tags_availability(check_args)])

            """Проверка дополнительныйх тегов(Quality)"""
            if check_additional_tags and new_uspd_version is False:
                helpTestActions.check_additional_tags(array=inner_current_file_text_array,
                                                      check_additional_tags=True)

            """Проверка дополнительных тегов(FL)"""
            if check_FL_tags:
                helpTestActions.check_additional_tags(array=inner_current_file_text_array,
                                                      check_FL_tag=True)

            """Проверка дополнительных тегов(JRNL)"""
            if check_JRNL_tags:
                helpTestActions.check_additional_tags(array=inner_current_file_text_array,
                                                          check_JRNL_tag=True)

        """ Проверка дополнительных аргументов если это новый тип USPD """
        if check_additional_tags and new_uspd_version is True:
            # print('myabe - here')
            check_meters_full_without_DT(number_of_counters=number_of_counters,
                                         start_counter_position=x+1,
                                         file_text_array=current_file_text_array,
                                         check_entire_period=check_entire_period,
                                         check_one_month_or_day=check_one_month_or_day,
                                         check_random_period=check_random_period,  # ???
                                         check_additional_tags=check_additional_tags,
                                         )

""" Работает корретно только БЕЗ DT """
""" Работает корретно только БЕЗ DT """
""" Работает корретно только БЕЗ DT """
""" start_counter_position - начало отсчета счетчика """
def check_meters_full_without_DT(number_of_counters, file_text_array,
                                 start_counter_position=0,
                                 check_entire_period=None,
                                 check_one_month_or_day=False,
                                 check_random_period=None,  # ???
                                 check_additional_tags=False,
                                 ):
    id_positions = helpActions.get_count_positions_in_file_text_array(array=file_text_array, count_tag='ID')

    for x in range(number_of_counters-start_counter_position):
        # Сделано по-другому в отличие от check_meters_full()
        try:
           current_file_text_array = file_text_array[id_positions[x + start_counter_position]: id_positions[x + start_counter_position + 1]]
        except:  # последний ID участок
           current_file_text_array = file_text_array[id_positions[x + start_counter_position]:]

        """check ID line"""
        helpTestActions.check_ID_line(searching_array=current_file_text_array)

        """ Нахождение всех позиций DT и прогонка по ним """
        all_dt_lines_for_this_meter = helpActions.get_count_positions_in_file_text_array(
            array=current_file_text_array, count_tag='DT')

        """Весь период"""
        if check_entire_period:
            assert (len(all_dt_lines_for_this_meter) >= helpActions.get_arch_depth_param(check_entire_period)), \
                "wrong number of " + check_entire_period

        """ Один день / месяц """
        if check_one_month_or_day:
            assert (len(all_dt_lines_for_this_meter) == 1), "there more/less than 1 day/month"

        if check_random_period:
            try:
                assert (len(all_dt_lines_for_this_meter) == check_random_period + 1), \
                    "there more/less than " + str(check_random_period) + " lines"
            except:
                assert (len(all_dt_lines_for_this_meter) == check_random_period), \
                    "there more/less than " + str(check_random_period) + " lines"

        """Проверка дополнительныйх тегов(Quality)"""
        if check_additional_tags:
            helpTestActions.check_additional_tags(array=current_file_text_array,
                                                  check_additional_tags=True)


