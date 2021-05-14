# Здесь расположим класс который будет проверять СТРУКТУРУ коректности Ответа
from copy import deepcopy
def str_to_hex(str_list):
    for i in range(len(str_list)):
        str_list[i] = hex(int('0x' + str_list[i], 16))

    return str_list


def parse_answer(answer_array):  ## Неправильно работает ?
    """
    Парсим ответ(answer_array) с успд.
    """
    result_map = {}
    # Х UINT8 Префиксный байт (имеет значение 0х02)
    result_map['prefix_byte'] = [answer_array[0]]  ##0-индекс пустой??
    # NN UINT16 Длина пакета без учета X,NN,KK
    result_map['package_size'] = answer_array[1:3]  ##0-индекс пустой??
    # II UINT16 Порядковый номер пакета
    result_map['prefix_byte_ww'] = answer_array[3:5]  ##0-индекс пустой??
    # АААА 4 байта Резерв
    result_map['reserve_one'] = answer_array[5:9]  ##0-индекс пустой??
    # SS 2 байт Резерв
    result_map['reserve_two'] = answer_array[9:11]  ##0-индекс пустой??
    # RR UINT8 код результата. 0 – ОК , иначе – код ошибки.
    # Для данного протокола,в случае ошибки данные-ответ на команду должны отсутствовать.
    result_map['result_code'] = [answer_array[11]]
    # DD… Переменная Данные. Ответ на команду-запрос (зависят от типа команды)
    result_map['answer_data'] = answer_array[12:-2]
    # КК UINT16 CRC – контрольная сумма
    result_map['crc'] = answer_array[-2:]
    #
    # result_map = {}
    # # Х UINT8 Префиксный байт (имеет значение 0х02)
    # result_map['prefix_byte'] = []  ##0-индекс пустой??
    # # NN UINT16 Длина пакета без учета X,NN,KK
    # result_map['package_size'] = []  ##0-индекс пустой??
    # # II UINT16 Порядковый номер пакета
    # result_map['prefix_byte_ww'] = []  ##0-индекс пустой??
    # # АААА 4 байта Резерв
    # result_map['reserve_one'] = []  ##0-индекс пустой??
    # # SS 2 байт Резерв
    # result_map['reserve_two'] = []  ##0-индекс пустой??
    # # RR UINT8 код результата. 0 – ОК , иначе – код ошибки.
    # # Для данного протокола,в случае ошибки данные-ответ на команду должны отсутствовать.
    # result_map['result_code'] = []
    # # DD… Переменная Данные. Ответ на команду-запрос (зависят от типа команды)
    # result_map['answer_data'] = []
    # # КК UINT16 CRC – контрольная сумма
    # result_map['crc'] = []
    #
    # template_answer = {
    #     # Х UINT8 Префиксный байт (имеет значение 0х02)
    #     'Х': [0],
    #     # NN UINT16 Длина пакета без учета X,NN,KK
    #     'NN': [1, 2],
    #     # II UINT16 Порядковый номер пакета
    #     'II': [3, 4],
    #     # АААА 4 байта Резерв
    #     'АААА': [5, 6, 7, 8],
    #     # SS 2 байт Резерв
    #     'SS': [9, 10],
    #     # RR UINT8 код результата. 0 – ОК , иначе – код ошибки.
    #     'RR': [11],
    #     # DD… Переменная Данные. Ответ на команду-запрос (зависят от типа команды)
    #     'DD': [],
    #     # КК UINT16 CRC – контрольная сумма
    #     'КК': [-1, -2]
    # }
    #
    # from Service.Constant_Value_Bank import template_answer
    # for i in range(len(answer_array)):
    #     # Переработаем согласно протоколу
    #     if i in template_answer['Х']:
    #         result_map['prefix_byte'].append(answer_array[i])
    #     elif i in template_answer['NN']:
    #         result_map['prefix_byte'].append(answer_array[i])
    #     elif i in template_answer['II']:
    #         result_map['prefix_byte'].append(answer_array[i])
    #     elif i in template_answer['АААА']:
    #         result_map['prefix_byte'].append(answer_array[i])
    #     elif i in template_answer['SS']:
    #         result_map['prefix_byte'].append(answer_array[i])
    #     elif i in template_answer['RR']:
    #         result_map['prefix_byte'].append(answer_array[i])
    #     else:
    #         # сюда отправляем остаток


    return result_map


class CheckUpStructureAnswer:
    """
    Расположим здесь класс валидации корректности пакета.

    """

    answer_bytes = []
    Answer_STR = []
    error = []

    def __init__(self, answer_bytes):
        self.error = []
        self.answer_bytes = []
        # Проверяем что наш ответ не пустой
        if len(answer_bytes) > 0:
            self.answer_bytes = answer_bytes
            self.Answer_STR = self._parsed_answer()
        else:
            self.error = [{'ОШИБКА': 'Получили пустой ответ'}]



    def _parsed_answer(self):
        from work_with_device import hex_bytes_array_to_string, get_right_hex, hex_bytes_to_string, get_crc, \
            bytes_string_to_upper_hex_array , bytes_list_to_string_hex

        answer_bytes = self.answer_bytes
        # Переводим в человеческий вид
        print('---answer_bytes', answer_bytes)
        hex_normal_view_answer_array = hex_bytes_array_to_string(answer_bytes)

        print('---hex_normal_view_answer_array', hex_normal_view_answer_array)

        # print(hex_normal_view_answer_array)
        # Переводим уже в нормальный hex
        # hex_answer_array = str_to_hex(hex_normal_view_answer_array)

        # Теперь - Проверяем минимальный набор символов
        if len(answer_bytes) < 14:
            self.error.append(
                {'ОШИБКА': 'Получили не полный ответ', 'Полученный ответ': str(hex_normal_view_answer_array)})
            # answer = hex_normal_view_answer_array
            answer = None

        else:
            # Если ответ корректный - Разбираем его на словарь
            answer = parse_answer(hex_normal_view_answer_array)
            # result = parse_answer(hex_normal_view_answer_array)

            # Проверяем контрольную сумму
            if answer_bytes[-3:] == ['3c', 'a0', '2f']: print('bad answer')
            result = b''
            for _ in answer_bytes[3:-2]: result += _

            # print('result', result)
            #     # Проверяем crc, который пришел в ответ.
            #     # убираем префикс 0x
            # print('-----result', result)
            # print('-----result', get_crc(result))
            # print('-----hex_bytes_to_string(get_crc(result))', hex_bytes_to_string(get_crc(result)))
            # print('-----get_right_hex(hex_bytes_to_string(get_crc(result)))', get_right_hex(hex_bytes_to_string(get_crc(result))))
            # print('-----get_right_hex(hex_bytes_to_string(get_crc(result))).strip()', get_right_hex(hex_bytes_to_string(get_crc(result))).strip())

            # print('ЗДЕСЬ ВЫЧЕСЛЯЕИ ИЗ ЭТОГО',result)
            CRC_normal = get_right_hex(hex_bytes_to_string(get_crc(result))).strip()
            # print('CRC', bytes_list_to_string_hex(answer_bytes[-2:]))

            # CRC_answer = get_right_hex(
            #     ''.join(bytes_string_to_upper_hex_array(b''.join(answer_bytes[-2:]))).lower()).strip()

            CRC_answer =  bytes_list_to_string_hex(answer_bytes[-2:])

            if int(str(CRC_normal), 16) != int(str(CRC_answer),16):
                self.error.append(
                    {
                        'ОШИБКА': 'CRC не правильно вычислили',
                        'CRC что должна быть ': CRC_normal,
                        'CRC что получили ': CRC_answer,
                        'Полученный ответ': str(hex_normal_view_answer_array)
                    }
                )
            # Проверяем целостность пакета - Длина пакета без учета X,NN,KK
            package_size_list = deepcopy(answer['package_size'])

            # Парсим длину пакета
            package_size = ''
            for i in range(len(package_size_list)):
                package_size = package_size + package_size_list[i]

            # ПРибавляем 5 байт длинны это  X,NN,KK
            package_size = int(package_size, base=16) + 5

            if package_size != len(answer_bytes):
                self.error.append(
                    {
                        'ОШИБКА': 'НЕВЕРНАЯ ДЛИНА ПАКЕТА',
                        'ДЛИНА ПАКЕТА ': len(answer_bytes) - 5,
                        'ЗАЯВЛЕННАЯ ДЛИНА ПАКЕТА ': package_size - 5,
                        'Полученный ответ': str(hex_normal_view_answer_array)
                    }
                )

        # return parse_answer(hex_normal_view_answer_array)
        return answer
