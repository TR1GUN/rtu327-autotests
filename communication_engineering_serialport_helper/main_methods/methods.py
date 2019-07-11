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