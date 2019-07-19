from communication_engineering_serialport_helper.Drivers import serialPort
from communication_engineering_serialport_helper.Drivers.port import settings
from communication_engineering_serialport_helper.Utils import helpActions


def read_raw_tcp(tcp_ip, tcp_port, command, tcp_timeout=25):
    """
    Отправляем команду/читаем по tcp_ip.
    ! Отправляем команду в ее готовом виде !
    Примеры :
            TRANSOPEN
            TRANSADD=1;3;60;010101010101;020202020202;0;4;6;8;0;0
    """
    result_send_command = helpActions.get_command(password=settings.pwd3, command=command)
    print(result_send_command)
    all_strings = serialPort.SerialPort().tcp_connect_read(uspd_server_ip=tcp_ip,
                                                           uspd_server_port=tcp_port,
                                                           command=result_send_command,
                                                           timeout=tcp_timeout)
    if all_strings == 'None': raise Exception("Can't coonect to uspd")
    return all_strings

def read_raw_com_port():
    """ Вроде этот метод просто читает данные с com-порта(указанного в settings.xml)"""
    return serialPort.SerialPort().read_data()


def send_read(password=None, command=None, serial_port=None, tcp_ip=None, tcp_port=None,
              answer_size=65536, logger=None, args_list=None, result_command=None, tcp_timeout=None):
    """ Готовая команда для работы и с COM-портом, так и с TCP/IP

    Большой пример ::
        commands = ['TRANSOPEN', ## Открываем соединение
                    'CLEARTABL', ['TRANSADD',['1','3','60','010101010101','020202020202','0','4','6','8','0','0','1','1','1']],
                    ['WARCHPRM',['1','1','1','1','0','0','0','1']],['WSCHEDAQUAL',['0','0','0','30']],
                    'TRANSCOMMIT'] ## Закрываем соединение

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
    """
    return helpActions.send_command(password=password, command=command, serial_port=serial_port, tcp_ip=tcp_ip,
                                    tcp_port=tcp_port, answer_size=answer_size, logger=logger, args_list=args_list,
                                    result_command=result_command, tcp_timeout=tcp_timeout)



# def send_read_text_rtu327_protocol(command_number=None, command_params=b'', send_command_raw=None):
#     """
#     Главный метод работы с успд - коннектимся к успд, отсылаем строку, получаем ответ.
#     """
#     res = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     res.connect(('192.168.205.10', 14101))  ##тестовая
#     res.settimeout(5)  ## Пока такое решение, на отключение ожидания ответа.
#     # Но надо сделать отключение через цикл со временм. Например 20 сек с последнего байта - отключаемся.
#     if command_number:
#         result_command = send_command(command_number=command_number, command_params=command_params)
#     elif send_command_raw:  ## Не работает корректно ?
#         result_command = send_command_raw  ##не работает правильно
#
#     print(result_command, 'to_send')
#     answer_bytes = []
#
#     for i in range(3):  # Успд не вседа отвечает сразу #Работает ?
#         print(res.sendall(result_command))
#         # Сначала читаем первые 3 байта.
#         # Второй и третий байт - это длина пакета.
#         for _ in range(3):
#             temp_char = res.recv(1)
#             answer_bytes.append(temp_char)
#
#         result_byte_str = b''
#         for _ in answer_bytes[1:]:
#             result_byte_str += _
#         answer_length_without_crc = hex_to_dec(result_byte_str)
#         for _ in range(answer_length_without_crc + 2):  ##Длина тела пакета + 2 байта на crc
#             temp_char = res.recv(1)
#             answer_bytes.append(temp_char)
#
#         if answer_bytes != []:
#             break
#         elif answer_bytes == []:
#             print(str(i), 'try to get answer')
#             continue
#         elif answer_bytes == [] and i == 3:
#             res.close()
#             raise Exception("USPD didn't answer")
#     res.close()
#
#     hex_normal_view_answer_array = hex_bytes_array_to_string(answer_bytes)
#     print(hex_normal_view_answer_array, 'parsed_answer')
#     result = b''
#     for _ in answer_bytes[3:-2]: result += _
#     return parse_answer(hex_normal_view_answer_array)
#



#  ## add serialport
#  ## add serialport
#  ## add serialport
# def send_read_text_protocol(self, command): ## --> private
#         print(uspd_password,uspd_tcp_ip,uspd_tcp_port,command)
#         # if type(command) is list:
#         if isinstance(command,list):
#             all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
#                                     command=command[0], args_list=command[1], tcp_timeout=5)
#         elif isinstance(command, str):
#             all_strings = send_read(password=uspd_password, tcp_ip=uspd_tcp_ip, tcp_port=uspd_tcp_port,
#                                     command=command, tcp_timeout=5)
#         else:
#             raise Exception('Неизвестный тип')
#         return all_strings