# Здесь находится селект в таблицу Журналов
from GenerateMeterData.Generate.Generate_MeterData import GeneratorWithMeterData


class GeneratorJournalValues(GeneratorWithMeterData):
    """
    Класс для генерации данных в для таблицы ElectricPowerValues

    """

    MeterData = {}
    JournalValues = {}
    DeviceIdx = 0
    RecordTypeId = ''
    Redefine_tag = {}
    MeterData_tag = {}
    Count_timestamp = 1

    def __init__(self,
                 RecordTypeId: str,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 MeterTable=None,
                 ElConfig=None):

        # Чтоб в будущем не выстрелить себе в ногу - Сначала ставим константы
        self.count = 1
        self.DeviceIdx = 0
        self.RecordTypeId = ''
        self.MeterData_tag = {}

        # Получаем запись MeterTable
        if MeterTable is None:
            self.MeterTable = self._generation_MeterTable()
        else:
            self.MeterTable = MeterTable

        if ElConfig is None:
            self.Config = self._generation_ElConfig()
        else:
            self.Config = ElConfig

        self.DeviceIdx = self.Config.get('DeviceIdx')

        self.RecordTypeId = RecordTypeId
        self.Count_timestamp = Count_timestamp
        # С Переопределяемымыми тэгами - сложнее - отделяем мух от котлет и meter data тэги от остальных
        self.Redefine_tag = self._find_redefine_tag(Redefine_tag)
        # Генерируем MeterData
        self.MeterData = self._generate_MeterData()
        # Разделяем переопределение тэгов

        # ТЕПЕРЬ ЧТО ДЕЛАЕМ - ГЕНЕРИРУЕМ НАШИ ОСНОВНЫЕ ДАННЫЕ
        self.JournalValues = self._Generate_JournalValues()
        # Теперь все записываем
        self._record_JournalValues()

    def _Generate_JournalValues(self):
        """
        Генерация Профиля мощности
        """

        from copy import deepcopy

        MeterData = deepcopy(self.MeterData)

        eventId = 0
        for ids in MeterData:
            if MeterData[ids].get('Valid') > 0:
                # генерируем сначала в формате JSON
                JournalValues_format_JSON = self._generate_JournalValues_one_record(eventId)

                MeterData[ids].update(JournalValues_format_JSON)
                eventId = eventId + 1
        return MeterData

    def _generate_MeterData(self):
        """
        Здесь Генерируем Данные для Meter Data
        """
        from GenerateMeterData.Generate.Generate_MeterData import GeneratorMeterData
        MeterData = GeneratorMeterData(DeviceIdx=self.DeviceIdx,
                                       RecordTypeId_Name=self.RecordTypeId,
                                       MeterData_tag=self.MeterData_tag,
                                       Count_timestamp=self.Count_timestamp).MeterData

        return MeterData

    def _generate_JournalValues_one_record(self, eventId):
        """Здесь генерируем ОДНУ ПОЛНУЮ ЗАПИСЬ"""
        import random
        # Здесь - По self.RecordTypeId Определяем Event Id , а после - сам Event - ЦЕ ВАЖНА
        # генерируем сначала в формате JSON
        from GenerateMeterData.Generate.Service_Generate_Constant import measure_Journal_list
        # сначала проверяем входит ли наш журнал в учтеные журналы

        assert self.RecordTypeId in measure_Journal_list, '\nНЕПРАВИЛЬНОЕ ИМЯ ЖУРНАЛА ' + '\nЗАДАН ' + str(self.RecordTypeId)

        JournalValues_format_JSON = \
            {
                # 'Event': random.randint(0, 1),
                # 'EventId': JournalValues_list[self.RecordTypeId],
                'EventId': eventId,
            }

        if self.RecordTypeId in ['ElJrnlLimUAMax', 'ElJrnlLimUAMin', 'ElJrnlLimUBMax', 'ElJrnlLimUBMin',
                                'ElJrnlLimUCMax', 'ElJrnlLimUCMin',
                                 ]:
            # Если у нас действительно этот тип значений , тогда что делаем - мы ставим либо 1 либо 0
            JournalValues_format_JSON['Event'] = 1

        elif self.RecordTypeId in ['ElJrnlUnAyth', "ElJrnlTrfCorr", 'ElJrnlReset','ElJrnlOpen']:
            JournalValues_format_JSON['Event'] = 0

        else:
            JournalValues_format_JSON['Event'] = random.randint(0, 1)
        # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
        JournalValues_format_JSON = self._redefine_tag(JournalValues_format_JSON)

        return JournalValues_format_JSON

    def _record_value_queue(self, JournalValues_format_JSON):
        """

        Здесь записываем сформированный пакет значений в формате JSON

        :param JournalValues_format_JSON:
        :return:
        """


        # Переводим в значения равные БД
        # Перебираем все значения что сгенерированли
        JournalValues_list = []

        for ids in JournalValues_format_JSON:
            if JournalValues_format_JSON[ids].get('Valid') > 0:
                JournalValues = \
                {
                    'Id': JournalValues_format_JSON[ids].get('Id'),
                    'Event': JournalValues_format_JSON[ids].get('Event'),
                    'EventId': JournalValues_format_JSON[ids].get('EventId')
                }

                # А теперь берем добавляем это все в наш список
                JournalValues_list.append(JournalValues)

        # начинаем формировать команду
        if len(JournalValues_list) > 0:
            columns_list = [
                'Id',
                'Event',
                'EventId'
                            ]

            columns = ''
            values = ''

            # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

            for i in range(len(columns_list)):
                columns = columns + columns_list[i] + ' , '

            # ТЕПЕРЬ ФОРМИРУЕМ ВСЕ ЗНАЧЕНИЯ
            for i in range(len(JournalValues_list)):
                values_element = ''
                for x in range(len(columns_list)):
                    # если это стринг - то экранируем его
                    if type(JournalValues_list[i].get(columns_list[x])) == str:
                        JournalValues_list[i][columns_list[x]] = '\"' + JournalValues_list[i].get(
                            columns_list[x]) + '\"'
                    # Если это None То Null
                    elif JournalValues_list[i].get(columns_list[x]) is None:
                        JournalValues_list[i][columns_list[x]] = 'Null'

                    values_element = values_element + str(JournalValues_list[i].get(columns_list[x])) + ' , '
                # Обрезаем последнюю запятую
                values_element = values_element[:-2]
                values = values + ' ( ' + values_element + ' ) , '

            # Обрезаем последнюю запятую
            columns = columns[:-2]
            values = values[:-2]

            command = 'INSERT INTO JournalValues ( ' + columns + ') VALUES  ' + values + ' ;'
            # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
            from GenerateMeterData.Service.Work_With_Database import SQL

            result = SQL(command=command)


    def _record_JournalValues(self):
        """
        Это метод записи значений в БД
        """
        from copy import deepcopy

        # Итак что делаем - Сделаем цикл

        JournalValues = deepcopy(self.JournalValues)

        # Итак что делаем - Сделаем цикл

        # Переводим в значения равные БД
        # Берем наши значения
        JournalValues_format_JSON = {}

        for key in JournalValues:
            # Набираем списоак
            JournalValues_format_JSON[key] = JournalValues[key]
            # Теперь берем по 150 штук
            if len(JournalValues_format_JSON) > 150:
                self._record_value_queue(JournalValues_format_JSON=JournalValues_format_JSON)
                JournalValues_format_JSON = {}
        if len(JournalValues_format_JSON) > 0:
            self._record_value_queue(JournalValues_format_JSON=JournalValues_format_JSON)