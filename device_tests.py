"""
py -m pytest device_tests.py::RTU327::test_gettime -s -v
"""
import unittest

from communication_engineering_serialport_helper.main_methods.methods import send_read
from work_with_device import *
import work_with_device


class RTU327(unittest.TestCase):

    counter_number = b'\x00\x10\x18\x47\x60'  ## Номер счетчика
    uspd_tcp_ip = '192.168.205.10'
    uspd_tcp_port = 14101
    uspd_password = '00000000'

    """'3c', 'a0', '2f' = неправильная контрольная сумма - жопа ответа
    прокинуть в каждый тест ? """

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
        commands = ['TRANSOPEN', ## Открываем соединение
                    'CLEARTABL', ['TRANSADD',['1','3','60','010101010101','020202020202','0','4','6','8','0','0','1','1','1']],
                    ## Последние три единички :: Syb_Rnk - Тип объекта :: N_Ob - Номер объекта :: N_Fid - Номер фидера
                    ['WARCHPRM',['1','1','1','1','0','0','0','1']],['WSCHEDAQUAL',['0','0','0','30']], ## Записываем -- для test_get_tests -- Качество сети приборов учета.
                    'TRANSCOMMIT'] ## Закрываем соединение
        """Последние три единички
            Syb_Rnk - Тип объекта  
            N_Ob - Номер объекта 
            N_Fid - Номер фидера 
        """
        for command in commands:
            if type(command) is list:
                all_strings = send_read(password=RTU327.uspd_password,tcp_ip=RTU327.uspd_tcp_ip, tcp_port=RTU327.uspd_tcp_port,
                                        command=command[0], args_list=command[1], tcp_timeout=5)
            elif type(command) is str:
                all_strings = send_read(password=RTU327.uspd_password,tcp_ip=RTU327.uspd_tcp_ip, tcp_port=RTU327.uspd_tcp_port,
                                        command=command, tcp_timeout=5)
            else:
                raise Exception('Неизвестный тип')

            print(all_strings)
            ## Проверка Ответа - пока только OK05C7??
            self.assertEqual('OK05C7',all_strings.strip())

        ##Далее мы просто ждем ????
        # print('!!!GOING TO SLEEP FOR 15 MINUTES!!!\n'*10)
        # time.sleep(15*60) #15 минут
        # print('was\\done\n'*10)

    def test_get_version(self):
        """
        USPD_RETURN :
            Описание версии, состоящее из 6 символов:
                2 байта – старший номер версии
                2 байта – средний номер версии
                2 байта – младший номер версии
        """

        result_answer_map = send_command_and_get_answer(3)
        answer_data = result_answer_map['answer_data']
        print(answer_data)
        self.assertEqual(6 , len(answer_data))

        ## Ожидаемый ответ железки
        ## ['0x30','0x32','0x30','0x31','0x30','0x32']
        self.assertEqual(['30', '32', '30', '31', '30', '32'], result_answer_map['answer_data'])


    @work_with_device.check_ip_args
    def test_get_time(self):
        result_answer_map = send_command_and_get_answer(114)
        answer_data = result_answer_map['answer_data'][::-1]
        result_answer_data = ''
        for x in answer_data: result_answer_data += x
        formated_device_time = int(result_answer_data, 16)
        device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        print(device_datetime)

        # check ## секунды не проверяю
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

        wrong_command = work_with_device.create_command(prefix=prefix, first_part_of_package_size=first_part_of_package_size,
                                                        ordinal_number=ordinal_number, password=password, reserve=reserve,
                                                        crc=b'\xff\xff', command_number=114)
        print(wrong_command)
        result_answer_map = send_command_and_get_answer(send_command_raw=wrong_command)
        self.assertEqual(['a0', '2f'],result_answer_map['crc'])


    def test_set_time(self):
        # TODO
        # Правильно переписывать , без дублирования test_gettime()

        hour_in_seconds = 3600
        # # # get_reversed_bytes_string_str_ver(get_right_hex(hex(3600)[2:])) -- > b'\x10\x0e'

        # result_answer_map = send_command_and_get_answer(115) ## Без доп. параметров работает
        res_hex_time = get_right_hex(hex(hour_in_seconds)[2:])
        amount_of_byte = len(res_hex_time) / 2
        result_hex_time = b''
        if amount_of_byte != 4:
            for _ in range(4 - int(amount_of_byte)):
                result_hex_time += b'\x00'
        result_hex_time += res_hex_time.encode()
        result_answer_map = send_command_and_get_answer(115,
                                                        command_params=b'\x10\x0e\x00\x00')  # 3600 + добавляем 1 час на успд
                                                        # command_params=b'\xf0\xf1\xff\xff')  # 3600 + добавляем 1 час на успд
                                                        # command_params=b'\x00\x00\x00\xff')  # 3600 + добавляем 1 час на успд
        # result_answer_map = send_command_and_get_answer(115, command_params=b'\xfe\xff\xff\xff')
        # check ## секунды не проверяю
        # Копия --- test_gettime


        """ Проверка """
        result_answer_map = send_command_and_get_answer(114)
        answer_data = result_answer_map['answer_data'][::-1]
        result_answer_data = ''
        for x in answer_data: result_answer_data += x
        formated_device_time = int(result_answer_data, 16)
        device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        curr_datetime = datetime.datetime.now()
        device_datetime = device_datetime + datetime.timedelta(hours=3)
        difference_between_dates = abs((curr_datetime - device_datetime).total_seconds())
        self.assertTrue(3540 < difference_between_dates < 3660)  # Разница +- 1 минута

    def helper_test_get_maxlogid(self):
        result_answer_map = send_command_and_get_answer(101, command_params=b'\x01')
        self.assertEqual(4, len(result_answer_map['answer_data']))
        before_generation_event = result_answer_map['answer_data']
        return dec_from_bytes_array(before_generation_event)

    def test_get_maxlogid(self):  ##
        """ Просто проверяем количество ответа - 4 байта. """
        max_log_id_before = self.helper_test_get_maxlogid()
        ## Сгенерить событие -->> проверить, что увеличился
        ## Уввеличиваем время
        result_answer_map = send_command_and_get_answer(115, command_params=b'\x10\x0e\x00\x00')  # 3600 + добавляем 1 час на успд
        # print(result_answer_map)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        max_log_id_after = self.helper_test_get_maxlogid()
        print(max_log_id_before, max_log_id_after)

        if max_log_id_before > 60000 and max_log_id_after < 5000: ##случай с обнулением: -- 65535
            pass
        else:
            self.assertTrue(max_log_id_after > max_log_id_before)

    def test_get_log(self):
        Nsect = b'\x00\x00\x00\x01'
        # Id = b'\x00\x00\x00\x01' ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
        Id = dec_to_hex(self.helper_test_get_maxlogid()) ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
        Id = add_empty_bytes(Id, 4-len(Id)) ## Доставляем до 4-х байтов
        Num = b'\x00\x01'
        result_answer_map = send_command_and_get_answer(117, command_params=Nsect + Id + Num)
        print(result_answer_map)
        self.assertEqual(13, len(result_answer_map))

    def test_get_shprm(self): ## Пока просто смотрим
        """серийный номер успд ?? откуда брать ??
         10 18 47 60
        """

        ##RTU327 протокол
        Nsh = RTU327.counter_number ## Номер счетчика
        result_answer_map = send_command_and_get_answer(112, command_params=Nsh)
        # answer_data = result_answer_map['answer_data'][::-1]  ##перевернутый ответ
        answer_data = result_answer_map['answer_data']
        vers = answer_data[:2]
        typ_sh = answer_data[2]
        kt = answer_data[3:11]  ##FLOAT8
        kn = answer_data[11:19]  ##FLOAT8
        m = answer_data[19:27]  ##FLOAT8
        interv = answer_data[27]
        syb_rnk = answer_data[28:32]  ##INT32
        n_ob = answer_data[32:36]  ##INT32
        n_fid = answer_data[36:]  ##INT32
        print(result_answer_map)
        print('vers :: ', vers)
        print('typ_sh :: ', typ_sh)
        print('kt :: ', kt)
        print('kn :: ', kn)
        print('m :: ', m)
        print('interv :: ', interv)
        print('syb_rnk :: ', syb_rnk)
        print('n_ob :: ', n_ob)
        print('n_fid :: ', n_fid)
        self.assertEqual(40, len(answer_data))
        ## Данные сравниваются с теми, которые были записаны по текстовому протоколу - команда TRANSADD
        self.assertEqual(['01', '00', '00', '00'], syb_rnk) ## Надо переворачивать ??
        self.assertEqual(['01', '00', '00', '00'], n_ob) ## Надо переворачивать ??
        self.assertEqual(['01', '00', '00', '00'], n_fid) ## Надо переворачивать ??

    def test_get_pok(self):  ##
        """ Просто проверяем количество ответа - 8 байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        NSH  = RTU327.counter_number
        Chnl  = b'\x01'
        time_minus_month  = get_reversed_time_bytes(date_to_seconds(datetime.datetime.now())) ##minus 1 month
        # result_answer_map = send_command_and_get_answer(113, command_params=NSH+Chnl+time_minus_month)
        result_answer_map = send_command_and_get_answer(113, command_params=NSH+Chnl+get_reversed_bytes_string_byte_ver(time_minus_month))
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        print(str(len(answer_data)))
        # self.assertEqual(8, len(answer_data))

        ##Текстовый протокол
        # gg = send_read(password=RTU327.uspd_password,tcp_ip = RTU327.uspd_tcp_ip, tcp_port = RTU327.uspd_tcp_ip,
        #                command='READMONTH', tcp_timeout=25)
        # print(gg)


    def test_get_lp(self):  ##
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = RTU327.counter_number
        Kanal = b'\x01'
        # Tstart = b'\x00\x00\x00\x00'
        Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7))) ## Откуда забирать дату данных со счетчика ??
        # Tstart = get_reversed_bytes_string_byte_ver(
        #     get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))) ## Откуда забирать дату данных со счетчика ??
        self.assertEqual(4, len(Tstart))
        Kk = b'\x00\x01'

        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        # result_answer_map = send_command_and_get_answer(111, command_params=Nsh+Kanal+get_reversed_bytes_string_byte_ver(Tstart))
        result_answer_map = send_command_and_get_answer(111, command_params=Nsh+Kanal+Tstart + Kk)
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertEqual(15, len(answer_data))

    def test_get_shortlp(self):        ## undone
        ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = RTU327.counter_number
        Kanal = b'\x01'
        Interval = b'\x00'
        # Tstart = b'\x00\x00\x00\x00'
        Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))
        Kk = b'\x00\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(105, command_params=Nsh+Kanal+Interval+Tstart+Kk)
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertEqual(15, len(answer_data))
        ## undone

    def test_get_tests(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = RTU327.counter_number
        # Tstart = b'\x00\x00\x00\x00'
        # Tstart = get_reversed_bytes_string_byte_ver(get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7))))
        # Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))
        # Tstart = b'\x5c\xac\xa4\x16'
        Tstart = b'\x00\x00\x00\x00'
        NumTests  = b'\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(107, command_params=Nsh+Tstart+NumTests)
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertTrue(len(answer_data) >= 18) #не менбше 18 байт - ?? как считается массиы ??

    def test_get_autoread(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        N_SH = RTU327.counter_number
        Tday  = b'\x00\x00\x00\x00'
        Kanal = b'\x01'
        Kk = b'\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(109, command_params=N_SH + Tday + Kanal + Kk)
        answer_data = result_answer_map['answer_data'][::-1]
        # print(answer_data)
        # print(len(answer_data))
        self.assertEqual(198,len(answer_data))

        Nsh = answer_data[:11]
        Dd_mm_yyyy = answer_data[11:15]
        Akwh = answer_data[15:23]
        Akw = answer_data[23:31]
        Atd = answer_data[31:39]
        Akwcum = answer_data[39:47]
        Akwc = answer_data[47:55]
        Bkwh = answer_data[55:63]
        Bkw = answer_data[63:71]
        Btd = answer_data[71:75]
        Bkwcum = answer_data[75:83]
        Bkwc = answer_data[83:91]
        Ckwh = answer_data[91:99]
        Ckw = answer_data[99:107]
        Ctd = answer_data[107:111]
        Ckwcum = answer_data[111:119]
        Ckwc = answer_data[119:127]
        dkwh = answer_data[127:135]
        dkw = answer_data[135:143]
        dtd = answer_data[143:147]
        dkwcum = answer_data[147:155]
        dkwc = answer_data[155:163]
        Kwha = answer_data[163:171]
        Q1 = answer_data[171:179]
        Q2 = answer_data[179:187]
        Q3 = answer_data[187:195]
        Q4 = answer_data[195:]


if __name__ == "__main__":
    unittest.main()
    # fast = unittest.TestSuite()
#     fast.addTests(TestFastThis)