# Здесь расположен класс генерации и записи в таблицу Meter Table


class GeneratorMeterTable:
    """
        Класс для генерации данных в для таблицы MeterTable

    """

    MeterTable = {}
    DeviceIdx_max = None
    MeterId_max = None
    Record_MeterTable = {}

    # ЕСЛИ НАДО БУДЕТ ПЕРЕОПРЕДЕЛИТЬ ТЭГИ
    redefine_tag = {}

    def __init__(self, redefine_tag: dict = {}):
        self.redefine_tag = {}
        self.MeterTable = {}
        self.DeviceIdx_max = None
        self.MeterId_max = None
        self.Record_MeterTable = {}

        # ПЕРЕОПРЕДЕЛЯЕМ ЗНАЧЕНИЯ
        self.redefine_tag = redefine_tag

        # ТЕПЕРЬ ГЕНЕРИРУЕМ ЗНАЧЕНИЯ
        self.Record_MeterTable = self._GenerateMeterTable()

        # А ПОСЛЕ ОТПРАВЛЯЕМ СГЕНЕРИРОВАННЫЕ ЗНАЧЕНИЯ НА ЗАПИСЬ В БД - возвращаем его айдишник
        self.Record_MeterTable['DeviceIdx'] = self._Record_value_to_MeterTable()

    # Получаем МАКСИМАЛЬНОЕ значения MeterId
    def __find_max_MeterId(self):
        """ Сначала ищем максимальное значение MeterId """
        from Service.Work_With_Database import find_to_max_MeterId_in_MeterTable
        # Получаем значение
        DeviceIdx_MeterId_max = find_to_max_MeterId_in_MeterTable()
        # После этого разбираем его на нужные составляющие

        self.MeterId_max = DeviceIdx_MeterId_max['MeterId']
        self.DeviceIdx_max = DeviceIdx_MeterId_max['DeviceIdx']

    def __redefine_tage(self, Record_MeterTable):
        """
        ПЕРЕЗАПИСЫВАЕМ НАШ СГЕНЕРИРВОАННЫЙ СПИСОК ЗНАЧЕНИЯМИ КОТОРЫЕ ХОТИМ ПЕРЕОПРЕДЕЛИТЬ , ЕСЛИ ОНИ КОРРЕКТНЫ
        """
        # Сюда спускаем и перезаписываем ТЭГИ которые были заранее Определены - ЭТО ВАЖНО
        # Перебираем все возможные комбинации
        for tag_castrom_value in self.redefine_tag:
            # ЕСЛИ ЭТОТ ТЭГ СУЩЕСТВУЕТТО ЕГО ПЕРЕЗАПСИЫВАЕМ
            if Record_MeterTable.get(tag_castrom_value) is not None:
                # Если ЕСТЬ - То его перезаписываем
                Record_MeterTable[tag_castrom_value] = self.redefine_tag[tag_castrom_value]
        return Record_MeterTable

    # Генерируем нужную запись
    def _GenerateMeterTable(self):

        """ГЛАВНЫЙ КЛАСС ГЕНЕРАЦИИ ДА ДА ДА"""
        # Первое что делаем - ищем запись
        self.__find_max_MeterId()
        # ТЕПЕРЬ - ФОРМИРУЕМ СЛОВАРЬ ЗАПИСИ
        import random
        if self.MeterId_max == 0:
            MeterId = 1001
        else:
            MeterId = self.MeterId_max + 1

        Meter_TypeId_list = [1, 2, 3, 4, 5, 6, 8, 10, 11, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        Record_MeterTable = \
            {
                # 'DeviceIdx': self.DeviceIdx_max + 1
                # ВНЕШНИЙ АЙДИШНИК - INTEGER NOT NULL,
                'MeterId': MeterId,
                #  СТЕПЕНЬ ИЕРПАРХИИ    INTEGER,
                #     Ставим НОЛЬ
                'ParentId': 0,
                #   ТИП СЧЕТЧИКА  INTEGER NOT NULL
                # Ставим Энергомеру 303
                # 'TypeId': 5,
                # Генерим случайное
                'TypeId': Meter_TypeId_list[random.randint(0, (len(Meter_TypeId_list) - 1))],
                # АДРЕСС TEXT NOT NULL - Ставим заметку что это наши тесты
                'Address': 'ТЕСТ RTU327',
                # ПАРОЛЬ ДЛЯ ЧТЕНИЯ TEXT
                'ReadPassword': '373737373737',
                # ПАРОЛЬ ДЛЯ ЗАПИСИ TEXT
                'WritePassword': '373737373737',
                # ТИП КОНЕНКТА INTEGER NOT NULL
                #     Ставим рандомно один из вариантов последовательных портов
                'InterfaceId': random.randint(1, 4),
                # КОНФИГ ИТЕРФЕЙСА TEXT
                'InterfaceConfig': '9600,8n1',
                # А ВОТ ЭТО ТЭГИ РТУ - ОНИ ИСПОЛЬЗУЮТСЯ
                # Пока пускай будет 1 везде

                # ТИП ОБЬЕКТА INTEGER
                'RTUObjType': 1,
                # НОМЕР ФИДЕРАINTEGER
                'RTUFeederNum': 1,
                # НОМЕР ОБЬЕКТА    INTEGER
                'RTUObjNum': 1,
            }

        # После того как сгенерировали - Перезаписываем нашими тэгами что определяли
        Record_MeterTable_final = self.__redefine_tage(Record_MeterTable)

        return Record_MeterTable_final

    def _Record_value_to_MeterTable(self):

        """ НАША ФУНКЦИЯ ЗАПИСИ наших записей в БД """

        from copy import deepcopy
        # Получаем наш список

        Record_MeterTable = deepcopy(self.Record_MeterTable)

        # начинаем формировать команду

        columns_list \
            = [
            'MeterId',
            'ParentId',
            'TypeId',
            'Address',
            'ReadPassword',
            'WritePassword',
            'InterfaceId',
            'InterfaceConfig',
            'RTUObjType',
            'RTUFeederNum',
            'RTUObjNum'
        ]

        columns = ''
        values = ''

        # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

        for i in range(len(columns_list)):
            columns = columns + columns_list[i] + ' , '

            # если это стринг - то экранируем его
            if type(Record_MeterTable[columns_list[i]]) == str:
                Record_MeterTable[columns_list[i]] = '\"' + Record_MeterTable[columns_list[i]] + '\"'
            values = values + str(Record_MeterTable[columns_list[i]]) + ' , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO MeterTable ( ' + columns + ') VALUES  ( ' + values + ' ) ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from Service.Work_With_Database import SQL

        result = SQL(command=command)

        DeviceIdx = self._select_device_idx_record(MeterId=Record_MeterTable['MeterId'])

        return DeviceIdx

    def _select_device_idx_record(self, MeterId):
        """
        Здесь Мы селектим idx нашей записи

        """
        # Собираем команду
        command = 'SELECT DeviceIdx FROM MeterTable WHERE MeterId = ' + str(MeterId) + ' ; '

        from Service.Work_With_Database import SQL

        result = SQL(command=command)
        # После чего возвращаем интовое значение

        return int(result)
