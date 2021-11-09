# Итак - Здесь расположим наши генераторы данных

# //--------------------------------------------------------------------------------------------------------------
# //                                 Изначальный класс , который содержит общие методы
# //--------------------------------------------------------------------------------------------------------------
class GeneratorDataConfig:
    """
    Класс родитель содержащий генерацию Таблицы счетчика и Конфиг

    """
    MeterId = 0
    Serial = 0
    # -->
    Redefine_tag = {}
    MeterTable = None
    ElConfig = None

    # Генерируем MeterTable
    def _Generate_MeterTable(self):
        """
        Генерируем MeterTable
        """
        from GenerateMeterData import MeterTable

        # Переопределяем тэги для RTU

        redefine_tag = {
            "Address": 'ТЕСТ RTU327',
            # ТИП ОБЬЕКТА INTEGER
            'RTUObjType': 1,
            # НОМЕР ФИДЕРАINTEGER
            'RTUFeederNum': 1,
            # НОМЕР ОБЬЕКТА    INTEGER
            'RTUObjNum': 1,
        }

        # Теперь соеденяем это с тэгами что спустили

        redefine_tag.update(self.Redefine_tag)

        MeterTable_record = MeterTable(redefine_tag=redefine_tag)

        return MeterTable_record

    # Генерируем Конфиг
    def _generate_ElConfig(self):
        """
        Здесь генерируем конфиг
        Необходимо :
        MeterTable
        Опционально - Переопределенные тэги
        """
        from GenerateMeterData import ElConfig

        redefine_tag = {

        }

        redefine_tag.update(self.Redefine_tag)

        ElConfig_record = ElConfig(MeterTable=self.MeterTable, Config_tag=redefine_tag)

        return ElConfig_record


# //--------------------------------------------------------------------------------------------------------------
# //                                 GETSHPRM
# //--------------------------------------------------------------------------------------------------------------
class GeneratorGETSHPRM(GeneratorDataConfig):
    """Класс Генерации данных для запроса GETSHPRM """

    MeterId = 0
    Serial = 0
    GETSHPRM = {}

    # -->
    Redefine_tag = {}
    MeterTable = None
    ElConfig = None
    ElArr1ConsPower = None

    def __init__(self, Redefine_tag=None):
        """
        Здесь Генерируем наши данные для RTU в виден что он кушает

        :param: Redefine_tag - Тэги дял переопределения значений

        """

        if Redefine_tag is None:
            Redefine_tag = {}
        self.MeterId = 0
        self.Serial = 0

        self.GETSHPRM = {}

        # Итак - Теперь переопределяем данные

        self.Redefine_tag = Redefine_tag
        # --->
        self.MeterTable = None
        self.ElConfig = None
        self.ElArr1ConsPower = None

        # Сначала генерируем данные
        self._generate_data_for_GETSHPRM()
        # Потом формируем их если данные пустые

        self.GETSHPRM = self._form_data_to_GETSHPRM()

    def _generate_ElArr1ConsPower(self):
        # Генерируем ОДИН профиль мощности

        from GenerateMeterData import ElArr1ConsPower

        # Определяем период интеграции - Пол часа
        redefine_tag = {
            'cTime': 30
        }

        redefine_tag.update(self.Redefine_tag)

        ElArr1ConsPower_record = ElArr1ConsPower(
            Redefine_tag=redefine_tag,
            Count_timestamp=1,
            MeterTable=self.MeterTable,
            ElConfig=self.ElConfig
        )

        return ElArr1ConsPower_record

    def _generate_data_for_GETSHPRM(self):
        """
        Здесь генерируем наши данные для нашей команды
        """

        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # и Генерируем ОДИН профиль мощности для выяснения периода интеграции
        RecordData = self._generate_ElArr1ConsPower()

        # print(RecordData)

        # Вытаскиваем Профиль мощности
        ElArr1ConsPower = RecordData.get('ElArr1ConsPower')
        self.ElArr1ConsPower = ElArr1ConsPower.get(list(ElArr1ConsPower.keys()).pop())
        # print(ElArr1ConsPower)

    def _form_data_to_GETSHPRM(self):
        """
        Основная функция формирования нужных данных

        """

        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = self.MeterTable.get('MeterId')
        self.Serial = self.ElConfig.get('Serial')
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа

        from Service.Service_function import MeterId_from_USPD_to_RTU

        GETSHPRM = \
            {
                # Vers Версия параметров ( текущее значение 1) INT16
                'Vers': 1,
                # Typ_Sh Тип счетчика INT8
                'Typ_Sh': MeterId_from_USPD_to_RTU(self.MeterTable.get('TypeId')),
                # Kt Коэффициент трансформации по току FLOAT8
                'Kt': self.ElConfig.get('CurrentCoeff'),
                # Kn Коэффициент трансформации по напряжению FLOAT8
                'Kn': self.ElConfig.get('VoltageCoeff'),
                # M Множитель FLOAT8
                'M': self.ElConfig.get('MeterConst'),
                # Interv Интервал профиля нагрузки INT8

                # 'Interv': self.ElConfig.get('IntervalPowerArrays'),
                'Interv': self.ElArr1ConsPower.get('cTime'),

                # Syb_Rnk Тип объекта INT32
                'Syb_Rnk': self.MeterTable.get('RTUObjType'),
                # N_Ob Номер объекта INT32
                'N_Ob': self.MeterTable.get('RTUObjNum'),
                # N_Fid Номер фидера INT32
                'N_Fid': self.MeterTable.get('RTUFeederNum'),
            }

        return GETSHPRM


# //--------------------------------------------------------------------------------------------------------------
# //                                 GETPOK
# //--------------------------------------------------------------------------------------------------------------

class GenerateGETPOK(GeneratorDataConfig):
    """Класс Генерации данных для запроса GETPOK """

    RecordTypeId = ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
    Count_timestamp = 1
    Redefine_tag = {}
    MeterId = 0
    Serial = 0
    Timestamp = 0
    GETPOK = {}

    # --->
    MeterTable = None
    ElConfig = None
    ElectricEnergyValues = None

    def __init__(self,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 RecordTypeId: list = ['ElMomentEnergy']
                 ):
        """
        Генерация
        """
        # Тип данных
        self.RecordTypeId = RecordTypeId
        # Внешний айдишник - Не определен
        self.MeterId = 0
        # Серийник
        self.Serial = 0
        # Сами данные
        self.GETPOK = {}
        self.MeterTable = None
        self.ElConfig = None
        self.ElectricEnergyValues = None

        # Итак - Теперь переопределяем данные
        self.Count_timestamp = Count_timestamp
        self.Redefine_tag = Redefine_tag

        # Генерируем
        self._generate_data_for_GETPOK()
        self.GETPOK = self._form_data_to_GETPOK()

    def _ElectricEnergyValues(self):
        """
        Здесь генерируем наш тип данных

        """

        RecordData = {}
        # Первое - По каждому из типов проходим

        for measure in self.RecordTypeId:

            if measure == 'ElMomentEnergy':
                # Генерируем Моментные показания энергии
                from GenerateMeterData import ElMomentEnergy

                ElMomentEnergy_record = ElMomentEnergy(
                    Redefine_tag=self.Redefine_tag,
                    Count_timestamp=self.Count_timestamp,
                    MeterTable=self.MeterTable,
                    ElConfig=self.ElConfig
                )

                # А теперь все что есть добавляем
                RecordData.update(ElMomentEnergy_record.get('ElMomentEnergy'))

            elif measure == 'ElDayEnergy':
                # Генерируем показания энергии на начало дня
                from GenerateMeterData import ElDayEnergy

                ElDayEnergy_record = ElDayEnergy(
                    Redefine_tag=self.Redefine_tag,
                    Count_timestamp=self.Count_timestamp,
                    MeterTable=self.MeterTable,
                    ElConfig=self.ElConfig
                )
                # А теперь все что есть добавляем
                RecordData.update(ElDayEnergy_record.get('ElDayEnergy'))

            elif measure == 'ElMonthEnergy':
                # Генерируем показания энергии на начало месяца
                from GenerateMeterData import ElMonthEnergy

                ElMonthEnergy_record = ElMonthEnergy(
                    Redefine_tag=self.Redefine_tag,
                    Count_timestamp=self.Count_timestamp,
                    MeterTable=self.MeterTable,
                    ElConfig=self.ElConfig
                )

                # А теперь все что есть добавляем
                RecordData.update(ElMonthEnergy_record.get('ElMonthEnergy'))

        return RecordData

    def _generate_data_for_GETPOK(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # сначала записываем все нужные данные в БД
        self.ElectricEnergyValues = self._ElectricEnergyValues()

    def _form_data_to_GETPOK(self):

        """
        Основная функция формирования нужных данных

        """

        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = self.MeterTable.get('MeterId')
        self.Serial = self.ElConfig.get('Serial')
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа

        # print('----->', RecordData)
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETPOK = {}
        for key in self.ElectricEnergyValues:
            GETPOK_element_dict = {
                'Id': self.ElectricEnergyValues[key].get('Id'),
                'Ap': self.ElectricEnergyValues[key].get('A+0'),
                'Am': self.ElectricEnergyValues[key].get('A-0'),
                'Rp': self.ElectricEnergyValues[key].get('R+0'),
                'Rm': self.ElectricEnergyValues[key].get('R-0'),
                'DeviceIdx': self.ElectricEnergyValues[key].get('DeviceIdx'),
                'Timestamp': self.ElectricEnergyValues[key].get('Timestamp')
            }

            # Ставим индефикаторы по таймштампам
            GETPOK[self.ElectricEnergyValues[key].get('Timestamp')] = GETPOK_element_dict

        return GETPOK


# //--------------------------------------------------------------------------------------------------------------
# //                Запрос на передачу профиля расходов коммерческого интервала - ПРОФИЛЬ МОЩНОСТИ
# //--------------------------------------------------------------------------------------------------------------

class GenerateGETLP(GeneratorDataConfig):
    """Класс Генерации данных для запроса GETLP """

    RecordTypeId = ['ElArr1ConsPower']
    GETLP = {}

    Count_timestamp = 1
    MeterId = 0
    Serial = 0

    cTime = 30

    # -->
    Redefine_tag = {}
    MeterTable = None
    ElConfig = None
    ElArr1ConsPower = None

    def __init__(self,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 cTime: int = 30
                 ):
        self.MeterId = 0
        self.Serial = 0
        self.GETLP = {}

        # Итак - Теперь переопределяем данные
        self.cTime = cTime
        self.Count_timestamp = Count_timestamp

        self.Redefine_tag = Redefine_tag

        self._generate_data_for_GETLP()

        self.GETLP = self._form_data_to_GETLP()

    # Профиль мощности
    def _generate_ElArr1ConsPower(self):
        # Генерируем ОДИН профиль мощности

        from GenerateMeterData import ElArr1ConsPower

        # Определяем период интеграции - Пол часа
        redefine_tag = {
            'cTime': 30
        }

        redefine_tag.update(self.Redefine_tag)

        ElArr1ConsPower_record = ElArr1ConsPower(
            Redefine_tag=redefine_tag,
            Count_timestamp=self.Count_timestamp,
            MeterTable=self.MeterTable,
            ElConfig=self.ElConfig,

        )

        return ElArr1ConsPower_record

    def _generate_ElectricPowerValues(self):
        """
        Метод для генерации Энергии чо так , да вот так
        """

        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # и Генерируем ОДИН профиль мощности для выяснения периода интеграции
        RecordData = self._generate_ElArr1ConsPower()

        # print(RecordData)

        # Вытаскиваем Профиль мощности
        ElArr1ConsPower = RecordData.get('ElArr1ConsPower')
        self.ElArr1ConsPower = ElArr1ConsPower.get(list(ElArr1ConsPower.keys()).pop())

    def _generate_data_for_GETLP(self):
        """
        Здесь генерируем наши данные для нашей команды
        """

        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # и Генерируем ОДИН профиль мощности для выяснения периода интеграции
        RecordData = self._generate_ElArr1ConsPower()

        # print(RecordData)

        # Вытаскиваем Профиль мощности
        # ElArr1ConsPower = RecordData.get('ElArr1ConsPower')
        self.ElArr1ConsPower = RecordData.get('ElArr1ConsPower')
        # self.ElArr1ConsPower = ElArr1ConsPower.get(list(ElArr1ConsPower.keys()).pop())

    def _form_data_to_GETLP(self):
        """
        Основная функция формирования нужных данных

        """
        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = self.MeterTable.get('MeterId')
        self.Serial = self.ElConfig.get('Serial')
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа

        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETLP = {}

        for key in self.ElArr1ConsPower:
            GETLP_element_dict = {
                'Id': self.ElArr1ConsPower[key].get('Id'),
                'cTime': self.ElArr1ConsPower[key].get('cTime'),
                'Pp': self.ElArr1ConsPower[key].get('P+'),
                'Pm': self.ElArr1ConsPower[key].get('P-'),
                'Qp': self.ElArr1ConsPower[key].get('Q+'),
                'Qm': self.ElArr1ConsPower[key].get('Q-'),
                'isPart': self.ElArr1ConsPower[key].get('isPart'),
                'isOvfl': self.ElArr1ConsPower[key].get('isOvfl'),
                'isSummer': self.ElArr1ConsPower[key].get('isSummer'),
                'DeviceIdx': self.ElArr1ConsPower[key].get('DeviceIdx'),
                'Timestamp': self.ElArr1ConsPower[key].get('Timestamp')
            }

            GETLP[self.ElArr1ConsPower[key].get('Timestamp')] = GETLP_element_dict

        return GETLP


# //--------------------------------------------------------------------------------------------------------------
# //                      Генерация для команды - GETTESTS - Запрос замеров параметров электросети.
# //--------------------------------------------------------------------------------------------------------------


class GenerateGETTESTS(GeneratorDataConfig):
    """Класс Генерации данных для запроса GETTESTS """

    RecordTypeId = ['ElMomentQuality']

    Count_timestamp = 1
    MeterId = 0
    Serial = 0

    GETTESTS = {}

    # -->
    Redefine_tag = {}
    MeterTable = None
    ElConfig = None
    ElMomentQuality = None

    def __init__(
            self,
            Redefine_tag: dict = {},
            Count_timestamp: int = 1
    ):
        self.MeterId = 0
        self.Serial = 0
        self.GETTESTS = {}

        # Итак - Теперь переопределяем данные

        self.Count_timestamp = Count_timestamp
        self.Redefine_tag = Redefine_tag

        self._generate_data_for_GETTESTS()

        self.GETTESTS = self._form_data_to_GETTESTS()

    # Профиль мощности
    def _generate_ElMomentQuality(self):
        # Генерируем ОДИН профиль мощности

        from GenerateMeterData import ElMomentQuality

        # Определяем период интеграции - Пол часа
        redefine_tag = {

        }

        redefine_tag.update(self.Redefine_tag)

        ElMomentQuality_record = ElMomentQuality(
            Redefine_tag=redefine_tag,
            Count_timestamp=self.Count_timestamp,
            MeterTable=self.MeterTable,
            ElConfig=self.ElConfig,

        )

        return ElMomentQuality_record

    def _generate_data_for_GETTESTS(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # сначала записываем все нужные данные в БД
        ElMomentQuality = self._generate_ElMomentQuality()
        self.ElMomentQuality = ElMomentQuality.get('ElMomentQuality')

    def _form_data_to_GETTESTS(self):
        """
        Основная функция формирования нужных данных

        """

        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = self.MeterTable.get('MeterId')
        self.Serial = self.ElConfig.get('Serial')

        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETTESTS = {}

        for key in self.ElMomentQuality:
            GETTESTS_element_dict = {
                'Id': self.ElMomentQuality[key].get('Id'),
                'Wa': self.ElMomentQuality[key].get('PA'),
                'Wb': self.ElMomentQuality[key].get('PB'),
                'Wc': self.ElMomentQuality[key].get('PC'),
                'VAa': self.ElMomentQuality[key].get('SA'),
                'VAb': self.ElMomentQuality[key].get('SB'),
                'VAc': self.ElMomentQuality[key].get('SC'),
                'FREQ': self.ElMomentQuality[key].get('Freq'),
                'Ia': self.ElMomentQuality[key].get('IA'),
                'Ib': self.ElMomentQuality[key].get('IB'),
                'Ic': self.ElMomentQuality[key].get('IC'),
                'Ua': self.ElMomentQuality[key].get('UA'),
                'Ub': self.ElMomentQuality[key].get('UB'),
                'Uc': self.ElMomentQuality[key].get('UC'),
                'PFangA': self.ElMomentQuality[key].get('LOL'),
                'PFangB': self.ElMomentQuality[key].get('LOL'),
                'PFangC': self.ElMomentQuality[key].get('LOL'),
                'PHangB': self.ElMomentQuality[key].get('AngAB'),
                'PhangC': self.ElMomentQuality[key].get('AngAC'),
                'Timestamp': self.ElMomentQuality[key].get('Timestamp')
            }

            GETTESTS[self.ElMomentQuality[key].get('Timestamp')] = GETTESTS_element_dict

        return GETTESTS


# //--------------------------------------------------------------------------------------------------------------
# //                      Генерация для команды - GETMTRLOG - Запрос журнала событий по счетчикам
# //--------------------------------------------------------------------------------------------------------------
class GenerateGETMTRLOG(GeneratorDataConfig):
    """Класс Генерации данных для запроса GETMTRLOG """

    RecordTypeId = ["ElJrnlPwr", "ElJrnlTimeCorr", "ElJrnlReset", "ElJrnlOpen", "ElJrnlPwrA", "ElJrnlPwrB",
                    "ElJrnlPwrC"]

    Count_timestamp = 1
    MeterId = 0
    Serial = 0

    GETMTRLOG = {}

    # -->
    Redefine_tag = {}
    MeterTable = None
    ElConfig = None
    JournalValues = None

    def __init__(self,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 RecordTypeId: list = ["ElJrnlPwr", "ElJrnlTimeCorr",
                                       "ElJrnlReset", "ElJrnlOpen", "ElJrnlPwrA",
                                       "ElJrnlPwrB", "ElJrnlPwrC"]
                 ):

        self.MeterId = 0
        self.Serial = 0
        self.GETMTRLOG = {}

        # Итак - Теперь переопределяем данные

        self.Count_timestamp = Count_timestamp
        self.Redefine_tag = Redefine_tag
        self.RecordTypeId = RecordTypeId

        self._generate_data_for_GETMTRLOG()

        self.GETMTRLOG = self._form_data_to_GETMTRLOG()

    # Генерируем журнал
    def _generate_JournalValues(self, RecordTypeId):
        # Генерируем ОДИН профиль мощности

        from GenerateMeterData import Journal

        # Определяем период интеграции - Пол часа
        redefine_tag = {

        }

        redefine_tag.update(self.Redefine_tag)

        Journal_record = Journal(
            Redefine_tag=redefine_tag,
            Count_timestamp=self.Count_timestamp,
            MeterTable=self.MeterTable,
            ElConfig=self.ElConfig,
            RecordTypeId=RecordTypeId
        )

        return Journal_record

    def _generate_data_for_GETMTRLOG(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # сначала записываем все нужные данные в БД
        JournalValues_dict = {}
        for i in range(len(self.RecordTypeId)):

            JournalValues = self._generate_JournalValues(RecordTypeId=self.RecordTypeId[i])

            JournalValues_dict[self.RecordTypeId[i]] = JournalValues.get(self.RecordTypeId[i])

        self.JournalValues = JournalValues_dict

    def _form_data_to_GETMTRLOG(self):

        """
        Основная функция формирования нужных данных

        """

        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = self.MeterTable.get('MeterId')
        self.Serial = self.ElConfig.get('Serial')

        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETMTRLOG = {}
        for measure in self.JournalValues:
            RecordData_measure = {}
            for Idx in self.JournalValues[measure]:
                RecordData_Idx_element_dict = {
                    'RecordTypeId': self.JournalValues[measure][Idx].get('RecordTypeId'),
                    'Id': self.JournalValues[measure][Idx].get('Id'),
                    'evTime': self.JournalValues[measure][Idx].get('Timestamp'),
                    'evType': self.JournalValues[measure][Idx].get('EventId'),
                    'Event': self.JournalValues[measure][Idx].get('Event'),
                    'DeviceIdx': self.JournalValues[measure][Idx].get('DeviceIdx'),
                    'Timestamp': self.JournalValues[measure][Idx].get('Timestamp')
                }
                RecordTypeId = self.JournalValues[measure][Idx].get('RecordTypeId')
                # RecordData_measure[Idx] = RecordData_Idx_element_dict
                RecordData_measure[self.JournalValues[measure][Idx].get('Timestamp')] = RecordData_Idx_element_dict

            # GETMTRLOG[RecordData[measure].get('Id')] = RecordData_Idx_element_dict
            # GETMTRLOG[measure] = RecordData_measure
            GETMTRLOG[RecordTypeId] = RecordData_measure

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

# //--------------------------------------------------------------------------------------------------------------
# //                Класс Генерации данных для запроса GETAUTOREAD
# //--------------------------------------------------------------------------------------------------------------


class GenerateGETAUTOREAD(GeneratorDataConfig):
    """Класс Генерации данных для запроса GETAUTOREAD """

    RecordTypeId = ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']

    Count_timestamp = 1
    MeterId = 0
    Serial = 0

    GETAUTOREAD = {}

    # -->
    Redefine_tag = {}
    MeterTable = None
    ElConfig = None
    ElectricEnergyValues = None

    def __init__(self,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 RecordTypeId: list = ['ElMomentEnergy']):

        self.MeterId = 0
        self.Serial = 0
        self.GETAUTOREAD = {}

        # Итак - Теперь переопределяем данные

        self.Count_timestamp = Count_timestamp
        self.Redefine_tag = Redefine_tag
        self.RecordTypeId = RecordTypeId

        self._generate_data_for_GETAUTOREAD()

        self.GETAUTOREAD = self._form_data_to_GETAUTOREAD()

    # Генерируем журнал
    def _generate_ElectricEnergyValues(self, RecordTypeId):

        RecordData = {}
        if RecordTypeId == 'ElMomentEnergy':
            # Генерируем Моментные показания энергии
            from GenerateMeterData import ElMomentEnergy

            ElMomentEnergy_record = ElMomentEnergy(
                Redefine_tag=self.Redefine_tag,
                Count_timestamp=self.Count_timestamp,
                MeterTable=self.MeterTable,
                ElConfig=self.ElConfig
            )

            # А теперь все что есть добавляем
            RecordData['ElMomentEnergy'] = ElMomentEnergy_record.get('ElMomentEnergy')

        elif RecordTypeId == 'ElDayEnergy':
            # Генерируем показания энергии на начало дня
            from GenerateMeterData import ElDayEnergy

            ElDayEnergy_record = ElDayEnergy(
                Redefine_tag=self.Redefine_tag,
                Count_timestamp=self.Count_timestamp,
                MeterTable=self.MeterTable,
                ElConfig=self.ElConfig
            )
            # А теперь все что есть добавляем
            RecordData['ElDayEnergy'] = ElDayEnergy_record.get('ElDayEnergy')

        elif RecordTypeId == 'ElMonthEnergy':
            # Генерируем показания энергии на начало месяца
            from GenerateMeterData import ElMonthEnergy

            ElMonthEnergy_record = ElMonthEnergy(
                Redefine_tag=self.Redefine_tag,
                Count_timestamp=self.Count_timestamp,
                MeterTable=self.MeterTable,
                ElConfig=self.ElConfig
            )

            # А теперь все что есть добавляем
            RecordData['ElMonthEnergy'] = ElMonthEnergy_record.get('ElMonthEnergy')

        return RecordData

    def _generate_data_for_GETAUTOREAD(self):
        """
        Здесь генерируем наши данные для нашей команды
        """
        # Генерируем MeterTable
        MeterTable = self._Generate_MeterTable()

        # print(MeterTable)
        self.MeterTable = MeterTable.get('MeterTable')
        # Генерируем Конфиг

        ElConfig = self._generate_ElConfig()
        # print(ElConfig)
        self.ElConfig = ElConfig.get('ElConfig')

        # сначала записываем все нужные данные в БД
        ElectricEnergyValues_dict = {}
        for i in range(len(self.RecordTypeId)):

            ElectricEnergyValues = self._generate_ElectricEnergyValues(RecordTypeId=self.RecordTypeId[i])

            ElectricEnergyValues_dict[self.RecordTypeId[i]] = ElectricEnergyValues.get(self.RecordTypeId[i])

        self.ElectricEnergyValues = ElectricEnergyValues_dict

    def _form_data_to_GETAUTOREAD(self):

        """
        Основная функция формирования нужных данных

        """

        # ПУНКТ ПЕРВЫЙ - ВЫТАСКИВАЕМ в переменную айдишник и серийник нашего счетчика
        self.MeterId = self.MeterTable.get('MeterId')
        self.Serial = self.ElConfig.get('Serial')

        # ПУНКТ ВТОРОЙ - формируем данные для команды ответа
        GETAUTOREAD = {}

        for measure in self.ElectricEnergyValues:
            RecordData_measure = {}

            for Idx in self.ElectricEnergyValues[measure]:
                RecordData_Idx_element_dict = {

                    'Id': self.ElectricEnergyValues[measure][Idx].get('Id'),

                    'A+1': self.ElectricEnergyValues[measure][Idx].get('A+1'),
                    'A-1': self.ElectricEnergyValues[measure][Idx].get('A-1'),
                    'R+1': self.ElectricEnergyValues[measure][Idx].get('R+1'),
                    'R-1': self.ElectricEnergyValues[measure][Idx].get('R-1'),

                    'A+2': self.ElectricEnergyValues[measure][Idx].get('A+2'),
                    'A-2': self.ElectricEnergyValues[measure][Idx].get('A-2'),
                    'R+2': self.ElectricEnergyValues[measure][Idx].get('R+2'),
                    'R-2': self.ElectricEnergyValues[measure][Idx].get('R-2'),

                    'A+3': self.ElectricEnergyValues[measure][Idx].get('A+3'),
                    'A-3': self.ElectricEnergyValues[measure][Idx].get('A-3'),
                    'R+3': self.ElectricEnergyValues[measure][Idx].get('R+3'),
                    'R-3': self.ElectricEnergyValues[measure][Idx].get('R-3'),

                    'A+4': self.ElectricEnergyValues[measure][Idx].get('A+4'),
                    'A-4': self.ElectricEnergyValues[measure][Idx].get('A-4'),
                    'R+4': self.ElectricEnergyValues[measure][Idx].get('R+4'),
                    'R-4': self.ElectricEnergyValues[measure][Idx].get('R-4'),
                    'RecordTypeId': self.ElectricEnergyValues[measure][Idx].get('RecordTypeId'),
                    'DeviceIdx': self.ElectricEnergyValues[measure][Idx].get('DeviceIdx'),
                    'Timestamp': self.ElectricEnergyValues[measure][Idx].get('Timestamp')
                }
                RecordTypeId = self.ElectricEnergyValues[measure][Idx].get('RecordTypeId')
                # RecordData_measure[Idx] = RecordData_Idx_element_dict
                RecordData_measure[self.ElectricEnergyValues[measure][Idx].get('Timestamp')] = RecordData_Idx_element_dict

                GETAUTOREAD[self.ElectricEnergyValues[measure][Idx].get('Timestamp')] = RecordData_Idx_element_dict
            # GETMTRLOG[RecordData[measure].get('Id')] = RecordData_Idx_element_dict
            # GETMTRLOG[measure] = RecordData_measure
            # GETAUTOREAD[measure] = RecordData_measure

        return GETAUTOREAD


# print(GenerateGETAUTOREAD().GETAUTOREAD)
#
# print(GeneratorGETSHPRM(Redefine_tag={'Valid':0}).GETSHPRM)
# print(GenerateGETMTRLOG().GETMTRLOG)
# print(GenerateGETPOK().GETPOK)
# print(GenerateGETTESTS().GETTESTS)