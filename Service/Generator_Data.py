# Итак - Здесь расположим наши генераторы данных

class GeneratorDataConfig:
    """Класс Генерации данных для запроса GETSHPRM """

    MeterTable_tag = {}
    Config_tag = {}
    MeterId = 0
    GETSHPRM = {}
    Serial = 0

    def __init__(self, MeterTable_tag: dict = {}, Config_tag: dict = {}):
        self.MeterId = 0
        self.Serial = 0
        self.MeterTable_tag = {}
        self.Config_tag = {}
        self.GETSHPRM = {}

        # Итак - Теперь переопределяем данные
        self.MeterTable_tag = MeterTable_tag
        self.Config_tag = Config_tag

        self.GETSHPRM = self._generate_data_for_GETSHPRM()

    def _generate_ElConfig(self):
        """
        Здесь генерируем данные  El Config
        """

        from Service.Generate.Generate_Config import GeneratorElectricConfig
        from Service.Generate.Generate_ElectricPowerValues import GeneratorElectricPowerValues
        Config = GeneratorElectricConfig(MeterTable_tag=self.MeterTable_tag, Config_tag=self.Config_tag)

        # Теперь вытаскиваем данные что записали
        # ТЕПЕРЬ ЗАПИСЫВАЕМ ПРОФИЛЬ МОЩНОСТИ
        ElectricPowerValues = GeneratorElectricPowerValues(DeviceIdx=Config.MeterTable.get('DeviceIdx'),
                                                           RecordTypeId='ElArr1ConsPower',
                                                           Redefine_tag={'cTime': 30},
                                                           Count_timestamp=1).ElectricPowerValues

        RecordData = {}
        RecordData.update(Config.MeterTable)
        RecordData.update(Config.Config)

        # Теперь - Берем последний ключ ид и по нему берем
        for keys in ElectricPowerValues:
            RecordData['IntervalPowerArrays'] = ElectricPowerValues[keys]['cTime']

        return RecordData

    def _generate_data_for_GETSHPRM(self):
        """
        Здесь генерируем наши данные для нашей команды
        """

        # сначала записываем все нужные данные в БД
        RecordData = self._generate_ElConfig()

        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = RecordData['MeterId']
        self.Serial = RecordData['Serial']
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа

        from Service.Service_function import MeterId_from_USPD_to_RTU

        GETSHPRM = \
            {
                # Vers Версия параметров ( текущее значение 1) INT16
                'Vers': 1,
                # Typ_Sh Тип счетчика INT8
                'Typ_Sh': MeterId_from_USPD_to_RTU(RecordData['TypeId']),
                # Kt Коэффициент трансформации по току FLOAT8
                'Kt': RecordData['CurrentCoeff'],
                # Kn Коэффициент трансформации по напряжению FLOAT8
                'Kn': RecordData['VoltageCoeff'],
                # M Множитель FLOAT8
                'M': RecordData['MeterConst'],
                # Interv Интервал профиля нагрузки INT8
                'Interv': RecordData['IntervalPowerArrays'],
                # Syb_Rnk Тип объекта INT32
                'Syb_Rnk': RecordData['RTUObjType'],
                # N_Ob Номер объекта INT32
                'N_Ob': RecordData['RTUObjNum'],
                # N_Fid Номер фидера INT32
                'N_Fid': RecordData['RTUFeederNum'],
            }

        return GETSHPRM


# //--------------------------------------------------------------------------------------------------------------
# //
# //--------------------------------------------------------------------------------------------------------------

class GenerateGETPOK:
    """Класс Генерации данных для запроса GETPOK """

    RecordTypeId = ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']

    Count_timestamp = 1

    MeterTable_tag = {}
    Redefine_tag = {}
    MeterId = 0
    Serial = 0
    DeviceIdx = 0
    Timestamp = 0
    GETPOK = {}

    def __init__(self, MeterTable_tag: dict = {}, Redefine_tag: dict = {}, Count_timestamp: int = 1,
                 RecordTypeId: list = ['ElMomentEnergy']):

        self.RecordTypeId = RecordTypeId
        self.Count_timestamp = 1
        self.MeterId = 0
        self.Serial = 0
        self.DeviceIdx = 0
        self.Timestamp = 0
        self.MeterTable_tag = {}
        self.Redefine_tag = {}
        self.GETPOK = {}

        # Итак - Теперь переопределяем данные
        self.Count_timestamp = Count_timestamp

        self.MeterTable_tag = MeterTable_tag
        self.Redefine_tag = Redefine_tag

        self.GETPOK = self._generate_data_for_GETPOK()

    def _generate_Config(self):
        """
        Метод для генерации конфига
        """
        from Service.Generate.Generate_Config import GeneratorElectricConfig
        # СНАЧАЛА - ГЕНЕРИРУЕМ КОНФИГ и МЕТЕР ДАТА
        Config = GeneratorElectricConfig(MeterTable_tag=self.MeterTable_tag, Config_tag={})

        RecordData = {}
        RecordData.update(Config.MeterTable)

        RecordData.update(Config.Config)
        return RecordData

    def _generate_ElectricEnergyValues(self):
        """
        Метод для генерации Энергии чо так , да вот так
        """
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues
        from copy import deepcopy

        ElectricEnergyValues_dict = {}
        for i in range(len(self.RecordTypeId)):
            ElectricEnergyValues = GeneratorElectricEnergyValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                                 RecordTypeId=self.RecordTypeId[i],
                                                                 Redefine_tag={},
                                                                 Count_timestamp=self.Count_timestamp
                                                                 ).ElectricEnergyValues

            ElectricEnergyValues_dict.update(ElectricEnergyValues)

        # Теперь возвращаем в зад ЭТО

        return ElectricEnergyValues_dict

    def _generate_data_for_GETPOK(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # сначала записываем все нужные данные в БД
        RecordData = self._generate_ElectricEnergyValues()

        # print('----->', RecordData)
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETPOK = {}
        for key in RecordData:
            GETPOK_element_dict = {
                'Id': RecordData[key].get('Id'),
                'Ap': RecordData[key].get('A+0'),
                'Am': RecordData[key].get('A-0'),
                'Rp': RecordData[key].get('R+0'),
                'Rm': RecordData[key].get('R-0'),
                'DeviceIdx': RecordData[key].get('DeviceIdx'),
                'Timestamp': RecordData[key].get('Timestamp')
            }

            GETPOK[RecordData[key].get('Timestamp')] = GETPOK_element_dict

        return GETPOK


# //--------------------------------------------------------------------------------------------------------------
# //                Запрос на передачу профиля расходов коммерческого интервала - ПРОФИЛЬ МОЩНОСТИ
# //--------------------------------------------------------------------------------------------------------------

class GenerateGETLP:
    """Класс Генерации данных для запроса GETLP """

    RecordTypeId = ['ElArr1ConsPower']

    Count_timestamp = 1

    MeterTable_tag = {}
    Redefine_tag = {}
    MeterId = 0
    Serial = 0
    DeviceIdx = 0
    Timestamp = 0
    GETLP = {}
    cTime = 30

    def __init__(self, MeterTable_tag: dict = {}, Redefine_tag: dict = {}, Count_timestamp: int = 1, cTime: int = 30):
        self.Count_timestamp = 1
        self.MeterId = 0
        self.Serial = 0
        self.DeviceIdx = 0
        self.Timestamp = 0
        self.MeterTable_tag = {}
        self.Redefine_tag = {}
        self.GETLP = {}

        # Итак - Теперь переопределяем данные
        self.cTime = cTime
        self.Count_timestamp = Count_timestamp

        self.MeterTable_tag = MeterTable_tag
        self.Redefine_tag = Redefine_tag

        self.GETLP = self._generate_data_for_GETLP()

    def _generate_Config(self):
        """
        Метод для генерации конфига
        """
        from Service.Generate.Generate_Config import GeneratorElectricConfig
        # СНАЧАЛА - ГЕНЕРИРУЕМ КОНФИГ и МЕТЕР ДАТА
        Config = GeneratorElectricConfig(MeterTable_tag=self.MeterTable_tag, Config_tag={})

        RecordData = {}
        RecordData.update(Config.MeterTable)

        RecordData.update(Config.Config)
        return RecordData

    def _generate_ElectricPowerValues(self):
        """
        Метод для генерации Энергии чо так , да вот так
        """
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_ElectricPowerValues import GeneratorElectricPowerValues

        ElectricPowerValues_dict = {}
        for i in range(len(self.RecordTypeId)):
            ElectricPowerValues = GeneratorElectricPowerValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                               RecordTypeId=self.RecordTypeId[i],
                                                               Redefine_tag={},
                                                               Count_timestamp=self.Count_timestamp,
                                                               cTime=self.cTime).ElectricPowerValues

            ElectricPowerValues_dict.update(ElectricPowerValues)

        # Теперь возвращаем в зад ЭТО

        return ElectricPowerValues_dict

    def _generate_data_for_GETLP(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # сначала записываем все нужные данные в БД
        RecordData = self._generate_ElectricPowerValues()

        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETLP = {}
        for key in RecordData:
            GETLP_element_dict = {
                'Id': RecordData[key].get('Id'),
                'cTime': RecordData[key].get('cTime'),
                'Pp': RecordData[key].get('P+'),
                'Pm': RecordData[key].get('P-'),
                'Qp': RecordData[key].get('Q+'),
                'Qm': RecordData[key].get('Q-'),
                'isPart': RecordData[key].get('isPart'),
                'isOvfl': RecordData[key].get('isOvfl'),
                'isSummer': RecordData[key].get('isSummer'),
                'DeviceIdx': RecordData[key].get('DeviceIdx'),
                'Timestamp': RecordData[key].get('Timestamp')
            }

            GETLP[RecordData[key].get('Timestamp')] = GETLP_element_dict

        return GETLP


# //--------------------------------------------------------------------------------------------------------------
# //                    Различные генерации
# //--------------------------------------------------------------------------------------------------------------


class GenerateTest:
    RecordTypeId = 'ElMomentEnergy'
    Count_timestamp = 1
    MeterTable_tag = {}
    Redefine_tag = {}
    MeterId = 0
    Serial = 0
    DeviceIdx = 0
    Timestamp = 0

    data = None

    def __init__(self, MeterTable_tag: dict = {}, Redefine_tag: dict = {}, Count_timestamp: int = 1):
        self.Count_timestamp = 1
        self.MeterId = 0
        self.Serial = 0
        self.DeviceIdx = 0
        self.Timestamp = 0
        self.MeterTable_tag = {}
        self.Redefine_tag = {}
        self.GETPOK = {}

        # Итак - Теперь переопределяем данные
        self.Count_timestamp = Count_timestamp

        self.MeterTable_tag = MeterTable_tag
        self.Redefine_tag = Redefine_tag

        self.data = self._generate_data()

    def _generate_Config(self):
        """
        Метод для генерации конфига
        """
        from Service.Generate.Generate_Config import GeneratorElectricConfig
        # СНАЧАЛА - ГЕНЕРИРУЕМ КОНФИГ и МЕТЕР ДАТА
        Config = GeneratorElectricConfig(MeterTable_tag=self.MeterTable_tag, Config_tag={})

        RecordData = {}
        RecordData.update(Config.MeterTable)

        RecordData.update(Config.Config)
        return RecordData

    def _generate_ElectricEnergyValues(self):
        """
        Метод для генерации Энергии чо так , да вот так
        """
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues

        ElectricEnergyValues = GeneratorElectricEnergyValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                             RecordTypeId=self.RecordTypeId,
                                                             Redefine_tag={},
                                                             Count_timestamp=self.Count_timestamp,
                                                             ).ElectricEnergyValues

        # Теперь возвращаем в зад ЭТО

        return ElectricEnergyValues

    def _generate_ElectricPowerValues(self):
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_ElectricPowerValues import GeneratorElectricPowerValues

        ElectricPowerValues = GeneratorElectricPowerValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                           RecordTypeId=self.RecordTypeId,
                                                           Redefine_tag={},
                                                           Count_timestamp=self.Count_timestamp).ElectricPowerValues

        # Теперь возвращаем в зад ЭТО
        # print('---->', ElectricPowerValues)
        return ElectricPowerValues

    def _generate_ElectricQualityValues(self):
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_ElectricQualityValues import GeneratorElectricQualityValues

        ElectricQualityValues = GeneratorElectricQualityValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                               RecordTypeId=self.RecordTypeId,
                                                               Redefine_tag={},
                                                               Count_timestamp=self.Count_timestamp).ElectricQualityValues

        # Теперь возвращаем в зад ЭТО
        # print('---->', ElectricQualityValues)

        return ElectricQualityValues

    def _generate_data(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # сначала записываем все нужные данные в БД
        # RecordData = self._generate_ElectricEnergyValues()
        # RecordData = self._generate_ElectricPowerValues()
        RecordData = self._generate_ElectricQualityValues()
        return RecordData


#
# a = GenerateTest(Count_timestamp=3)
#


# //--------------------------------------------------------------------------------------------------------------
# //                      Генерация для команды - GETTESTS - Запрос замеров параметров электросети.
# //--------------------------------------------------------------------------------------------------------------


class GenerateGETTESTS:
    """Класс Генерации данных для запроса GETLP """

    RecordTypeId = ['ElMomentQuality']

    Count_timestamp = 1

    MeterTable_tag = {}
    Redefine_tag = {}
    MeterId = 0
    Serial = 0
    DeviceIdx = 0
    Timestamp = 0
    GETTESTS = {}
    cTime = 30

    def __init__(self, MeterTable_tag: dict = {}, Redefine_tag: dict = {}, Count_timestamp: int = 1):
        self.Count_timestamp = 1
        self.MeterId = 0
        self.Serial = 0
        self.DeviceIdx = 0
        self.Timestamp = 0
        self.MeterTable_tag = {}
        self.Redefine_tag = {}
        self.GETTESTS = {}

        # Итак - Теперь переопределяем данные

        self.Count_timestamp = Count_timestamp

        self.MeterTable_tag = MeterTable_tag
        self.Redefine_tag = Redefine_tag

        self.GETTESTS = self._generate_data_for_GETTESTS()

    def _generate_Config(self):
        """
        Метод для генерации конфига
        """
        from Service.Generate.Generate_Config import GeneratorElectricConfig
        # СНАЧАЛА - ГЕНЕРИРУЕМ КОНФИГ и МЕТЕР ДАТА
        Config = GeneratorElectricConfig(MeterTable_tag=self.MeterTable_tag, Config_tag={})

        RecordData = {}
        RecordData.update(Config.MeterTable)

        RecordData.update(Config.Config)
        return RecordData

    def _generate_ElectricQualityValues(self):
        """
        Метод для генерации Энергии чо так , да вот так
        """
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_ElectricQualityValues import GeneratorElectricQualityValues

        ElectricQualityValues_dict = {}
        for i in range(len(self.RecordTypeId)):
            ElectricQualityValues = GeneratorElectricQualityValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                                   RecordTypeId=self.RecordTypeId[i],
                                                                   Redefine_tag={},
                                                                   Count_timestamp=self.Count_timestamp
                                                                   ).ElectricQualityValues

            ElectricQualityValues_dict.update(ElectricQualityValues)

        # Теперь возвращаем в зад ЭТО

        return ElectricQualityValues_dict

    def _generate_data_for_GETTESTS(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # сначала записываем все нужные данные в БД
        RecordData = self._generate_ElectricQualityValues()
        print(RecordData)
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETTESTS = {}
        for key in RecordData:
            GETTESTS_element_dict = {
                'Id': RecordData[key].get('Id'),
                'Wa': RecordData[key].get('PA'),
                'Wb': RecordData[key].get('PB'),
                'Wc': RecordData[key].get('PC'),
                'VAa': RecordData[key].get('SA'),
                'VAb': RecordData[key].get('SB'),
                'VAc': RecordData[key].get('SC'),
                'FREQ': RecordData[key].get('Freq'),
                'Ia': RecordData[key].get('IA'),
                'Ib': RecordData[key].get('IB'),
                'Ic': RecordData[key].get('IC'),
                'Ua': RecordData[key].get('UA'),
                'Ub': RecordData[key].get('UB'),
                'Uc': RecordData[key].get('UC'),
                'PFangA': RecordData[key].get('LOL'),
                'PFangB': RecordData[key].get('LOL'),
                'PFangC': RecordData[key].get('LOL'),
                'PHangB': RecordData[key].get('AngAB'),
                'PhangC': RecordData[key].get('AngAC'),
                'Timestamp': RecordData[key].get('Timestamp')
            }

            GETTESTS[RecordData[key].get('Timestamp')] = GETTESTS_element_dict

        return GETTESTS


# //--------------------------------------------------------------------------------------------------------------
# //                      Генерация для команды - GETMTRLOG - Запрос журнала событий по счетчикам
# //--------------------------------------------------------------------------------------------------------------


class GenerateGETMTRLOG:
    """Класс Генерации данных для запроса GETMTRLOG """

    RecordTypeId = ["ElJrnlPwr", "ElJrnlTimeCorr", "ElJrnlReset", "ElJrnlOpen", "ElJrnlPwrA", "ElJrnlPwrB",
                    "ElJrnlPwrC"]

    Count_timestamp = 1

    MeterTable_tag = {}
    Redefine_tag = {}
    MeterId = 0
    Serial = 0
    DeviceIdx = 0
    Timestamp = 0
    GETMTRLOG = {}

    def __init__(self, MeterTable_tag: dict = {}, Redefine_tag: dict = {}, Count_timestamp: int = 1,
                 RecordTypeId: list = ["ElJrnlPwr", "ElJrnlTimeCorr", "ElJrnlReset", "ElJrnlOpen", "ElJrnlPwrA",
                                       "ElJrnlPwrB", "ElJrnlPwrC"]):

        self.RecordTypeId = RecordTypeId
        self.Count_timestamp = 1
        self.MeterId = 0
        self.Serial = 0
        self.DeviceIdx = 0
        self.Timestamp = 0
        self.MeterTable_tag = {}
        self.Redefine_tag = {}
        self.GETMTRLOG = {}

        # Итак - Теперь переопределяем данные

        self.Count_timestamp = Count_timestamp

        self.MeterTable_tag = MeterTable_tag
        self.Redefine_tag = Redefine_tag

        self.GETMTRLOG = self._generate_data_for_GETMTRLOG()

    def _generate_Config(self):
        """
        Метод для генерации конфига
        """
        from Service.Generate.Generate_Config import GeneratorElectricConfig
        # СНАЧАЛА - ГЕНЕРИРУЕМ КОНФИГ и МЕТЕР ДАТА
        Config = GeneratorElectricConfig(MeterTable_tag=self.MeterTable_tag, Config_tag={})

        RecordData = {}
        RecordData.update(Config.MeterTable)

        RecordData.update(Config.Config)
        return RecordData

    def _generate_JournalValues(self):
        """
        Метод для генерации Энергии чо так , да вот так
        """
        # начала генерируем наш конфиг
        RecordData_Config = self._generate_Config()

        # Перезаписываем наши поля которые нам нужны
        self.Serial = RecordData_Config.get('Serial')

        # Теперь когда получиили конфиг можно сгенерировать Энергию. ШО уж там

        from Service.Generate.Generate_JournalValues import GeneratorJournalValues


        JournalValues_dict = {}
        for i in range(len(self.RecordTypeId)):
            print('пошли')
            JournalValues = GeneratorJournalValues(DeviceIdx=RecordData_Config.get('DeviceIdx'),
                                                   RecordTypeId=self.RecordTypeId[i],
                                                   Redefine_tag={},
                                                   Count_timestamp=self.Count_timestamp
                                                   ).JournalValues

            JournalValues_dict.update(JournalValues)

        # Теперь возвращаем в зад ЭТО

        return JournalValues_dict

    def _generate_data_for_GETMTRLOG(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        print('dfdfdf')
        # сначала записываем все нужные данные в БД
        RecordData = self._generate_JournalValues()

        # print('----->', RecordData)
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETMTRLOG = {}
        for key in RecordData:
            GETMTRLOG_element_dict = {
                'Id': RecordData[key].get('Id'),
                'evTime': RecordData[key].get('Timestamp'),
                'evType': RecordData[key].get('EventId'),
                'Event': RecordData[key].get('Event'),
                'DeviceIdx': RecordData[key].get('DeviceIdx'),
                'Timestamp': RecordData[key].get('Timestamp')
            }

            GETMTRLOG[RecordData[key].get('Id')] = GETMTRLOG_element_dict

        return GETMTRLOG


def define_count_measure(count: int, measure_list: list):
    """
    Здесь определяем рандомное количество элементов из нужного нм списка

    """

    from random import randint
    define_measure_list = set

    i = 0
    while i == count:

        len_measure_list = len(define_measure_list)
        # генерирум число
        generate = randint(0, len(measure_list) - 1)
        define_measure_list.update(generate)
        if len(define_measure_list) > len_measure_list:
            i = i + 1

    # ПОСЛЕ ТОГО КАК ИМЕЕТ СЕТ ИЗ УНИКАЛЫХ ЗНАЧЕНИЙ ЧТО СОПОСТАВЛЯЮТСЯ АЙДИЩНИКАМИ - ПРЕОЬРАЗУЕМ

    define_measure_list = list(define_measure_list)

    # НАШ КОНЕЧНЫЙ МАССИВ
    measure = []
    for i in define_measure_list:
        measure.append(measure_list[i])

    return measure