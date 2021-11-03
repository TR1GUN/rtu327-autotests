# Здесь расположим класс генерации для MeterData

# //------------------------------------------------------------------------------------------------------------------
# //                                        Генерация Самой записи MeterData
# //------------------------------------------------------------------------------------------------------------------

class GeneratorMeterData:
    """

    Здесь расположим класс генерации данных для MeterData

    """

    RecordTypeId = 0
    DeviceIdx = 0
    RecordTypeId_Name = ''
    MeterData = {}
    MeterData_tag = {}
    Timestamp = []
    cTime = 30

    def __init__(self,
                 DeviceIdx: int,
                 RecordTypeId_Name: str,
                 MeterData_tag: dict = {},
                 Count_timestamp: int = 1,
                 cTime: int = 30
                 ):

        self.MeterData = {}
        self.Timestamp = []
        # Первое что делаем - узнает тип данных
        self.cTime = cTime
        self.RecordTypeId_Name = RecordTypeId_Name
        self.DeviceIdx = DeviceIdx
        self.MeterData_tag = MeterData_tag

        # ТЕПЕРЬ ОПРЕДЕЛЯЕМСЯ С ТАЙМШТАМПАМИ
        # Если у нас ЧИСЛО таймштампов - то генерируем
        if type(Count_timestamp) == int:
            from GenerateMeterData.Generate.Generate_Time import GenerateTimestamp

            self.Timestamp = GenerateTimestamp(measure=RecordTypeId_Name, Count_timestamp=Count_timestamp,
                                               cTime=self.cTime).Timestamp_list
        # Если у нас список таймштампов - то просто переопределяем
        elif type(Count_timestamp) == list:
            self.Timestamp = Count_timestamp

        # ИНАЧЕ - ГЕНЕРИУРЕМ ОДИН ТАЙМШТАМП
        else:
            from GenerateMeterData.Generate.Generate_Time import GenerateTimestamp
            self.Timestamp = GenerateTimestamp(measure=RecordTypeId_Name,
                                               Count_timestamp=1).Timestamp_list

        self.RecordTypeId = self._define_RecordTypeId()
        # ТЕПЕРЬ НАЧИНАЕМ ГЕНЕРИРОВАТЬ ЗАПИСИ ДЛЯ НАШЕЙ ЗАПИСИ

        self._generate_and_record_MeterData()
        # self.MeterData = self._Generate_MeterData_dict()
        # # Теперь это записываем
        # self.MeterData['id'] = self._Record_value_to_Table()

    def _define_RecordTypeId(self):
        """
        Этот метод нужен для определения типа записи RecordTypeId через таблицу
        """
        from GenerateMeterData.Service.Work_With_Database import SQL

        Command = 'SELECT Id FROM ArchTypes WHERE Name in ' + '( \"' + self.RecordTypeId_Name + '\" ) ;'

        result = SQL(Command)
        return int(result)

    # Функция Перезаписи конфига
    def _redefine_tag(self, MeterData):
        """
        ПЕРЕЗАПИСЫВАЕМ наш сгенерированный MeterData
        """
        # Сюда спускаем и перезаписываем ТЭГИ которые были заранее Определены - ЭТО ВАЖНО
        # Перебираем все возможные комбинации
        for tag_castrom_value in self.MeterData_tag:
            # ЕСЛИ ЭТОТ ТЭГ СУЩЕСТВУЕТТО ЕГО ПЕРЕЗАПСИЫВАЕМ
            if MeterData.get(tag_castrom_value) is not None:
                # Если ЕСТЬ - То его перезаписываем
                MeterData[tag_castrom_value] = self.MeterData_tag[tag_castrom_value]
        return MeterData

    def _Generate_MeterData_dict(self, Timestamp):
        """
        Здесь генерируем нашу запись
        """
        # ТЕПЕРЬ - ФОРМИРУЕМ СЛОВАРЬ ЗАПИСИ
        from copy import deepcopy
        # import random
        # from datetime import datetime
        # from time import mktime
        # unix_date_now = mktime(datetime.now().timetuple())

        MeterData = \
            {
                'DeviceIdx': deepcopy(self.DeviceIdx),
                'RecordTypeId': deepcopy(self.RecordTypeId),
                'Timestamp': Timestamp,
                'Valid': 1,
            }

        MeterData = self._redefine_tag(MeterData)
        return MeterData

    # def _Record_value_to_Table(self, MeterData):
    #
    #     """ НАША ФУНКЦИЯ ЗАПИСИ наших записей в БД """
    #
    #     from copy import deepcopy
    #     # Получаем наш список
    #
    #     MeterData = deepcopy(MeterData)
    #     # начинаем формировать команду
    #
    #     columns_list = \
    #         [
    #             'DeviceIdx',
    #             'RecordTypeId',
    #             'Timestamp',
    #             'Valid',
    #         ]
    #
    #     columns = ''
    #     values = ''
    #
    #     # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ
    #
    #     for i in range(len(columns_list)):
    #         columns = columns + columns_list[i] + ' , '
    #
    #         # если это стринг - то экранируем его
    #         if type(MeterData[columns_list[i]]) == str:
    #             MeterData[columns_list[i]] = '\"' + MeterData[columns_list[i]] + '\"'
    #
    #         values = values + str(MeterData[columns_list[i]]) + ' , '
    #
    #     # Обрезаем последнюю запятую
    #     columns = columns[:-2]
    #     values = values[:-2]
    #
    #     command = 'INSERT INTO MeterData ( ' + columns + ') VALUES  ( ' + values + ' ) ;'
    #
    #     # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
    #     from Service.Work_With_Database import SQL
    #
    #     result = SQL(command=command)
    #
    #     # Теперь после записи селектор нашу запись
    #     command_where = ''
    #     for i in range(len(columns_list)):
    #         command_where = command_where + ' ' + columns_list[i] + ' == ' + str(MeterData[columns_list[i]]) + ' AND '
    #
    #     # Теперь обрезаем
    #     command_where = command_where[:-4]
    #
    #     command = 'SELECT id FROM MeterData WHERE ' + command_where + ' ; '
    #
    #     result = SQL(command=command)
    #
    #     return int(result)
    def _Record_value_to_Table(self, MeterData):

        """ НАША ФУНКЦИЯ ЗАПИСИ наших записей в БД """

        from copy import deepcopy
        # Получаем наш список

        MeterData = deepcopy(MeterData)
        # начинаем формировать команду

        columns_list = \
            [
                'DeviceIdx',
                'RecordTypeId',
                'Timestamp',
                'Valid',
            ]

        columns = ''
        values = ''

        # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

        for i in range(len(columns_list)):
            columns = columns + columns_list[i] + ' , '

        # ТЕПЕРЬ ФОРМИРУЕМ ВСЕ ЗНАЧЕНИЯ
        for i in MeterData:
            values_element = ''
            for x in range(len(columns_list)):
                # если это стринг - то экранируем его
                if type(MeterData[i].get(columns_list[x])) == str:
                    MeterData[i][columns_list[x]] = '\"' + MeterData[i].get(
                        columns_list[x]) + '\"'

                values_element = values_element + str(MeterData[i].get(columns_list[x])) + ' , '
            # Обрезаем последнюю запятую
            values_element = values_element[:-2]
            values = values + ' ( ' + values_element + ' ) , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO MeterData ( ' + columns + ') VALUES  ' + values + ' ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from GenerateMeterData.Service.Work_With_Database import SQL

        result = SQL(command=command)


        # Теперь после записи селектор нашу запись
        command_where = ''
        columns_select_list = [
            'DeviceIdx',
            'RecordTypeId'
                              ]

        for i in range(len(columns_select_list)):
            for x in MeterData:
                command_where = command_where + ' ' + columns_select_list[i] + ' == ' + str(
                    MeterData[x][columns_select_list[i]]) + ' AND '

        # Теперь обрезаем
        command_where = command_where[:-4]

        command = 'SELECT Id ,' + columns + ' FROM MeterData WHERE ' + command_where + ' ; '

        result = SQL(command=command)


        # ТЕПЕРЬ ПОЛУЧИВШУЮСЯ КАШУ РАСКЛАДЫВАЕМ
        result = result.split('\n')
        # КАЖДЫЙ ЭЛЕМЕНТ СПИСКА СОДЕРЖИТ ровно один столбец
        result_list = []
        for i in range(len(result)):
            if len(result[i]) > 0:

                # ТЕПЕРЬ ИЗ ЭТОГО ФОРМИРУЕМ СЛОВАРЬ ЗНАЧЕНИЙ
                result_line = result[i].split('|')
                result_line_key = ['Id'] + columns_list
                result_line_dict = {}

                for x in range(len(result_line_key)):
                    result_line_dict[result_line_key[x]] = result_line[x]
                result_list.append(result_line_dict)
        return result_list

    def _generate_and_record_MeterData(self):

        """

        Это общая Функция Для записывания всей инфы что есть

        """
        from copy import deepcopy
        # ТЕПЕРЬ БЕРЕМ НАШИ ТАЙМШТАМПЫ
        Timestamp = deepcopy(self.Timestamp)
        MeterData = {}
        for i in range(len(Timestamp)):
            MeterData_element = {}
            # ТЕПЕРЬ НАЧИНАЕМ ГЕНЕРИРОВАТЬ ЗАПИСИ ДЛЯ НАШЕЙ ЗАПИСИ
            MeterData_element = self._Generate_MeterData_dict(Timestamp=Timestamp[i])
            # Теперь это записываем
            MeterData[i] = MeterData_element

        # ТЕПЕРЬ ВСЕ ЭТО ОТПРАВЛЯЕМ НА ЗАПИСЬ
        MeterData_to_record_list = self._Record_value_to_Table(MeterData=MeterData)
        # MeterData['Id'] = self._Record_value_to_Table(MeterData=MeterData)
    #         # И по айдишнику добавляем в именованный список
    #         self.MeterData[MeterData['Id']] = MeterData
    #     ТЕПЕРЬ - ВАЖНО
    #     ищим соответсвия

        # for i in MeterData:
        #     for x in range(len())
    # СЛИШКОМ ДОЛГО искать соответсия и запутано - возвращаем так есть
        MeterData = {}
        for x in range(len(MeterData_to_record_list)):
            for i in MeterData_to_record_list[x]:
                MeterData_to_record_list[x][i] = int(MeterData_to_record_list[x][i])

            MeterData[MeterData_to_record_list[x]['Id']] = MeterData_to_record_list[x]

        self.MeterData = MeterData
# //------------------------------------------------------------------------------------------------------------------
# //                                  РОДИТЕЛЬСКИЙ КЛАСС ГЕНЕРАЦИИ ВМЕСТЕ С METERDATA
# //------------------------------------------------------------------------------------------------------------------

class GeneratorWithMeterData:
    """
        Класс для генерации данных в для таблицы ElectricPowerValues

    """

    MeterData = {}
    DeviceIdx = 0
    RecordTypeId = ''
    Redefine_tag = {}
    MeterData_tag = {}
    Count_timestamp = 1

    MeterTable = {}
    Config = {}

    def _find_redefine_tag(self, Redefine_tag):
        """
        Функция для определения тэгов куда и к чему переопределять
        """
        # Формируем два списка - то что пойдет в Meterdata  нет
        MeterData_tag = \
            [
                'DeviceIdx',
                'RecordTypeId',
                'Timestamp',
                'Valid',
            ]
        self.MeterData_tag = {}

        key_to_del_list = []
        # Итак теперь проходимся по всем ключам


        for key in Redefine_tag:
            if key in MeterData_tag:
                # Добавляем ключ для переопределения тэгов MeterData
                self.MeterData_tag[key] = Redefine_tag[key]
                key_to_del_list.append(key)

        # Теперь удаляем лишнее
        for key in key_to_del_list:
            Redefine_tag.pop(key)


        return Redefine_tag
        # Функция Перезаписи конфига

    def _redefine_tag(self, Data):
        """
        ПЕРЕЗАПИСЫВАЕМ наши сгенерированные тэги
        """
        # Сюда спускаем и перезаписываем ТЭГИ которые были заранее Определены - ЭТО ВАЖНО
        # Перебираем все возможные комбинации
        for tag_castrom_value in self.Redefine_tag:
            # ЕСЛИ ЭТОТ ТЭГ СУЩЕСТВУЕТТО ЕГО ПЕРЕЗАПСИЫВАЕМ
            if Data.get(tag_castrom_value) is not None:
                # Если ЕСТЬ - То его перезаписываем
                Data[tag_castrom_value] = self.Redefine_tag[tag_castrom_value]
        return Data

    def _generate_MeterData(self):
        """
        Здесь Генерируем Данные для Meter Data
        """

        MeterData = GeneratorMeterData(DeviceIdx=self.DeviceIdx,
                                       RecordTypeId_Name=self.RecordTypeId,
                                       MeterData_tag=self.MeterData_tag,
                                       Count_timestamp=self.Count_timestamp
                                       ).MeterData

        return MeterData

    def _generation_ElConfig(self):
        """
        Итак - Здесь генерируем данные MeterTable для нашего конфига

        """

        from GenerateMeterData.Generate.Generate_Config import GeneratorElectricConfig

        # MeterTable = GeneratorMeterTable(redefine_tag=self.MeterTable_tag).Record_MeterTable
        Config = GeneratorElectricConfig(MeterTable=self.MeterTable).Config
        return Config

    def _generation_MeterTable(self):
        """
        Итак - Здесь генерируем данные MeterTable для нашего конфига

        """

        from GenerateMeterData.Generate.Generate_MeterTable import GeneratorMeterTable

        # MeterTable = GeneratorMeterTable(redefine_tag=self.MeterTable_tag).Record_MeterTable
        MeterTable = GeneratorMeterTable().Record_MeterTable
        return MeterTable