# Здесь расположим наш конструктор правильного ответа команды
from work_with_device import hex_bytes_array_to_string, get_right_hex, hex_bytes_to_string, get_crc, \
    bytes_string_to_upper_hex_array
from Service.Constant_Value_Bank import answer_default_values


# Функция КОНСТРУИРОВАНИЯ массива из байтов из байтовой строки
def construct_hex_str_to_hex_list(hex_str):
    hex_list = []
    # пункт первый - достраиваем на один 0 если у нас нечетная длина
    if len(hex_list) % 2 > 0:
        hex_str = '0' + hex_str

    # Теперь проходимся по каждому элементу
    for i in range(int(len(hex_str)/2)):
        # Теперь берем элемент
        element = hex_str[i*2] + hex_str[(i*2)+1]

        hex_list.append(element)
    # hex_list.reverse()
    return hex_list


def Constructor_Answer(data_bytes):
    template_answer = {
                       'prefix_byte': hex_bytes_array_to_string(answer_default_values['Х']),
                       'package_size': None,
                       'prefix_byte_ww': hex_bytes_array_to_string(answer_default_values['II']),
                       'reserve_one': hex_bytes_array_to_string(answer_default_values['АААА']),
                       'reserve_two': hex_bytes_array_to_string(answer_default_values['SS']),
                       'result_code': hex_bytes_array_to_string(answer_default_values['RR']),
                       'answer_data': None,
                       'crc': None
                       }

    data_list = [None] * len(data_bytes)
    # Делаем массив байтов
    from work_with_device import get_right_hex
    for i in range(len(data_bytes)):
        data_list[i] = bytes.fromhex(get_right_hex(hex(data_bytes[i])[2:]))

    # Вычисляем длину пакета
    package_size = len(
        template_answer['prefix_byte_ww'] + template_answer['reserve_one'] + template_answer['reserve_two'] +
        template_answer['result_code'] + hex_bytes_array_to_string(data_list))

    # ТЕПЕРЬ ПЕРЕВОДИМ В HEX и срезаем префикс
    package_size_list = hex(package_size).strip('0x')
    # Добавляем нужные нули
    # ищем нужное количество , что нужно добавить
    # Добавляем
    package_size_list = '0' * (4 - len(package_size_list)) + package_size_list

    # package_size_hex_list = [package_size_list[:2], package_size_list[2:]]

    package_size_hex_list = construct_hex_str_to_hex_list(package_size_list)
    template_answer['package_size'] = package_size_hex_list
    # И вычиляем контрольную сумму
    command = answer_default_values['II'] + answer_default_values['АААА'] + \
              answer_default_values['SS'] + answer_default_values['RR'] + data_list
    data = b''
    for _ in command: data += _

    # ТЕПЕРЬ ВЫЧИСЛЯЕМ CRC
    CRC_value = get_right_hex(hex_bytes_to_string(get_crc(data))).strip()

    template_answer['crc'] = construct_hex_str_to_hex_list('0' * (4 - len(CRC_value)) + CRC_value)
    # template_answer['crc'] = CRC_value

    template_answer['answer_data'] = hex_bytes_array_to_string(data_list)

    return template_answer

#
# b'\x01\x00 \x00\x00\x00\x00 \x00\x00 \x00020102'
#
# b'\x01\x00 \x00\x00\x00\x00 \x00\x00 020102'
