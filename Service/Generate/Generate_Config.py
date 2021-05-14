# здесь находятся генераторы конфигов
# //-------------------------------------------------------------------------------------------------------------
# //                            Общий базовый класс от которого наследуемся
# //-------------------------------------------------------------------------------------------------------------
class GeneratorConfig:
    """
    Общий класс генерации конфигов
    """
    MeterTable_tag = {}
    Config_tag = {}
    MeterTable = {}
    Config = {}

    def _Generate_Serial(self):
        """Генерируем серийник - ЕТО ВАЖНО -"""

        # Генерируем серийник - ЕТО ВАЖНО -
        from copy import deepcopy
        # СЕРЙИНИК РАВЕН МЕТЕР ИД  и НУЖНОЕ КОЛЛИЧЕТВО НУЛЕЙ ДО 10 символов
        serial = str(deepcopy(self.MeterTable.get('MeterId')))
        serial = '0' * (10 - len(serial)) + serial
        return serial

    def _generation_MeterTable(self):
        """
        Итак - Здесь генерируем данные MeterTable для нашего конфига

        """

        from Service.Generate.Generate_MeterTable import GeneratorMeterTable

        MeterTable = GeneratorMeterTable(redefine_tag=self.MeterTable_tag).Record_MeterTable

        return MeterTable

    # Функция Перезаписи конфига
    def _redefine_tag(self, Config):
        """
        ПЕРЕЗАПИСЫВАЕМ НАШ СГЕНЕРИРВОАННЫЙ СПИСОК ЗНАЧЕНИЯМИ КОТОРЫЕ ХОТИМ ПЕРЕОПРЕДЕЛИТЬ , ЕСЛИ ОНИ КОРРЕКТНЫ
        """
        # Сюда спускаем и перезаписываем ТЭГИ которые были заранее Определены - ЭТО ВАЖНО
        # Перебираем все возможные комбинации
        for tag_castrom_value in self.Config_tag:
            # ЕСЛИ ЭТОТ ТЭГ СУЩЕСТВУЕТТО ЕГО ПЕРЕЗАПСИЫВАЕМ
            if Config.get(tag_castrom_value) is not None:
                # Если ЕСТЬ - То его перезаписываем
                Config[tag_castrom_value] = self.Config_tag[tag_castrom_value]
        return Config


# //-------------------------------------------------------------------------------------------------------------
# //                            Конфиг Электросчетчика
# //-------------------------------------------------------------------------------------------------------------


class GeneratorElectricConfig(GeneratorConfig):
    """
    Общий класс генерации ЭЛЕКТРОНИК КОНФИГ
    """
    MeterTable_tag = {}
    Config_tag = {}
    MeterTable = {}
    Config = {}

    def __init__(self, MeterTable_tag={}, Config_tag={}):
        self.MeterTable_tag = {}
        self.Config_tag = {}
        self.MeterTable = {}

        # ПЕРЕОПРЕДЕЛЯЕМ
        self.MeterTable_tag = MeterTable_tag
        self.Config_tag = Config_tag

        # Получаем запись MeterTable
        self.MeterTable = self._generation_MeterTable()

        # Теперь Генеририруем Конфиг
        self.Config = self._Generate_Config()

        # После чего отправляем его на запись
        self._Record_value_to_Table()

    # Генерация самого конфига
    def _Generate_Config(self):
        """

        Здесь Генерируем наш Конфиг

        """

        # ТЕПЕРЬ - ФОРМИРУЕМ СЛОВАРЬ ЗАПИСИ
        from copy import deepcopy
        import random

        # ФОРМИРУЕМ КОНФИГ
        Config = {
            #   INTEGER NOT NULL,
            'DeviceIdx': deepcopy(self.MeterTable['DeviceIdx']),
            #             BIGINT NOT NULL,
            'Timestamp': random.randint(1500000000, 1609459200),
            #                  TEXT NOT NULL,
            'Serial': self._Generate_Serial(),
            #                    TEXT,
            'Model': 'TEST MODEL',
            #      INTEGER,
            'IntervalPowerArrays': 30,
            #                      BOOLEAN,
            'DST': 1,
            #                   BOOLEAN,
            'Clock': 1,
            #                   BOOLEAN,
            'Tariff': 1,
            #                 BOOLEAN,
            'Reactive': 1,
            #            BOOLEAN,
            'ActiveReverse': 1,
            #          BOOLEAN,
            'ReactiveReverse': 1,
            #   Коофиецент            DOUBLE,
            'CurrentCoeff': float('{:.2f}'.format(float(random.uniform(11.11, 99.99)))),
            #              DOUBLE,
            'VoltageCoeff': float('{:.2f}'.format(float(random.uniform(11.11, 99.99)))),
            #                DOUBLE,
            'MeterConst': float('{:.2f}'.format(float(random.uniform(11.11, 99.99)))),
        }

        # После того как сгенерировали - Перезаписываем нашими тэгами что определяли
        Config_final = self._redefine_tag(Config)

        return Config_final

    def _Record_value_to_Table(self):

        """ НАША ФУНКЦИЯ ЗАПИСИ наших записей в БД """

        from copy import deepcopy
        # Получаем наш список

        Config = deepcopy(self.Config)

        # начинаем формировать команду

        columns_list = \
            [
                'DeviceIdx',
                'Timestamp',
                'Serial',
                'Model',
                'IntervalPowerArrays',
                'DST',
                'Clock',
                'Tariff',
                'Reactive',
                'ActiveReverse',
                'ReactiveReverse',
                'CurrentCoeff',
                'VoltageCoeff',
                'MeterConst'
            ]

        columns = ''
        values = ''

        # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

        for i in range(len(columns_list)):
            columns = columns + columns_list[i] + ' , '

            # если это стринг - то экранируем его
            if type(Config[columns_list[i]]) == str:
                Config[columns_list[i]] = '\"' + Config[columns_list[i]] + '\"'
            values = values + str(Config[columns_list[i]]) + ' , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO ElectricConfig ( ' + columns + ') VALUES  ( ' + values + ' ) ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from Service.Work_With_Database import SQL

        result = SQL(command=command)


# //-------------------------------------------------------------------------------------------------------------
# //                            Конфиг диджитал значений
# //-------------------------------------------------------------------------------------------------------------


class GeneratorDigitalConfig(GeneratorConfig):
    """
    Общий класс генерации ЭЛЕКТРОНИК КОНФИГ
    """
    MeterTable_tag = {}
    Config_tag = {}
    MeterTable = {}
    Config = {}

    def __init__(self, MeterTable_tag={}, Config_tag={}):
        self.MeterTable_tag = {}
        self.Config_tag = {}
        self.MeterTable = {}

        # ПЕРЕОПРЕДЕЛЯЕМ
        self.MeterTable_tag = MeterTable_tag
        self.Config_tag = Config_tag

        # Получаем запись MeterTable
        self.MeterTable = self._generation_MeterTable()

        # Теперь Генеририруем Конфиг
        self.Config = self._Generate_Config()

        # После чего отправляем его на запись
        self._Record_value_to_Table()

    # Генерация самого конфига
    def _Generate_Config(self):
        """

        Здесь Генерируем наш Конфиг

        """

        # ТЕПЕРЬ - ФОРМИРУЕМ СЛОВАРЬ ЗАПИСИ
        from copy import deepcopy
        import random

        # ФОРМИРУЕМ КОНФИГ
        Config = {
            #   INTEGER NOT NULL,
            'DeviceIdx': deepcopy(self.MeterTable['DeviceIdx']),
            #             BIGINT NOT NULL,
            'Timestamp': random.randint(1500000000, 1609459200),
            #                  TEXT NOT NULL,
            'Serial': self._Generate_Serial(),
            #                    TEXT,
            'Model': 'TEST MODEL',
            #                      BOOLEAN,
            'DST': 1,
            #      INTEGER NOT NULL
            'ChannelsIn': 32,
            # INTEGER NOT NULL

            'ChannelsOut': 32,

        }

        # После того как сгенерировали - Перезаписываем нашими тэгами что определяли
        Config_final = self._redefine_tag(Config)

        return Config_final

    def _Record_value_to_Table(self):

        """ НАША ФУНКЦИЯ ЗАПИСИ наших записей в БД """

        from copy import deepcopy
        # Получаем наш список

        Config = deepcopy(self.Config)

        # начинаем формировать команду

        columns_list = \
            [
                'DeviceIdx',
                'Timestamp',
                'Serial',
                'Model',
                'ChannelsIn',
                'ChannelsOut',
                'DST',
            ]

        columns = ''
        values = ''

        # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

        for i in range(len(columns_list)):
            columns = columns + columns_list[i] + ' , '

            # если это стринг - то экранируем его
            if type(Config[columns_list[i]]) == str:
                Config[columns_list[i]] = '\"' + Config[columns_list[i]] + '\"'
            values = values + str(Config[columns_list[i]]) + ' , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO DigitalConfig ( ' + columns + ') VALUES  ( ' + values + ' ) ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from Service.Work_With_Database import SQL

        result = SQL(command=command)


# //-------------------------------------------------------------------------------------------------------------
# //                            Конфиг импульсных счетчиков
# //-------------------------------------------------------------------------------------------------------------


class GeneratorPulseConfig(GeneratorConfig):
    """
    Общий класс генерации ИМПУЛЬСНЫЙ КОНФИГ
    """
    MeterTable_tag = {}
    Config_tag = {}
    MeterTable = {}
    Config = {}

    def __init__(self, MeterTable_tag={}, Config_tag={}):
        self.MeterTable_tag = {}
        self.Config_tag = {}
        self.MeterTable = {}

        # ПЕРЕОПРЕДЕЛЯЕМ
        self.MeterTable_tag = MeterTable_tag
        self.Config_tag = Config_tag

        # Получаем запись MeterTable
        self.MeterTable = self._generation_MeterTable()

        # Теперь Генеририруем Конфиг
        self.Config = self._Generate_Config()

        # После чего отправляем его на запись
        self._Record_value_to_Table()

    # Генерация самого конфига
    def _Generate_Config(self):
        """

        Здесь Генерируем наш Конфиг

        """

        # ТЕПЕРЬ - ФОРМИРУЕМ СЛОВАРЬ ЗАПИСИ
        from copy import deepcopy
        import random

        # ФОРМИРУЕМ КОНФИГ
        Config = {
            #   INTEGER NOT NULL,
            'DeviceIdx': deepcopy(self.MeterTable['DeviceIdx']),
            #             BIGINT NOT NULL,
            'Timestamp': random.randint(1500000000, 1609459200),
            #                  TEXT NOT NULL,
            'Serial': self._Generate_Serial(),
            #                    TEXT,
            'Model': 'TEST MODEL',
            #                      BOOLEAN,
            'DST': 1,
            #      INTEGER NOT NULL
            'Channels': 32,

        }

        # После того как сгенерировали - Перезаписываем нашими тэгами что определяли
        Config_final = self._redefine_tag(Config)

        return Config_final

    def _Record_value_to_Table(self):

        """ НАША ФУНКЦИЯ ЗАПИСИ наших записей в БД """

        from copy import deepcopy
        # Получаем наш список

        Config = deepcopy(self.Config)

        # начинаем формировать команду

        columns_list = \
            [
                'DeviceIdx',
                'Timestamp',
                'Serial',
                'Model',
                'Channels',
                'DST',
            ]

        columns = ''
        values = ''

        # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

        for i in range(len(columns_list)):
            columns = columns + columns_list[i] + ' , '

            # если это стринг - то экранируем его
            if type(Config[columns_list[i]]) == str:
                Config[columns_list[i]] = '\"' + Config[columns_list[i]] + '\"'
            values = values + str(Config[columns_list[i]]) + ' , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO PulseConfig ( ' + columns + ') VALUES  ( ' + values + ' ) ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from Service.Work_With_Database import SQL

        result = SQL(command=command)
