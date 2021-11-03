# здесь расположим нашу функцию которая с помощью SSH соединения будет выполнять команду SQL

def SQL(command: str):
    """
    Функция для работы с БД через SSH

    Принимает на вход команду которую надо исполнить

    И возвращает результат
    """
    # ДЕЛАЕМ КОНЕКТ ПО SSH
    # для начала импортируем наш модуль конекта
    from GenerateMeterData.Service.Connect_to_SSH import ConnectSSH

    SSH = ConnectSSH()

    # и Делаем нашу команду
    print('--->',command)
    result = SSH.Exec_command_return_result('sudo sqlite3 /var/opt/uspd/meterdb/meter.db \'' + command + '\' ')
    # Закрываем соеденение
    # if result == 'Error: unable to open database file' :
    #     result = SSH.Exec_command_return_result('sudo sqlite3 /var/opt/uspd/meterdb/meter.db \'' + command + '\' ')
    # print(result)




    SSH.close()

    return result


def find_to_max_MeterId_in_MeterTable():
    """
    Функция для поиска максимального MeterId

    ВОЗВРАЩАЕТ СЛВОАРЬ - МАКСИСМАЛЬНОГО ЗНАЧЕНИЯ MeterId и соответсвеного ему DeviceIdx
    """
    # Формируем команду
    command = 'SELECT max(MeterId), DeviceIdx FROM MeterTable ;'
    # Запускаем ее
    result = SQL(command=command)

    # проверяем что заселектили не пустое значение
    if len(result) > 2:
        # Сначала очищаем ее от мусора
        result = result.strip('\\n')
        result = result.strip(' ')

        # После чего превращаем в словарь
        result = result.split('|')
        result = \
            {
                'MeterId': int(result[0]),
                'DeviceIdx': int(result[1])
            }

    else:
        result = \
            {
                'MeterId': 0,
                'DeviceIdx': 0
            }
    return result



