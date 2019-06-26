import unittest
from work_with_device import *

class RTU327(unittest.TestCase):

    def test_gettime(self):
        result_answer_map = send_command_and_get_answer(114)
        answer_data = result_answer_map['answer_data'][::-1]
        result_answer_data = ''
        for x in answer_data: result_answer_data += x
        formated_device_time = int(result_answer_data, 16)
        device_datetime = datetime.datetime.utcfromtimestamp(formated_device_time)
        print(device_datetime)

        #check ## секунды не проверяю
        curr_datetime= datetime.datetime.now()
        device_datetime = device_datetime + datetime.timedelta(hours=3)
        difference_between_dates = abs((curr_datetime-device_datetime).total_seconds())
        self.assertTrue(difference_between_dates < 59) # Разница, не больше 59 секунд.

    def test_settime(self):
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
        result_answer_map = send_command_and_get_answer(115, command_params=b'\x10\x0e\x00\x00') #3600 + добавляем 1 час на успд
        # result_answer_map = send_command_and_get_answer(115, command_params=b'\xfe\xff\xff\xff')


        # check ## секунды не проверяю
        # Копия --- test_gettime
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


    def test_getmaxlogid(self): ##
        """ Просто проверяем количество ответа - 4 байта. """
        result_answer_map = send_command_and_get_answer(101, command_params=b'\x01')
        # answer_data = result_answer_map['answer_data'][::-1]
        self.assertEqual(4, len(result_answer_map['answer_data']))

    def test_getlog(self):
        pass

    def test_getshprn(self):
        """серийный номер  ?? откуда брать ??
         10 18 47 60
         """
        result_answer_map = send_command_and_get_answer(101, command_params=b'\x01')
        # answer_data = result_answer_map['answer_data'][::-1]
        self.assertEqual(4, len(result_answer_map['answer_data']))