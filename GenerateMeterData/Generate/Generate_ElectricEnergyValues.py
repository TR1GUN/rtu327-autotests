# Здесь находится селект в таблицу Энергии
from GenerateMeterData.Generate.Generate_MeterData import GeneratorWithMeterData


class GeneratorElectricEnergyValues(GeneratorWithMeterData):
    """
    Класс для генерации данных в для таблицы ElectricEnergyValues

    """

    MeterData = {}
    ElectricEnergyValues = {}
    DeviceIdx = 0
    RecordTypeId = ''
    Redefine_tag = {}
    MeterData_tag = {}
    Count_timestamp = 1
    Config = {}
    MeterTable = {}
    cTime = 30

    def __init__(self,
                 RecordTypeId: str,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 MeterTable=None,
                 ElConfig=None
                 ):

        # Чтоб в будущем не выстрелить себе в ногу - Сначала ставим константы
        self.count = 1
        self.DeviceIdx = 0
        self.RecordTypeId = ''
        self.MeterData_tag = {}
        self.MeterData = {}
        self.ElectricEnergyValues = {}
        self.Config = {}
        self.MeterTable = {}

        # Теперь Переопределяем тэги
        # MeterTable -
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
        # С Переопределяемыми тэгами - сложнее - отделяем мух от котлет и meter data тэги от остальных
        self.Redefine_tag = self._find_redefine_tag(Redefine_tag)

        # Генерируем MeterData
        self.MeterData = self._generate_MeterData()
        # Разделяем переопределение тэгов

        # ТЕПЕРЬ ЧТО ДЕЛАЕМ - ГЕНЕРИРУЕМ НАШИ ОСНОВНЫЕ ДАННЫЕ
        self.ElectricEnergyValues = self._Generate_ElectricEnergyValues()
        # Теперь все записываем
        self._record_ElectricEnergyValues()

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

    def _Generate_ElectricEnergyValues(self):
        """
        Генерация Профиля мощности
        """

        from copy import deepcopy

        MeterData = deepcopy(self.MeterData)

        for ids in MeterData:
            # генерируем сначала в формате JSON
            # Если Valid > 0 Генерируем
            if MeterData[ids].get('Valid') > 0:
                ElectricPowerValues_format_JSON = self._generate_ElectricEnergyValues_one_record()
                # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
                # Теперь ставим айдишник записи
                # ElectricPowerValues_format_JSON['id'] = deepcopy(self.MeterData[ids]['id'])
                MeterData[ids].update(ElectricPowerValues_format_JSON)

        return MeterData

    def _generate_ElectricEnergyValues_one_record(self):
        """Здесь генерируем ОДНУ ПОЛНУЮ ЗАПИСЬ"""
        import random
        # генерируем сначала в формате JSON
        ElectricPowerValues_format_JSON = \
            {
                'A+0': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A+1': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A+2': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A+3': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A+4': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A-0': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A-1': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A-2': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A-3': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'A-4': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R+0': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R+1': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R+2': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R+3': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R+4': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R-0': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R-1': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R-2': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R-3': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'R-4': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
            }
        # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
        ElectricPowerValues_format_JSON = self._redefine_tag(ElectricPowerValues_format_JSON)

        return ElectricPowerValues_format_JSON

    def _record_value_queue(self, ElectricEnergyValues_format_JSON):

        """

        Здесь записываем сформированный пакет значений в формате JSON

        :param ElectricEnergyValues_format_JSON:
        :return:
        """
        # Переводим в значения равные БД
        # Перебираем все значения что сгенерированли
        ElectricEnergyValues_list = []

        for ids in ElectricEnergyValues_format_JSON:
            # Формируем 5 списков как раз по тарифам
            # ВСЕ ЗАПИСЫВАЕМ ТОЛЬКО ЕСЛИ VALID > 0 :
            if ElectricEnergyValues_format_JSON[ids].get('Valid') > 0:
                ElectricEnergyValues_tariff0 = {
                    'Id': ElectricEnergyValues_format_JSON[ids].get('Id'),
                    'Tariff': 0,
                    'Ap': ElectricEnergyValues_format_JSON[ids].get('A+0'),
                    'Rp': ElectricEnergyValues_format_JSON[ids].get('R+0'),
                    'Am': ElectricEnergyValues_format_JSON[ids].get('A-0'),
                    'Rm': ElectricEnergyValues_format_JSON[ids].get('R-0'),
                }
                ElectricEnergyValues_tariff1 = {
                    'Id': ElectricEnergyValues_format_JSON[ids].get('Id'),
                    'Tariff': 1,
                    'Ap': ElectricEnergyValues_format_JSON[ids].get('A+1'),
                    'Rp': ElectricEnergyValues_format_JSON[ids].get('R+1'),
                    'Am': ElectricEnergyValues_format_JSON[ids].get('A-1'),
                    'Rm': ElectricEnergyValues_format_JSON[ids].get('R-1'),
                }

                ElectricEnergyValues_tariff2 = {
                    'Id': ElectricEnergyValues_format_JSON[ids].get('Id'),
                    'Tariff': 2,
                    'Ap': ElectricEnergyValues_format_JSON[ids].get('A+2'),
                    'Rp': ElectricEnergyValues_format_JSON[ids].get('R+2'),
                    'Am': ElectricEnergyValues_format_JSON[ids].get('A-2'),
                    'Rm': ElectricEnergyValues_format_JSON[ids].get('R-2'),
                }

                ElectricEnergyValues_tariff3 = {
                    'Id': ElectricEnergyValues_format_JSON[ids].get('Id'),
                    'Tariff': 3,
                    'Ap': ElectricEnergyValues_format_JSON[ids].get('A+3'),
                    'Rp': ElectricEnergyValues_format_JSON[ids].get('R+3'),
                    'Am': ElectricEnergyValues_format_JSON[ids].get('A-3'),
                    'Rm': ElectricEnergyValues_format_JSON[ids].get('R-3'),
                }

                ElectricEnergyValues_tariff4 = {
                    'Id': ElectricEnergyValues_format_JSON[ids].get('Id'),
                    'Tariff': 4,
                    'Ap': ElectricEnergyValues_format_JSON[ids].get('A+4'),
                    'Rp': ElectricEnergyValues_format_JSON[ids].get('R+4'),
                    'Am': ElectricEnergyValues_format_JSON[ids].get('A-4'),
                    'Rm': ElectricEnergyValues_format_JSON[ids].get('R-4'),
                }

                # А теперь берем добавляем это все в наш список
                ElectricEnergyValues_list.append(ElectricEnergyValues_tariff0)
                ElectricEnergyValues_list.append(ElectricEnergyValues_tariff1)
                ElectricEnergyValues_list.append(ElectricEnergyValues_tariff2)
                ElectricEnergyValues_list.append(ElectricEnergyValues_tariff3)
                ElectricEnergyValues_list.append(ElectricEnergyValues_tariff4)

        # начинаем формировать команду ТОЛЬКО В ТМО СЛУЧАЕ ЕСЛИ У НАС ЕСТЬ ХОТЬ ЧТОТО
        if len(ElectricEnergyValues_list) > 0:
            columns_list = [
                'Id',
                'Tariff',
                'Ap',
                'Rp',
                'Am',
                'Rm',
            ]

            columns = ''
            values = ''

            # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

            for i in range(len(columns_list)):
                columns = columns + columns_list[i] + ' , '

            # ТЕПЕРЬ ФОРМИРУЕМ ВСЕ ЗНАЧЕНИЯ
            for i in range(len(ElectricEnergyValues_list)):
                values_element = ''
                for x in range(len(columns_list)):
                    # если это стринг - то экранируем его
                    if type(ElectricEnergyValues_list[i].get(columns_list[x])) == str:
                        ElectricEnergyValues_list[i][columns_list[x]] = '\"' + ElectricEnergyValues_list[i].get(
                            columns_list[x]) + '\"'
                    # Если это None То Null
                    elif ElectricEnergyValues_list[i].get(columns_list[x]) is None:
                        ElectricEnergyValues_list[i][columns_list[x]] = 'Null'

                    values_element = values_element + str(ElectricEnergyValues_list[i].get(columns_list[x])) + ' , '
                # Обрезаем последнюю запятую
                values_element = values_element[:-2]
                values = values + ' ( ' + values_element + ' ) , '

            # Обрезаем последнюю запятую
            columns = columns[:-2]
            values = values[:-2]

            command = 'INSERT INTO ElectricEnergyValues ( ' + columns + ') VALUES  ' + values + ' ;'

            # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
            from GenerateMeterData.Service.Work_With_Database import SQL

            result = SQL(command=command)

    def _record_ElectricEnergyValues(self):
        """
        Это метод записи значений в БД
        """
        from copy import deepcopy

        # Итак что делаем - Сделаем цикл

        ElectricEnergyValues = deepcopy(self.ElectricEnergyValues)

        # Берем наши значения
        ElectricEnergyValues_format_JSON = {}

        for key in ElectricEnergyValues:
            # Набираем списоак
            ElectricEnergyValues_format_JSON[key] = ElectricEnergyValues[key]
            # Теперь берем по 150 штук
            if len(ElectricEnergyValues_format_JSON) > 150:
                self._record_value_queue(ElectricEnergyValues_format_JSON=ElectricEnergyValues_format_JSON)
                ElectricEnergyValues_format_JSON = {}
        if len(ElectricEnergyValues_format_JSON) > 0 :
            self._record_value_queue(ElectricEnergyValues_format_JSON=ElectricEnergyValues_format_JSON)