"""
py -m pytest device_tests.py::RTU327::test_gettime -s -v
"""
import re
import unittest

from communication_engineering_serialport_helper.Utils.helpActions import get_normal_text
from communication_engineering_serialport_helper.main_methods.methods import send_read
from work_with_device import *
import work_with_device


class RTU327(unittest.TestCase):

    # counter_number = b'\x00\x10\x18\x47\x60'  ## Номер счетчика

    # temp_config_parser = ConfigParser()
    # temp_config_parser.read('uspd_settings.ini')
    # temp_config_parser.get('RTU-327','uspd_tcp_ip')
    # uspd_tcp_ip = temp_config_parser.get('RTU-327','uspd_tcp_ip')
    # uspd_tcp_port = int(temp_config_parser.get('RTU-327','uspd_tcp_port'))
    # uspd_password = temp_config_parser.get('RTU-327','uspd_password')

    def commands_send_helper(self, command):
        if type(command) is list:
            all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
                                    command=command[0], args_list=command[1], tcp_timeout=5)
        elif type(command) is str:
            all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
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
            all_strings = self.commands_send_helper(command)
            print(all_strings)
            ## Проверка Ответа - пока только OK05C7??
            self.assertEqual('OK05C7',all_strings.strip())

        ## TODO
        ## Тут собирать uspd_settings.ini --> ConfigParser


        ##Далее мы просто ждем ????
        # print('!!!GOING TO SLEEP FOR 15 MINUTES!!!\n'*10)
        # time.sleep(15*60) #15 минут
        # print('was\\done\n'*10)

    @staticmethod
    def get_uspd_count_number(): ## Использовать для проверок
        ## TODO
        ## Возможно следует READQUAL следует заменить на другую -- чтобы меньше грузилась успд.
        all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
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

        result_answer_map = send_command_and_get_answer(3)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data']
        print(answer_data)
        self.assertEqual(6, len(answer_data))

        ## Ожидаемый ответ железки
        ## ['0x30','0x32','0x30','0x31','0x30','0x32']
        self.assertEqual(['30', '32', '30', '31', '30', '32'], result_answer_map['answer_data'])


    # @work_with_device.check_ip_args
    def test_get_time(self):
        result_answer_map = send_command_and_get_answer(114)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
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
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        # result_answer_map = send_command_and_get_answer(115, command_params=b'\xfe\xff\xff\xff')
        # check ## секунды не проверяю
        # Копия --- test_gettime


        """ Проверка """
        result_answer_map = send_command_and_get_answer(114)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
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
                         result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map

    def helper_test_get_maxlogid(self):
        result_answer_map = send_command_and_get_answer(101, command_params=b'\x01')
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
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

        ## Возвращаем время назад
        send_command_and_get_answer(115, command_params=b'\xf0\xf1\xff\xff')  # 3600 == убираем 1 час на успд

    def test_get_log(self):
        Nsect = b'\x00\x00\x00\x01'
        # Id = b'\x00\x00\x00\x01' ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
        Id = dec_to_hex(self.helper_test_get_maxlogid()) ## id события - вот тут надо доставать последнее событие из журнала --> test_get_maxlogid()
        Id = add_empty_bytes(Id, 4-len(Id)) ## Доставляем до 4-х байтов
        Num = b'\x00\x01'
        result_answer_map = send_command_and_get_answer(117, command_params=Nsect + Id + Num)
        print(result_answer_map)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        self.assertEqual(13, len(result_answer_map))

    def test_get_shprm(self): ## Пока просто смотрим
        """серийный номер успд ?? откуда брать ??
         10 18 47 60
        """
        ##RTU327 протокол
        Nsh = work_with_device.uspd_counter_number ## Номер счетчика
        result_answer_map = send_command_and_get_answer(112, command_params=Nsh)
        # answer_data = result_answer_map['answer_data'][::-1]  ##перевернутый ответ
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
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

        self.assertEqual(1.0, hex_to_double(kt))
        self.assertEqual(1.0, hex_to_double(kn))
        self.assertEqual(1.0, hex_to_double(m))
        self.assertEqual(1, hex_array_to_dec(syb_rnk))
        self.assertEqual(1, hex_array_to_dec(n_ob))
        self.assertEqual(1, hex_array_to_dec(n_fid))


    def test_get_pok(self):  ##
        """ Просто проверяем количество ответа - 8 байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """

        ## Читаем показания счетчика - по текстовому протоколу
        ## TODO
        ## ? Перенести в Текстовый протокол ?
        cur_date = datetime.datetime.now() - datetime.timedelta(days=1)
        temp_date_array = [str(cur_date.year)[2:], '.',
               str(cur_date.month) if cur_date.month > 9 else '0' + str(cur_date.month), '.',
               str(cur_date.day) if cur_date.day > 9 else '0' + str(cur_date.day)]
        command = ['READDAY',[''.join(temp_date_array)]]

        all_strings = self.commands_send_helper(command)
        array_of_string = get_normal_text(all_strings.split('\n')).split('\n')

        # print(array_of_string)
        # print(array_of_string)
        res_text_protocol_dict = {}
        for line in array_of_string:
            line_array = line.split()
            if len(line_array) <= 1:
                pass
            else:
                res_text_protocol_dict[line_array[0]] = line_array[1]


        print(res_text_protocol_dict)


        # Вторая реализация -- проверяем все Chnl
        for _ in [1,3,7,15]: ## 1,3,7,15 --> постепенное заполнение битами , т.е. 0001 / 0011 / 0111 / 1111 ### 1111 -- > (R-)/(R+)/(A-)/(A+)
            Chnl = dec_to_hex(_)
            NSH = work_with_device.uspd_counter_number

            # ставим дату - предыдущий день -- 00:00
            cur_date = datetime.datetime.now()
            previous_day = get_reversed_time_bytes(
                date_to_seconds(datetime.datetime.now() - datetime.timedelta(days=1, hours=cur_date.hour,minutes=cur_date.minute, seconds=cur_date.second,microseconds=cur_date.microsecond)
                               ))

            # result_answer_map = send_command_and_get_answer(113, command_params=NSH+Chnl+time_minus_month)
            result_answer_map = send_command_and_get_answer(113, command_params=NSH+Chnl+previous_day)
            self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
            answer_data = result_answer_map['answer_data'][::-1]
            print(answer_data,str(len(answer_data)))

            if _ == 1:
                answer_data_for_1 = answer_data
                self.assertEqual(8, len(answer_data))
                self.assertEqual(int(float(res_text_protocol_dict['dA+0'])), int(hex_to_double(answer_data)*1000))
            elif _ == 3:
                answer_data_for_3 = answer_data
                self.assertTrue(answer_data_for_1 == answer_data_for_3[8:])  ## ?? Спереди или сзади проверять ответ ??
                self.assertEqual(int(float(res_text_protocol_dict['dA-0'])), int(hex_to_double(answer_data[:8])*1000)) ## float , а дальше в int не осень красиво
                self.assertEqual(16, len(answer_data))
            elif _ == 7:
                answer_data_for_7 = answer_data
                self.assertTrue(answer_data_for_3 == answer_data_for_7[8:])  ## ?? Спереди или сзади проверять ответ ??
                self.assertEqual(24, len(answer_data))
                self.assertEqual(int(float(res_text_protocol_dict['dR+0'])), int(hex_to_double(answer_data[:8])*1000))
            elif _ == 15:
                answer_data_for_15 = answer_data
                self.assertTrue(answer_data_for_7 == answer_data_for_15[8:])  ## ?? Спереди или сзади проверять ответ ??
                self.assertEqual(32, len(answer_data))
                self.assertEqual(int(float(res_text_protocol_dict['dR-0'])), int(hex_to_double(answer_data[:8])*1000))


    def test_get_lp(self):  ##
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = work_with_device.uspd_counter_number
        Kanal = b'\x01'
        Tstart = b'\x00\x00\x00\x00'
        # Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7))) ## Откуда забирать дату данных со счетчика ??
        # Tstart = get_reversed_bytes_string_byte_ver(
        #     get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))) ## Откуда забирать дату данных со счетчика ??
        self.assertEqual(4, len(Tstart))
        Kk = b'\x00\x01'

        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        # result_answer_map = send_command_and_get_answer(111, command_params=Nsh+Kanal+get_reversed_bytes_string_byte_ver(Tstart))
        result_answer_map = send_command_and_get_answer(111, command_params=Nsh+Kanal+Tstart + Kk)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertEqual(15, len(answer_data))

    def test_get_shortlp(self):        ## undone
        ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = work_with_device.uspd_counter_number
        Kanal = b'\x01'
        Interval = b'\x00'
        # Tstart = b'\x00\x00\x00\x00'
        Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))
        Kk = b'\x00\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(105, command_params=Nsh+Kanal+Interval+Tstart+Kk)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertEqual(15, len(answer_data))
        ## undone

    def test_get_tests(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = work_with_device.uspd_counter_number
        # Tstart = b'\x00\x00\x00\x00'
        # Tstart = get_reversed_bytes_string_byte_ver(get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7))))
        # Tstart = get_reversed_time_bytes(date_to_seconds(datetime.datetime(day=8, month=7, year=2019, hour=16, minute=7)))
        # Tstart = b'\x5c\xac\xa4\x16'
        # Tstart = b'\x00\x00\x00\x00'
        Tstart = b'\x16\xa4\xac\x5c'
        NumTests  = b'\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(107, command_params=Nsh+Tstart+NumTests)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertTrue(len(answer_data) >= 18) #не менбше 18 байт - ?? как считается массиы ??

    def test_get_autoread(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        # N_SH = RTU327.counter_number
        N_SH = work_with_device.uspd_counter_number
        # Tday  = b'\x00\x00\x00\x00'

        Tday  = b'\x4f\x7f\x27\x5d' ## При 7f ок
        # Tday  = b'\x4f\x80\x27\x5d' ## При 80 не ок, т.е. при > 7f , crc на успд уже не так считается

        # Tday  = b'\x7f\x7f\x7f\x7f'

        # Tday = b'\x5d\x27\xa3\x4f'
        # Tday = b'\x4f\xa3\x27\x5d'

        # Tday = b'\x95\xff\x26\x5d'
        # Tday = b'\x5d\x26\xff\x95'

        Kanal = b'\x01'
        Kk = b'\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(109, command_params=N_SH + Tday + Kanal + Kk)
        self.assertEqual('00',result_answer_map['result_code'])  ##Проверка правильного выполнения команды -- result_answer_map
        # answer_data = result_answer_map['answer_data'][::-1]
        answer_data = result_answer_map['answer_data']
        # print(answer_data)
        # print(len(answer_data))
        self.assertEqual(198,len(answer_data))

        autoread_temp_Nsh = answer_data[:10] ## 10 или 5 байт ?? STR<10> ++ переворачиваем ответ
        autoread_temp_Dd_mm_yyyy = answer_data[10:14][::-1] ## TIME_T ## Надо переворачивать  ?
        autoread_temp_Akwh = answer_data[14:22][::-1] ## FLOAT8 --> Double
        autoread_temp_Akw = answer_data[22:30][::-1] ## FLOAT8 --> Double
        autoread_temp_Atd = answer_data[30:34][::-1] ## TIME_T --> datetime
        autoread_temp_Akwcum = answer_data[34:42][::-1] ## FLOAT8 --> Double
        autoread_temp_Akwc = answer_data[42:50][::-1] ## FLOAT8 --> Double
        autoread_temp_Bkwh = answer_data[50:58][::-1] ## FLOAT8 --> Double
        autoread_temp_Bkw = answer_data[58:66][::-1] ## FLOAT8 --> Double
        autoread_temp_Btd = answer_data[66:70][::-1] ## TIME_T --> datetime
        autoread_temp_Bkwcum = answer_data[70:78][::-1] ## FLOAT8 --> Double
        autoread_temp_Bkwc = answer_data[78:86][::-1] ## FLOAT8 --> Double
        autoread_temp_Ckwh = answer_data[86:94][::-1] ## FLOAT8 --> Double
        autoread_temp_Ckw = answer_data[94:102][::-1] ## FLOAT8 --> Double
        autoread_temp_Ctd = answer_data[102:106][::-1] ## TIME_T --> datetime
        autoread_temp_Ckwcum = answer_data[106:114][::-1] ## FLOAT8 --> Double
        autoread_temp_Ckwc = answer_data[114:122][::-1] ## FLOAT8 --> Double
        autoread_temp_dkwh = answer_data[122:130][::-1] ## FLOAT8 --> Double
        autoread_temp_dkw = answer_data[130:138][::-1] ## FLOAT8 --> Double
        autoread_temp_dtd = answer_data[138:142][::-1] ## TIME_T --> datetime
        autoread_temp_dkwcum = answer_data[142:150][::-1] ## FLOAT8 --> Double
        autoread_temp_dkwc = answer_data[150:158][::-1] ## FLOAT8 --> Double
        autoread_temp_Kwha = answer_data[158:166][::-1] ## FLOAT8 --> Double
        autoread_temp_Q1 = answer_data[166:174][::-1] ## FLOAT8 --> Double
        autoread_temp_Q2 = answer_data[174:182][::-1] ## FLOAT8 --> Double
        autoread_temp_Q3 = answer_data[182:190][::-1] ## FLOAT8 --> Double
        autoread_temp_Q4 = answer_data[190:][::-1] ## FLOAT8 --> Double

        temp_vars = vars().copy()  ## Делаем копию переменных, т.к. список ?почему-то? изменяется в реальном времени.
        res_array = {}
        for _ in temp_vars:
            if _.startswith('autoread_temp_'):
                res_array[_] = temp_vars[_]
                print(_, temp_vars[_])

        ## Проверяем только
        ## - *kwh
        ## - даты ?
        ## Остальные значения по идеи -1 --> ['bf', 'f0', '00', '00', '00', '00', '00', '00']

        for _ in res_array:
            # print('cur_key','__' + _ + '__')
            if _.strip() == 'autoread_temp_Nsh':
                ## Номер счетчика откуда брать??
                ## ['30', '30', '31', '30', '31', '38', '34', '37', '36', '30'] --> 0010184760
                uspd_counter_number = [str(int(bytes.fromhex(_), 16)) for _ in res_array[_]]
                uspd_counter_number = int(''.join(uspd_counter_number))
                # self.assertEqual(10184760, uspd_counter_number)
                self.assertEqual(uspd_counter_number_as_int, uspd_counter_number)
                # self.assertEqual(['30', '30', '31', '30', '31', '38', '34', '37', '36', '30'], res_array[_])
            elif _.strip() in ['autoread_temp_Dd_mm_yyyy', 'autoread_temp_Atd', 'autoread_temp_Btd',
                               'autoread_temp_Ctd', 'autoread_temp_dtd']:
                ## TODO
                ## Как смотреть -- autoread_temp_Dd_mm_yyyy  ????
                cur_date_from_answer_in_seconds = dec_from_bytes_array(res_array[_])
                self.assertTrue(cur_date_from_answer_in_seconds >= 0)
            elif _.strip().endswith('kwh'): #Akwh, Bkwh, Ckwh, Dkwh
                ## TODO
                ## Как проверять ?
                pass
                # print(_,'kwh_pal')
                # self.assertEqual(1.0, hex_to_double(res_array[_]))
            else:
                # По идеи все остальные параметры должны быть -1
                self.assertEqual(-1.0, hex_to_double(res_array[_]))


if __name__ == "__main__":
    unittest.main()
    # fast = unittest.TestSuite()
#     fast.addTests(TestFastThis)

#======

def get_var_name_and_var_value_from_vars(var_prefix):
    """
    Ищем (вроде) во всех переменных, переменные с префиксом --var_prefix--
    """
    temp_vars = vars().copy()  ## Делаем копию переменных, т.к. список ?почему-то? изменяется в реальном времени.
    print(vars())
    res_array = {}
    for _ in temp_vars:
        if _.startswith(var_prefix):
            res_array[_] = temp_vars[_]
    return res_array
