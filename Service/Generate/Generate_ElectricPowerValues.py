# Здесь находится селект в таблицу профиля мощности
from Service.Generate.Generate_MeterData import GeneratorWithMeterData


class GeneratorElectricPowerValues(GeneratorWithMeterData):
    """
    Класс для генерации данных в для таблицы ElectricPowerValues

    """

    MeterData = {}
    ElectricPowerValues = {}
    DeviceIdx = 0
    RecordTypeId = ''
    Redefine_tag = {}
    MeterData_tag = {}
    Count_timestamp = 1
    cTime = 30

    def __init__(self, DeviceIdx: int, RecordTypeId: str, Redefine_tag: dict = {}, Count_timestamp: int = 1 , cTime :int = 30):

        # Чтоб в будущем не выстрелить себе в ногу - Сначала ставим константы
        self.count = 1
        self.DeviceIdx = 0
        self.RecordTypeId = ''
        self.MeterData_tag = {}
        self.cTime = cTime

        # Теперь Переопределяем тэги
        self.DeviceIdx = DeviceIdx
        self.RecordTypeId = RecordTypeId
        self.Count_timestamp = Count_timestamp
        # С Переопределяемымыми тэгами - сложнее - отделяем мух от котлет и meter data тэги от остальных
        self.Redefine_tag = self._find_redefine_tag(Redefine_tag)

        # Генерируем MeterData
        self.MeterData = self._generate_MeterData()
        # Разделяем переопределение тэгов

        # ТЕПЕРЬ ЧТО ДЕЛАЕМ - ГЕНЕРИРУЕМ НАШИ ОСНОВНЫЕ ДАННЫЕ
        self.ElectricPowerValues = self._Generate_ElectricPowerValues()
        # Теперь все записываем
        self._record_ElectricPowerValues()

    def _Generate_ElectricPowerValues(self):
        """
        Генерация Профиля мощности
        """

        import random
        from copy import deepcopy

        MeterData = deepcopy(self.MeterData)

        for ids in MeterData:
            # генерируем сначала в формате JSON
            ElectricPowerValues_format_JSON = self._generate_ElectricPowerValues_one_record()
            # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
            # Теперь ставим айдишник записи
            # ElectricPowerValues_format_JSON['id'] = deepcopy(self.MeterData[ids]['id'])
            MeterData[ids].update(ElectricPowerValues_format_JSON)

        return MeterData

    def _generate_MeterData(self):
        """
        Здесь Генерируем Данные для Meter Data
        """
        from Service.Generate.Generate_MeterData import GeneratorMeterData
        MeterData = GeneratorMeterData(DeviceIdx=self.DeviceIdx,
                                       RecordTypeId_Name=self.RecordTypeId,
                                       MeterData_tag=self.MeterData_tag,
                                       Count_timestamp=self.Count_timestamp,
                                       cTime= self.cTime).MeterData

        return MeterData

    def _generate_ElectricPowerValues_one_record(self):
        """Здесь генерируем ОДНУ ПОЛНУЮ ЗАПИСЬ"""
        import random
        # генерируем сначала в формате JSON
        ElectricPowerValues_format_JSON = \
            {
                'cTime': self.cTime,
                # 'P+': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                # 'Q+': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                # 'P-': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                # 'Q-': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                # 'isPart': random.randint(0, 1),
                # 'isOvfl': random.randint(0, 1),
                # 'isSummer': random.randint(0, 1),
                'P+': float(1.0),
                'Q+': float(3.0),
                'P-': float(2.0),
                'Q-': float(4.0),
                'isPart': 1,
                'isOvfl': 1,
                'isSummer': 1,
            }
        # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
        ElectricPowerValues_format_JSON = self._redefine_tag(ElectricPowerValues_format_JSON)

        return ElectricPowerValues_format_JSON

    def _record_ElectricPowerValues(self):
        """
        Это метод записи значений в БД
        """
        from copy import deepcopy

        # Итак что делаем - Сделаем цикл

        ElectricPowerValues_format_JSON = deepcopy(self.ElectricPowerValues)

        # Переводим в значения равные БД
        # Перебираем все значения что сгенерированли
        ElectricPowerValues_list = []

        for ids in ElectricPowerValues_format_JSON:
            # Формируем 5 списков как раз по тарифам

            ElectricPowerValues = {
                'Id': ElectricPowerValues_format_JSON[ids].get('Id'),
                'Period': ElectricPowerValues_format_JSON[ids].get('cTime'),
                'Pp': ElectricPowerValues_format_JSON[ids].get('P+'),
                'Pm': ElectricPowerValues_format_JSON[ids].get('P-'),
                'Qp': ElectricPowerValues_format_JSON[ids].get('Q+'),
                'Qm': ElectricPowerValues_format_JSON[ids].get('Q-'),
                'Partial': ElectricPowerValues_format_JSON[ids].get('isPart'),
                'Overflow': ElectricPowerValues_format_JSON[ids].get('isOvfl'),
                'Season': ElectricPowerValues_format_JSON[ids].get('isSummer')
            }

            # А теперь берем добавляем это все в наш список
            ElectricPowerValues_list.append(ElectricPowerValues)

        # начинаем формировать команду

        columns_list = [
            'Id',
            'Period',
            'Pp',
            'Pm',
            'Qp',
            'Qm',
            'Partial',
            'Overflow',
            'Season'
        ]

        columns = ''
        values = ''

        # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

        for i in range(len(columns_list)):
            columns = columns + columns_list[i] + ' , '

        # ТЕПЕРЬ ФОРМИРУЕМ ВСЕ ЗНАЧЕНИЯ
        for i in range(len(ElectricPowerValues_list)):
            values_element = ''
            for x in range(len(columns_list)):
                # если это стринг - то экранируем его
                if type(ElectricPowerValues_list[i].get(columns_list[x])) == str:
                    ElectricPowerValues_list[i][columns_list[x]] = '\"' + ElectricPowerValues_list[i].get(
                        columns_list[x]) + '\"'

                values_element = values_element + str(ElectricPowerValues_list[i].get(columns_list[x])) + ' , '
            # Обрезаем последнюю запятую
            values_element = values_element[:-2]
            values = values + ' ( ' + values_element + ' ) , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO ElectricPowerValues ( ' + columns + ') VALUES  ' + values + ' ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from Service.Work_With_Database import SQL

        result = SQL(command=command)
