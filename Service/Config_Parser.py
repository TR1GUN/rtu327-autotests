# Здесь расположим парсер для конфигов
import configparser
import os
from copy import deepcopy
path ='/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
settings = '../uspd_settings.ini'
# настройки берем из конфига

file_path = os.path.join(path,settings)

def get_settings_dictionary_from_ini_file(file_path, uspd_name):
    temp_config_parser = configparser.ConfigParser()
    temp_config_parser.read(file_path)
    dict_schema = temp_config_parser.__dict__['_sections'][uspd_name]
    return dict(dict_schema) ## Кастим OrderDict в обычный


# Читаем сам файл
uspd_rtu_dict = get_settings_dictionary_from_ini_file(file_path, 'RTU-327')

# Вытаскиваем нужные данные
uspd_counter_number = b''.join(list((bytes.fromhex(uspd_rtu_dict.get('counter_number')[_ * 2:_ * 2 + 2])) for _ in range(int(len(uspd_rtu_dict.get('counter_number')) / 2))))  ## Номер счетчика
uspd_counter_number_as_int = int(uspd_rtu_dict.get('counter_number'))
uspd_tcp_ip = uspd_rtu_dict.get('uspd_tcp_ip')
uspd_rtu_protocol_tcp_port = int(uspd_rtu_dict.get('uspd_rtu_protocol_tcp_port'))
uspd_text_protocol_tcp_port = int(uspd_rtu_dict.get('uspd_text_protocol_tcp_port'))
uspd_password = uspd_rtu_dict.get('uspd_password')

# # Парсим наш айпищнике для работы с ним
ip_address = uspd_rtu_dict.get('ip_address')
ip_port = int(uspd_rtu_dict.get('ip_port'))

# ПЕРЕМЕННЫЕ ДЛЯ SSH
addres_ssh = uspd_rtu_dict.get('ip_address')
port_ssh = int(uspd_rtu_dict.get('ssh_port'))
user_login = uspd_rtu_dict.get('user_login')
user_password = uspd_rtu_dict.get('user_password')