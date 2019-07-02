"""
py -m pytest device_tests.py::RTU327::test_gettime -s -v
"""
import unittest
from work_with_device import *
import work_with_device


class RTU327(unittest.TestCase):

    """'3c', 'a0', '2f' = неправильная контрольная сумма - жопа ответа
    прокинуть в каждый тест ? """

    def test_ver(self):
        result_answer_map = send_command_and_get_answer(3)
        answer_data = result_answer_map['answer_data'][::-1]
        result_answer_data = ''
        for x in answer_data: result_answer_data += x
        formated_device_time = int(result_answer_data, 16)
        device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        print(device_datetime)

        # check ## секунды не проверяю
        # curr_datetime = datetime.datetime.now()
        # device_datetime = device_datetime + datetime.timedelta(hours=3)
        # difference_between_dates = abs((curr_datetime - device_datetime).total_seconds())
        # self.assertTrue(difference_between_dates < 59)  # Разница, не больше 59 секунд.

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
        # result_answer_map = send_command_and_get_answer(115) ## Без доп. параметров работает
        res_hex_time = get_right_hex(hex(hour_in_seconds)[2:])
        amount_of_byte = len(res_hex_time) / 2
        result_hex_time = b''
        if amount_of_byte != 4:
            for _ in range(4 - int(amount_of_byte)):
                result_hex_time += b'\x00'
        result_hex_time += res_hex_time.encode()
        result_answer_map = send_command_and_get_answer(115,
                                                        # command_params=b'\x10\x0e\x00\x00')  # 3600 + добавляем 1 час на успд
                                                        # command_params=b'\xf0\xf1\xff\xff')  # 3600 + добавляем 1 час на успд
                                                        command_params=b'\x00\x00\x00\xff')  # 3600 + добавляем 1 час на успд
        # result_answer_map = send_command_and_get_answer(115, command_params=b'\xfe\xff\xff\xff')
        # check ## секунды не проверяю
        # Копия --- test_gettime


        """ Проверка """
        # result_answer_map = send_command_and_get_answer(114)
        # answer_data = result_answer_map['answer_data'][::-1]
        # result_answer_data = ''
        # for x in answer_data: result_answer_data += x
        # formated_device_time = int(result_answer_data, 16)
        # device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        # curr_datetime = datetime.datetime.now()
        # device_datetime = device_datetime + datetime.timedelta(hours=3)
        # difference_between_dates = abs((curr_datetime - device_datetime).total_seconds())
        # self.assertTrue(3540 < difference_between_dates < 3660)  # Разница +- 1 минута

    def test_get_maxlogid(self):  ##
        """ Просто проверяем количество ответа - 4 байта. """
        result_answer_map = send_command_and_get_answer(101, command_params=b'\x01')
        # answer_data = result_answer_map['answer_data'][::-1]
        self.assertEqual(4, len(result_answer_map['answer_data']))

    def test_get_log(self):
        Nsect = b'\x00\x00\x00\x01'
        Id = b'\x00\x00\x00\x01'
        Num = b'\x00\x01'
        result_answer_map = send_command_and_get_answer(117, command_params=Nsect + Id + Num)
        print(result_answer_map)
        self.assertEqual(13, len(result_answer_map))

    def test_get_shprm(self): ## Пока просто смотрим
        """серийный номер успд ?? откуда брать ??
         10 18 47 60
         """
        Nsh =b'\x00\x10\x18\x47\x60'
        result_answer_map = send_command_and_get_answer(112, command_params=Nsh)
        answer_data = result_answer_map['answer_data'][::-1] ##перевернутый ответ
        # answer_data = result_answer_map['answer_data'] ##перевернутый ответ
        print(len(answer_data))
        print(len(answer_data))
        print(len(answer_data))
        vers = answer_data[:2]
        typ_sh = answer_data[2]
        kt = answer_data[3:11] ##FLOAT8
        kn = answer_data[11:19] ##FLOAT8
        m = answer_data[19:27] ##FLOAT8
        interv = answer_data[27]
        syb_rnk = answer_data[28:32] ##INT32
        n_ob = answer_data[32:36] ##INT32
        n_fid = answer_data[36:] ##INT32
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

        # print(answer_data)
        # self.assertEqual(4, len(result_answer_map['answer_data']))

    def test_get_pok(self):  ##
        """ Просто проверяем количество ответа - 8 байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        NSH  =b'\x00\x10\x18\x47\x60'
        Chnl  = b'\x01'
        Time  = b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(113, command_params=NSH+Chnl+Time)
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertEqual(8, len(answer_data))

    def test_get_lp(self):  ##
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh =b'\x00\x10\x18\x47\x60'
        Kanal = b'\x01'
        Tstart = b'\x00\x00\x00\x00'
        Kk = b'\x00\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(111, command_params=Nsh+Kanal+Tstart+Kk)
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        self.assertEqual(15, len(answer_data))

    def test_get_shortlp(self):        ## undone
        ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh =b'\x00\x10\x18\x47\x60'
        Kanal = b'\x01'
        Interval = b'\x00'
        Tstart = b'\x00\x00\x00\x00'
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
        Nsh =b'\x00\x10\x18\x47\x60'
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
        N_SH =b'\x00\x10\x18\x47\x60'
        Tday  = b'\x00\x00\x00\x00'
        Kanal = b'\x01'
        Kk = b'\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(109, command_params=N_SH + Tday + Kanal + Kk)
        answer_data = result_answer_map['answer_data'][::-1]
        # print(answer_data)
        # print(len(answer_data))
        self.assertEqual(198,len(answer_data))

    def test_get_mtrlog(self):  ## undone
        """ Просто проверяем количество ответа - ?? байта.
        Номер счетчика - b'\x00\x10\x18\x47\x60'
        """
        Nsh = b'\x00\x10\x18\x47\x60'
        Tstart = b'\x00\x00\x00\x00'
        Cnt = b'\x00\x01'
        #Какое время задать -- ? Пока что -- b'\x00\x00\x00\x00'
        result_answer_map = send_command_and_get_answer(116, command_params=Nsh + Tstart + Cnt)
        answer_data = result_answer_map['answer_data'][::-1]
        print(answer_data)
        print(len(answer_data))
        # ?? self.assertEqual(198,len(answer_data)) ??

if __name__ == "__main__":
    unittest.main()
    # fast = unittest.TestSuite()
#     fast.addTests(TestFastThis)