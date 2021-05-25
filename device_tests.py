"""
py -m pytest device_tests.py::RTU327::test_gettime -s -v
"""
import unittest
from USPD_RTU327ProtoFramework.main_methods.methods import send_read
from USPD_RTU327ProtoFramework.Utils.helpActions import get_normal_text
from work_with_device import *
import work_with_device


class RTU327(unittest.TestCase):

    def commands_send_helper(self, command):  ## --> private
        print(uspd_password, uspd_tcp_ip, uspd_text_protocol_tcp_port, command)
        if type(command) is list:
            all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_text_protocol_tcp_port,
                                    command=command[0], args_list=command[1], tcp_timeout=5)
        elif type(command) is str:
            all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_text_protocol_tcp_port,
                                    command=command, tcp_timeout=5)
        else:
            raise Exception('Неизвестный тип')
        return all_strings

    def test_preparation_stage(self):
        """
        пример -- 138_TRANSADD_write_2_test.py
        TRANSADD
        Команда текстового протокола - ('1','','3','1','303030303030','303030303030','0','Auto','','','','',None,None,None,'OK'),
        00000000,TRANSOPEN2050 (00000000,TRANSOPEN)
        00000000,CLEARTABLE6CF (00000000,CLEARTABLE)
        00000000,TRANSADD=1;3;60;010101010101;020202020202;0;4;6;8;0;0D1E6 (00000000,TRANSADD=1;3;60;010101010101;020202020202;0;4;6;8;0;0)
        00000000,TRANSCOMMIT48FD (00000000,TRANSCOMMIT)
        """

        ##Текстовый протокол
        # commands = ['TRANSOPEN', 'CLEARTABL', ['TRANSADD',['1','3','60','010101010101','020202020202','0','4','6','8','0','0']], 'TRANSCOMMIT']
        commands = ['TRANSOPEN',  ## Открываем соединение
                    'CLEARTABL', ['TRANSADD',
                                  ['1', '3', '60', '010101010101', '020202020202', '0', '4', '6', '8', '0', '0', '1',
                                   '1', '1']],
                    ## Последние три единички :: Syb_Rnk - Тип объекта :: N_Ob - Номер объекта :: N_Fid - Номер фидера
                    ['WARCHPRM', ['1', '1', '1', '1', '1', '1', '1', '1']], ['WSCHEDAQUAL', ['1', '0', '0', '30']],
                    ## Записываем -- для test_get_tests -- Качество сети приборов учета.
                    'TRANSCOMMIT']  ## Закрываем соединение
        """Последние три единички
            Syb_Rnk - Тип объекта
            N_Ob - Номер объекта
            N_Fid - Номер фидера
        """
        for command in commands:
            all_strings = self.commands_send_helper(command)
            print(all_strings)
            ## Проверка Ответа - пока только OK05C7??
            self.assertEqual('OK05C7', all_strings.strip())

        ## TODO
        ## Тут собирать uspd_settings.ini --> ConfigParser
        ##Далее мы просто ждем ????
        # print('!!!GOING TO SLEEP FOR 33 MINUTES!!!\n'*10)
        # time.sleep(33*60) #33 минуты -- ждем когда появятся ?? архивные данные + номер счетчика
        # print('was\\done\n'*10)

    @staticmethod
    def get_uspd_count_number():  ## Использовать для проверок
        ## TODO
        ## Возможно следует READQUAL следует заменить на другую -- чтобы меньше грузилась успд.
        all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_text_protocol_tcp_port,
                                command='READAQUAL', tcp_timeout=5)
        return all_strings.split('\n')[3]

    def test_get_version(self):
        """
        USPD_RETURN :
            Описание версии, состоящее из 6 символов:
                2 байта – старший номер версии
                2 байта – средний номер версии
                2 байта – младший номер версии
        """
        print()
        result_answer_map = send_command_and_get_answer(3)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data']
        self.assertEqual(6, len(answer_data))
        ## Ожидаемый ответ железки -- ['0x30','0x32','0x30','0x31','0x30','0x32']
        self.assertEqual(['30', '32', '30', '31', '30', '32'], result_answer_map['answer_data'])

    # @work_with_device.check_ip_args
    def test_get_time(self):
        result_answer_map = send_command_and_get_answer(114)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data'][::-1]
        result_answer_data = ''
        for x in answer_data: result_answer_data += x
        formated_device_time = int(result_answer_data, 16)
        device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        curr_datetime = datetime.datetime.now()
        device_datetime = device_datetime + datetime.timedelta(hours=3)
        difference_between_dates = abs((curr_datetime - device_datetime).total_seconds())
        self.assertTrue(difference_between_dates < 59)  # Разница, не больше 59 секунд.

    def test_bad_crc(self):
        prefix = b'\x02'  ## префикс
        first_part_of_package_size = b'\x00'  ## \x00 ++ <тут мы подсчитываем \\x > - Длина пакета \
        ordinal_number = b'\x01\x00'  ## порядковый номер
        password = b'\x00\x00\x00\x00'  ## пароль
        reserve = b'\x00\x00'  ## резерв

        wrong_command = work_with_device.create_command(prefix=prefix,
                                                        first_part_of_package_size=first_part_of_package_size,
                                                        ordinal_number=ordinal_number, password=password,
                                                        reserve=reserve,
                                                        crc=b'\xff\xff', command_number=114)
        result_answer_map = send_command_and_get_answer(send_command_raw=wrong_command)

        # print(get_crc(b'\x01\x00\x00\x00\x00\x00\x00\x00\x3c'))
        # print(get_crc(ordinal_number+password + reserve + decode_hex_to_str_hex(hex(114))))

        print(result_answer_map)
        self.assertEqual(['a0', '2f'], result_answer_map['crc'])

    def test_set_time(self):
        # TODO
        # Правильно переписывать , без дублирования test_gettime()

        hour_in_seconds = 3600
        res_hex_time = get_right_hex(hex(hour_in_seconds)[2:])
        amount_of_byte = len(res_hex_time) / 2
        result_hex_time = b''
        if amount_of_byte != 4:
            for _ in range(4 - int(amount_of_byte)):
                result_hex_time += b'\x00'
        result_hex_time += res_hex_time.encode()
        result_answer_map = send_command_and_get_answer(115,
                                                        command_params=b'\x10\x0e\x00\x00')  # 3600 + добавляем 1 час на успд

        print('lol')
        print(result_answer_map)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map

        """ Проверка """
        result_answer_map = send_command_and_get_answer(114)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data'][::-1]
        result_answer_data = ''
        for x in answer_data: result_answer_data += x
        formated_device_time = int(result_answer_data, 16)
        device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        curr_datetime = datetime.datetime.now()
        device_datetime = device_datetime + datetime.timedelta(hours=3)
        difference_between_dates = abs((curr_datetime - device_datetime).total_seconds())
        self.assertTrue(3540 < difference_between_dates < 3660)  # Разница +- 1 минута
        ## Возвращаем время назад
        result_answer_map = send_command_and_get_answer(115,
                                                        command_params=b'\xf0\xf1\xff\xff')  # 3600 + убираем 1 час на успд
        self.assertEqual('00',
                         result_answer_map[
                             'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map

    def _helper_text_protocol_answer_to_dict(self, all_strings):
        res_text_protocol_dict = {}
        array_of_string = get_normal_text(all_strings.split('\n')).split('\n')
        for line in array_of_string:
            line_array = line.split()
            if len(line_array) <= 1:
                pass
            else:
                res_text_protocol_dict[line_array[0]] = line_array[1]
        return res_text_protocol_dict

    def test_helper_test_get_maxlogid(self):
        result_answer_map = send_command_and_get_answer(101, command_params=b'\x01')
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        self.assertEqual(4, len(result_answer_map['answer_data']))
        before_generation_event = result_answer_map['answer_data']
        return dec_from_bytes_array(before_generation_event)

    def test_get_maxlogid(self):  ##
        """ Просто проверяем количество ответа - 4 байта. """
        max_log_id_before = self._helper_test_get_maxlogid()
        ## Сгенерить событие -->> проверить, что увеличился
        ## Уввеличиваем время
        result_answer_map = send_command_and_get_answer(115,
                                                        command_params=b'\x10\x0e\x00\x00')  # 3600 + добавляем 1 час на успд
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        max_log_id_after = self._helper_test_get_maxlogid()
        if max_log_id_before > 60000 and max_log_id_after < 5000:  ##случай с обнулением: -- 65535
            pass
        else:
            self.assertTrue(max_log_id_after > max_log_id_before)
        ## Возвращаем время назад
        send_command_and_get_answer(115, command_params=b'\xf0\xf1\xff\xff')  # 3600 == убираем 1 час на успд

    def test_get_log(self):
        Nsect = b'\x00\x00\x00\x01'
        # Id = b'\x00\x00\x00\x01' ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
        Id = dec_to_hex(
            self._helper_test_get_maxlogid())  ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
        Id = add_empty_bytes(Id, 4 - len(Id))  ## Доставляем до 4-х байтов
        Num = b'\x00\x01'
        result_answer_map = send_command_and_get_answer(117, command_params=Nsect + Id + Num)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        self.assertEqual(13, len(result_answer_map))

    def test_get_shprm(self):  ## Пока просто смотрим
        """серийный номер успд ?? откуда брать ??
         10 18 47 60
        """
        ##RTU327 протокол
        Nsh = work_with_device.uspd_counter_number  ## Номер счетчика
        result_answer_map = send_command_and_get_answer(112, command_params=Nsh)

        print(result_answer_map)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data']
        vers = answer_data[:2]
        typ_sh = answer_data[2]
        kt = answer_data[3:11][::-1]  ##FLOAT8 ## Надо переворачивать ??
        kn = answer_data[11:19][::-1]  ##FLOAT8 ## Надо переворачивать ??
        m = answer_data[19:27][::-1]  ##FLOAT8 ## Надо переворачивать ??
        interv = answer_data[27]
        syb_rnk = answer_data[28:32][::-1]  ##INT32 ## Надо переворачивать ??
        n_ob = answer_data[32:36][::-1]  ##INT32 ## Надо переворачивать ??
        n_fid = answer_data[36:][::-1]  ##INT32 ## Надо переворачивать ??
        self.assertEqual(40, len(answer_data))
        ## Данные сравниваются с теми, которые были записаны по текстовому протоколу - команда TRANSADD
        self.assertEqual(1.0, hex_to_double(kt))
        self.assertEqual(1.0, hex_to_double(kn))
        self.assertEqual(1.0, hex_to_double(m))
        self.assertEqual(1, hex_array_to_dec(syb_rnk))
        self.assertEqual(1, hex_array_to_dec(n_ob))
        self.assertEqual(1, hex_array_to_dec(n_fid))

    def _help_check_if_not_prevent_values(self, text_protocol_value, rtu_protocol_value):
        """Если текстовый протокол возращает ? , то сравниваем с RTU327 что он возвращает -1"""

        print(text_protocol_value, rtu_protocol_value)

        return text_protocol_value == '?' and rtu_protocol_value == -1

    def _help_get_pok_assert_equal(self, res_text_protocol_dict_value, answer_data):
        """Вынес отдельно метод сравнения, т.к. повторяется"""
        if self._help_check_if_not_prevent_values(res_text_protocol_dict_value, hex_to_double(answer_data)):
            pass
        else:
            self.assertEqual(int(float(res_text_protocol_dict_value)), int(hex_to_double(answer_data) * 1000))

    def test_get_pok(self):  ##
        """ Просто проверяем количество ответа - 8 байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """

        ## Читаем показания счетчика - по текстовому протоколу
        ## TODO
        ## ? Перенести в Текстовый протокол ?
        cur_datetime = datetime.datetime.now()

        # 1. Начало текущего месяца
        at_current_month_start = get_at_day_start_datetime(cur_datetime.day - 1)

        # 2. Начало текущего дня
        at_current_day_start = get_at_day_start_datetime()

        # 3. -6 секунд от текущего времени
        minus_six_seconds = cur_datetime - datetime.timedelta(seconds=6)

        # dates = [at_current_day_start,at_current_month_start,minus_six_seconds]
        # TODO
        # На данный момент minus_six_seconds не работает, т.к. непонятно как ее(дату) правильно сравнивать.

        dates = [at_current_day_start, at_current_month_start]
        for cur_date in dates:
            command = ['READDAY', [datetime.datetime.strftime(cur_date, '%y.%m.%d')]]

            all_strings = self.commands_send_helper(command)
            res_text_protocol_dict = self._helper_text_protocol_answer_to_dict(all_strings)

            # Вторая реализация -- проверяем все Chnl
            for _ in [1, 3, 7,
                      15]:  ## 1,3,7,15 --> постепенное заполнение битами , т.е. 0001 / 0011 / 0111 / 1111 ### 1111 -- > (R-)/(R+)/(A-)/(A+)
                Chnl = dec_to_hex(_)
                NSH = work_with_device.uspd_counter_number

                cur_day_in_bytes = get_reversed_time_bytes_by_datetime(cur_date)

                # result_answer_map = send_command_and_get_answer(113, command_params=NSH+Chnl+time_minus_month)
                result_answer_map = send_command_and_get_answer(113, command_params=NSH + Chnl + cur_day_in_bytes)
                self.assertEqual('00', result_answer_map[
                    'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
                answer_data = result_answer_map['answer_data'][::-1]

                if _ == 1:
                    answer_data_for_1 = answer_data
                    self.assertEqual(8, len(answer_data))
                    self._help_get_pok_assert_equal(res_text_protocol_dict['dA+0'], answer_data)
                elif _ == 3:
                    answer_data_for_3 = answer_data
                    self.assertTrue(
                        answer_data_for_1 == answer_data_for_3[8:])  ## ?? Спереди или сзади проверять ответ ??
                    self.assertEqual(16, len(answer_data))
                    self._help_get_pok_assert_equal(res_text_protocol_dict['dA-0'], answer_data[:8])
                elif _ == 7:
                    answer_data_for_7 = answer_data
                    self.assertTrue(
                        answer_data_for_3 == answer_data_for_7[8:])  ## ?? Спереди или сзади проверять ответ ??
                    self.assertEqual(24, len(answer_data))
                    self._help_get_pok_assert_equal(res_text_protocol_dict['dR+0'], answer_data[:8])
                elif _ == 15:
                    answer_data_for_15 = answer_data
                    self.assertTrue(
                        answer_data_for_7 == answer_data_for_15[8:])  ## ?? Спереди или сзади проверять ответ ??
                    self.assertEqual(32, len(answer_data))
                    self._help_get_pok_assert_equal(res_text_protocol_dict['dR-0'], answer_data[:8])

    def _check_if_hex_array_is_zero(self, array_byte):
        """
        Хз почему, но struct.unpack здесь ругается. Быстрый костыль.
        """
        if array_byte == ['00', '00', '00', '00', '00', '00', '00', '00']:
            return 0
        else:
            return array_byte

    def test_get_lp(self):  ##

        """ Текстовый протокол """
        res_text_protocol_dict = {}

        """ RTU-327 протокол """
        Nsh = work_with_device.uspd_counter_number
        Tstart = b'\x00\x00\x00\x00'
        Kk = b'\x01\x00'  ## ==> 1 (так пишется единица, меньшие биты впереди ?)
        for _ in [1, 3, 7,
                  15]:  ## 1,3,7,15 --> постепенное заполнение битами , т.е. 0001 / 0011 / 0111 / 1111 ### 1111 -- > (R-)/(R+)/(A-)/(A+)
            Kanal = dec_to_hex(_)
            result_answer_map = send_command_and_get_answer(111, command_params=Nsh + Kanal + Tstart + Kk)
            self.assertEqual('00', result_answer_map[
                'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
            answer_data = result_answer_map['answer_data']
            lp_temp_Cnt = answer_data[:2][::-1]
            lp_temp_Status = answer_data[2]  ## Проверять ???
            lp_temp_date_to_uspd = answer_data[3:7][::-1]  ##TLast
            lp_temp_date_to_uspd_as_datetime = date_from_seconds(
                hex_array_to_dec(lp_temp_date_to_uspd)) + datetime.timedelta(
                hours=3)  ## Прибавить 3 часа , почему-то по UTC .. CNT*30 отнимается.
            lp_temp_date_from = get_str_date_from_datetime(lp_temp_date_to_uspd_as_datetime - datetime.timedelta(
                minutes=30 * hex_array_to_dec([lp_temp_Cnt[1]])))  ## Cnt скорее всего не правильно считаю
            lp_temp_date_to = get_str_date_from_datetime(lp_temp_date_to_uspd_as_datetime)
            lp_temp_Val = answer_data[7:-1]
            lp_temp_Stat = answer_data[-1]  ## Проверять ???
            temp_vars = vars().copy()  ## Делаем копию переменных, т.к. список ?почему-то? изменяется в реальном времени.
            res_array = {}
            for temp_var in temp_vars:
                if temp_var.startswith('lp_temp_'):
                    res_array[_] = temp_vars[temp_var]
            #         print(temp_var, temp_vars[temp_var])
            if _ == 1:  ## DPAp
                """Запрашиваем один раз"""
                """ Текстовый протокол """
                command = ['READSTATE', [str(lp_temp_date_from) + ' 0 ' + str(
                    lp_temp_date_to) + ' 0']]  ## 0 вроде состояние зима/лето. Вроде лето?
                all_strings = self.commands_send_helper(command)
                res_text_protocol_dict = self._helper_text_protocol_answer_to_dict(all_strings)

                answer_data_for_1 = answer_data[:-1]  ## Последний байт -- Stat
                self.assertEqual(8, len(lp_temp_Val))
                self.assertEqual((res_text_protocol_dict['DPAp']), str(hex_to_double(lp_temp_Val[::-1])))
            elif _ == 3:  ## DPAm
                answer_data_for_3 = answer_data[:-1]  ## Последний байт -- Stat
                lp_temp_val_cur = self._check_if_hex_array_is_zero(lp_temp_Val[-8:][::-1])
                lp_temp_val_cur = str(0 if lp_temp_val_cur == 0 else hex_to_double(lp_temp_val_cur))
                self.assertEqual(str(res_text_protocol_dict['DPAm']), lp_temp_val_cur)
                self.assertTrue(answer_data_for_1 == answer_data_for_3[:-8])
                self.assertEqual(16, len(lp_temp_Val))
            elif _ == 7:  ## DPRp
                answer_data_for_7 = answer_data[:-1]  ## Последний байт -- Stat
                self.assertTrue(answer_data_for_3 == answer_data_for_7[:-8])
                self.assertEqual(24, len(lp_temp_Val))
                lp_temp_val_cur = self._check_if_hex_array_is_zero(lp_temp_Val[-8:][::-1])
                lp_temp_val_cur = str(0 if lp_temp_val_cur == 0 else hex_to_double(lp_temp_val_cur))
                self.assertEqual(str(res_text_protocol_dict['DPRp']), lp_temp_val_cur)
            elif _ == 15:  ## DPRm
                answer_data_for_15 = answer_data[:-1]
                self.assertTrue(answer_data_for_7 == answer_data_for_15[
                                                     :-8])  ## Как тут правильно сравнивать - т.к. + 1 байт на конце ??
                self.assertEqual(32, len(lp_temp_Val))
                lp_temp_val_cur = self._check_if_hex_array_is_zero(lp_temp_Val[-8:][::-1])
                lp_temp_val_cur = str(0 if lp_temp_val_cur == 0 else hex_to_double(lp_temp_val_cur))
                self.assertEqual(str(res_text_protocol_dict['DPRm']), lp_temp_val_cur)

    ## undone

    # TODO:
    # !!! Оставил заготовку                          !!!
    # !!! На данный момент, команда не используется. !!!
    # def test_get_shortlp(self):
    #     ## undone
    #     """ Просто проверяем количество ответа - ?? байта.
    #     Номер счетчика - b'\x00\x10\x18\x47\x60'
    #     """
    #     Nsh = work_with_device.uspd_counter_number
    #     Kanal = b'\x01'
    #     Interval = b'\x00'
    #     # Tstart = b'\x00\x00\x00\x00'
    #     Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))
    #     Kk = b'\x00\x01'
    #     #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
    #     result_answer_map = send_command_and_get_answer(105, command_params=Nsh+Kanal+Interval+Tstart+Kk)
    #     self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
    #     answer_data = result_answer_map['answer_data'][::-1]
    #     print(answer_data)
    #     self.assertEqual(15, len(answer_data))

    ## undone

    def test_get_tests(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        ## Читаем дату + данные из текстового протокола
        ## Надо везде открывать закрывать соединение ?????
        ## 1. Читаем за последние 1 час READAQUAL - и забираем последнюю дату + данные
        ## Читаем последние данные.
        commands = ['READAQUAL',
                    [get_str_date_from_datetime(datetime.datetime.now() - datetime.timedelta(minutes=32)) + ' 0 ' +
                     get_str_date_from_datetime(datetime.datetime.now()) + ' 0']]
        all_strings = self.commands_send_helper(commands)
        res_text_protocol_dict = self._helper_text_protocol_answer_to_dict(all_strings)

        ## Работаем с RTU327
        Nsh = work_with_device.uspd_counter_number
        Tstart = get_reversed_time_bytes(
            date_to_seconds(get_datetime_from_string(
                get_str_date_from_datetime(datetime.datetime.now() - datetime.timedelta(minutes=32)),
                '%y.%m.%d %H:%M:%S')))
        NumTests = b'\x01'
        # Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(107, command_params=Nsh + Tstart + NumTests)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data']
        self.assertTrue(len(answer_data) >= 18)  # не меньше 18 байт - ?? как считается массиы ??
        tests_temp_BITSTATS = answer_data[:4]  ##INT32
        tests_temp_Realint = answer_data[4]  ## INT8
        tests_temp_Elm = answer_data[5]  ## INT8
        tests_temp_data_time = answer_data[6:10]
        tests_temp_data = answer_data[10:]
        aqual_vars_from_rtu_protocol = {}
        aqual_vars_names = ['P0', 'P1', 'P2', 'S0', 'S1', 'S2', 'F', 'I0', 'I1', 'I2',
                            'U0', 'U1', 'U2', 'Ang0', 'Ang2']  ##Нет Ang 1???

        round_number = 1000  ## На сколько домонжаем

        for _ in range(int(len(tests_temp_data) / 8)):
            aqual_vars_from_rtu_protocol[aqual_vars_names[_]] = hex_to_double(
                tests_temp_data[_ * 8: _ * 8 + 8][::-1]) * 1000

        for key in aqual_vars_from_rtu_protocol.keys():
            if key in ['P0', 'P1', 'P2', 'S0', 'S1', 'S2']:
                ## Обнуление до двух знаков после запятой -- float???
                self.assertEqual(round(float(aqual_vars_from_rtu_protocol[key]), 2),
                                 round(float(res_text_protocol_dict[key]), 2))
            elif key in ['F', 'I0', 'I1', 'I2', 'U0', 'U1', 'U2', 'Ang0', 'Ang2']:
                if key in ['U2', 'Ang0', 'Ang2']:
                    ## 'U2','Ang0','Ang2' имеют много знаков после запятой
                    ## Пока просто преобразуем в Int --> отбрасываем знаки после запятой.
                    self.assertEqual(int(float((aqual_vars_from_rtu_protocol[key] / round_number))),
                                     int(float(res_text_protocol_dict[key])))
                else:
                    self.assertEqual(round(float((aqual_vars_from_rtu_protocol[key] / round_number)), 2),
                                     round(float(res_text_protocol_dict[key]), 2))

    def test_get_autoread(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """

        ## Текстовы протокол
        ## Дублирование -- из get_pok()
        cur_date = datetime.datetime.now()
        temp_date_array = [str(cur_date.year)[2:], '.',
                           str(cur_date.month) if cur_date.month > 9 else '0' + str(cur_date.month), '.',
                           str(cur_date.day) if cur_date.day > 9 else '0' + str(cur_date.day)]
        command = ['READDAY', [''.join(temp_date_array)]]
        all_strings = self.commands_send_helper(command)
        res_text_protocol_dict = self._helper_text_protocol_answer_to_dict(all_strings)

        N_SH = work_with_device.uspd_counter_number
        # Tday = get_at_day_start_datetime_bytes(amoun_of_days=1)  ## !!! Смотрит на текущую дату, а не минус день. !!!!

        Timestamp = 1590969599
        Tday = int(Timestamp).to_bytes(length=4, byteorder='little')

        Kanal = b'\x01'
        Kk = b'\x01'
        result_answer_map = send_command_and_get_answer(109, command_params=N_SH + Tday + Kanal + Kk)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data']
        self.assertEqual(198, len(answer_data))

        autoread_temp_Nsh = answer_data[:10]  ## 10 или 5 байт ?? STR<10> ++ переворачиваем ответ
        autoread_temp_Dd_mm_yyyy = answer_data[10:14][::-1]  ## TIME_T ## Надо переворачивать  ?
        autoread_temp_Akwh = answer_data[14:22][::-1]  ## FLOAT8 --> Double
        autoread_temp_Akw = answer_data[22:30][::-1]  ## FLOAT8 --> Double
        autoread_temp_Atd = answer_data[30:34][::-1]  ## TIME_T --> datetime
        autoread_temp_Akwcum = answer_data[34:42][::-1]  ## FLOAT8 --> Double
        autoread_temp_Akwc = answer_data[42:50][::-1]  ## FLOAT8 --> Double
        autoread_temp_Bkwh = answer_data[50:58][::-1]  ## FLOAT8 --> Double
        autoread_temp_Bkw = answer_data[58:66][::-1]  ## FLOAT8 --> Double
        autoread_temp_Btd = answer_data[66:70][::-1]  ## TIME_T --> datetime
        autoread_temp_Bkwcum = answer_data[70:78][::-1]  ## FLOAT8 --> Double
        autoread_temp_Bkwc = answer_data[78:86][::-1]  ## FLOAT8 --> Double
        autoread_temp_Ckwh = answer_data[86:94][::-1]  ## FLOAT8 --> Double
        autoread_temp_Ckw = answer_data[94:102][::-1]  ## FLOAT8 --> Double
        autoread_temp_Ctd = answer_data[102:106][::-1]  ## TIME_T --> datetime
        autoread_temp_Ckwcum = answer_data[106:114][::-1]  ## FLOAT8 --> Double
        autoread_temp_Ckwc = answer_data[114:122][::-1]  ## FLOAT8 --> Double
        autoread_temp_dkwh = answer_data[122:130][::-1]  ## FLOAT8 --> Double
        autoread_temp_dkw = answer_data[130:138][::-1]  ## FLOAT8 --> Double
        autoread_temp_dtd = answer_data[138:142][::-1]  ## TIME_T --> datetime
        autoread_temp_dkwcum = answer_data[142:150][::-1]  ## FLOAT8 --> Double
        autoread_temp_dkwc = answer_data[150:158][::-1]  ## FLOAT8 --> Double
        autoread_temp_Kwha = answer_data[158:166][::-1]  ## FLOAT8 --> Double
        autoread_temp_Q1 = answer_data[166:174][::-1]  ## FLOAT8 --> Double
        autoread_temp_Q2 = answer_data[174:182][::-1]  ## FLOAT8 --> Double
        autoread_temp_Q3 = answer_data[182:190][::-1]  ## FLOAT8 --> Double
        autoread_temp_Q4 = answer_data[190:][::-1]  ## FLOAT8 --> Double

        temp_vars = vars().copy()  ## Делаем копию переменных, т.к. список ?почему-то? изменяется в реальном времени.
        res_array = {}
        for _ in temp_vars:
            if _.startswith('autoread_temp_'):
                res_array[_] = temp_vars[_]
                print(_, temp_vars[_])
        for _ in res_array:
            if _.strip() == 'autoread_temp_Nsh':
                uspd_counter_number = [str(int(bytes.fromhex(_), 16)) for _ in res_array[_]]
                uspd_counter_number = int(''.join(uspd_counter_number))
                self.assertEqual(uspd_counter_number_as_int, uspd_counter_number)
            elif _.strip() in ['autoread_temp_Dd_mm_yyyy', 'autoread_temp_Atd', 'autoread_temp_Btd',
                               'autoread_temp_Ctd', 'autoread_temp_dtd']:
                ## TODO
                ## Как смотреть -- autoread_temp_Dd_mm_yyyy  ????
                cur_date_from_answer_in_seconds = dec_from_bytes_array(res_array[_])
                self.assertTrue(cur_date_from_answer_in_seconds >= 0)
            elif _.strip().endswith('kwh') or _.strip().endswith('Kwha'):  # Akwh, Bkwh, Ckwh, Dkwh
                if _ == 'autoread_temp_Akwh':
                    self.assertEqual(int(float(res_text_protocol_dict['dA+1'])), int(
                        float(hex_to_double(res_array[_]) * 1000)))  ## float , а дальше в int не осень красиво
                elif _ == 'autoread_temp_Bkwh':
                    self.assertEqual(int(float(res_text_protocol_dict['dA+2'])), int(
                        float(hex_to_double(res_array[_]) * 1000)))  ## float , а дальше в int не осень красиво
                elif _ == 'autoread_temp_Ckwh':
                    self.assertEqual(int(float(res_text_protocol_dict['dA+3'])),
                                     int(float(hex_to_double(
                                         res_array[_]) * 1000)))  ## float , а дальше в int не осень красиво
                elif _ == 'autoread_temp_dkwh':
                    self.assertEqual(int(float(res_text_protocol_dict['dA+4'])),
                                     int(float(hex_to_double(
                                         res_array[_]) * 1000)))  ## float , а дальше в int не осень красиво
                elif _ == 'autoread_temp_Kwha':
                    self.assertEqual(int(float(res_text_protocol_dict['dA+0'])),
                                     int(float(hex_to_double(
                                         res_array[_]) * 1000)))  ## float , а дальше в int не осень красиво
            else:
                # По идеи все остальные параметры должны быть -1
                self.assertEqual(-1.0, hex_to_double(res_array[_]))

    # ???? undone ????
    def test_get_mtrlog(self):
        """
        Проверяем коды событий журнала счетчиков + проверяем что возвращается дата.
        """
        Nsh = work_with_device.uspd_counter_number
        Tstart = b'\x00\x00\x00\x00'
        Cnt = b'\x00\x01'
        all_evType_arrays = [0, 1, 2, 3, 4, 5, 6, 9, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213,
                             214,
                             215, 216, 255, 128, 192, 129, 193, 130, 194, 131, 195, 132, 196, 133, 197, 134, 198,
                             135, 199, 200, 137, 217, 138, 218, 139, 219]
        result_answer_map = send_command_and_get_answer(116, command_params=Nsh + Tstart + Cnt)
        self.assertEqual('00', result_answer_map[
            'result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data']
        self.assertTrue(len(answer_data) >= 19)

        for _ in range(int(len(answer_data) / 6)):
            cur_temp_answer = answer_data[_ * 6:_ * 6 + 6]
            cur_evTime = date_from_seconds(hex_array_to_dec(cur_temp_answer[:4][::-1]))
            evType = hex_array_to_dec(cur_temp_answer[4:][::-1])
            self.assertTrue(evType in all_evType_arrays)
            self.assertTrue(isinstance(cur_evTime, datetime.datetime))
    # ???? undone ????


if __name__ == "__main__":
    unittest.main()


# ======

def get_var_name_and_var_value_from_vars(var_prefix):
    """
    Ищем (вроде) во всех переменных, переменные с префиксом --var_prefix--
    """
    temp_vars = vars().copy()  ## Делаем копию переменных, т.к. список ?почему-то? изменяется в реальном времени.
    res_array = {}
    for _ in temp_vars:
        if _.startswith(var_prefix):
            res_array[_] = temp_vars[_]
    return res_array
