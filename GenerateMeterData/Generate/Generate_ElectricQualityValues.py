# Здесь находится селект в таблицу Энергии
from GenerateMeterData.Generate.Generate_MeterData import GeneratorWithMeterData


class GeneratorElectricQualityValues(GeneratorWithMeterData):
    """
    Класс для генерации данных в для таблицы ElectricEnergyValues

    """

    MeterData = {}
    ElectricQualityValues = {}
    DeviceIdx = 0
    RecordTypeId = 'ElMomentQuality'
    Redefine_tag = {}
    MeterData_tag = {}
    Count_timestamp = 1
    cTime = 30

    def __init__(self,
                 Redefine_tag: dict = {},
                 Count_timestamp: int = 1,
                 MeterTable=None,
                 ElConfig=None
                 ):

        # Чтоб в будущем не выстрелить себе в ногу - Сначала ставим константы
        self.count = 1
        self.DeviceIdx = 0
        self.MeterData_tag = {}

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

        self.Count_timestamp = Count_timestamp
        # С Переопределяемымыми тэгами - сложнее - отделяем мух от котлет и meter data тэги от остальных
        self.Redefine_tag = self._find_redefine_tag(Redefine_tag)

        # Генерируем MeterData
        self.MeterData = self._generate_MeterData()
        # Разделяем переопределение тэгов

        # ТЕПЕРЬ ЧТО ДЕЛАЕМ - ГЕНЕРИРУЕМ НАШИ ОСНОВНЫЕ ДАННЫЕ
        self.ElectricQualityValues = self._Generate_ElectricQualityValues()
        # Теперь все записываем
        self._record_ElectricQualityValues()

    def _Generate_ElectricQualityValues(self):
        """
        Генерация Профиля мощности
        """

        import random
        from copy import deepcopy

        MeterData = deepcopy(self.MeterData)

        for ids in MeterData:
            # генерируем сначала в формате JSON
            if MeterData[ids].get('Valid') > 0:
                ElectricQualityValues_format_JSON = self._generate_ElectricQualityValues_one_record()
                # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
                MeterData[ids].update(ElectricQualityValues_format_JSON)

        return MeterData

    def _generate_ElectricQualityValues_one_record(self):
        """Здесь генерируем ОДНУ ПОЛНУЮ ЗАПИСЬ"""
        import random
        # генерируем сначала в формате JSON
        ElectricQualityValues_format_JSON = \
            {
                'UA': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'UB': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'UC': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                #//----
                'IA': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'IB': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'IC': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                # //----
                'PS': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'PA': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'PB': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'PC': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                # //----
                'QS': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'QA': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'QB': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'QC': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                # //----
                'kPS': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'kPA': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'kPB': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'kPC': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                # //----
                'SS': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'SA': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'SB': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                'SC': float('{:.3f}'.format(float(random.uniform(111.111, 999.999)))),
                # //----
                'AngAB': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                'AngBC': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                'AngAC': float('{:.4f}'.format(float(random.uniform(-99.99, 99.99)))),
                # //----
                'Freq': float('{:.2f}'.format(float(random.uniform(11.11, 99.99)))),
            }
        # ТЕПЕРЬ ПЕРЕЗАПИСЫВАЕМ ЗНАЧЕНИЯ
        ElectricQualityValues_format_JSON = self._redefine_tag(ElectricQualityValues_format_JSON)

        return ElectricQualityValues_format_JSON

    def _record_value_queue(self, ElectricQualityValues_format_JSON):
        """
        Здесь записываем сформированный пакет значений в формате JSON

        :param ElectricQualityValues_format_JSON:
        :return:
        """

        # Перебираем все значения что сгенерированли
        ElectricQualityValues_list = []

        for ids in ElectricQualityValues_format_JSON:
            # Формируем 5 списков как раз по тарифам
            if ElectricQualityValues_format_JSON[ids].get('Valid') > 0:
                ElectricQualityValues_PhaseA = {
                    'Id': ElectricQualityValues_format_JSON[ids].get('Id'),
                    'Phase': 'A',
                    'U': ElectricQualityValues_format_JSON[ids].get('UA'),
                    'I': ElectricQualityValues_format_JSON[ids].get('IA'),
                    'P': ElectricQualityValues_format_JSON[ids].get('PA'),
                    'Q': ElectricQualityValues_format_JSON[ids].get('QA'),
                    'S': ElectricQualityValues_format_JSON[ids].get('SA'),
                    'KP': ElectricQualityValues_format_JSON[ids].get('kPA'),
                    'Angle': ElectricQualityValues_format_JSON[ids].get('AngAB'),
                    'F': None,
                }
                ElectricQualityValues_PhaseB = {
                    'Id': ElectricQualityValues_format_JSON[ids].get('Id'),
                    'Phase': 'B',
                    'U': ElectricQualityValues_format_JSON[ids].get('UB'),
                    'I': ElectricQualityValues_format_JSON[ids].get('IB'),
                    'P': ElectricQualityValues_format_JSON[ids].get('PB'),
                    'Q': ElectricQualityValues_format_JSON[ids].get('QB'),
                    'S': ElectricQualityValues_format_JSON[ids].get('SB'),
                    'KP': ElectricQualityValues_format_JSON[ids].get('kPB'),
                    'Angle': ElectricQualityValues_format_JSON[ids].get('AngBC'),
                    'F': None,
                }

                ElectricQualityValues_PhaseC = {
                    'Id': ElectricQualityValues_format_JSON[ids].get('Id'),
                    'Phase': 'C',
                    'U': ElectricQualityValues_format_JSON[ids].get('UC'),
                    'I': ElectricQualityValues_format_JSON[ids].get('IC'),
                    'P': ElectricQualityValues_format_JSON[ids].get('PC'),
                    'Q': ElectricQualityValues_format_JSON[ids].get('QC'),
                    'S': ElectricQualityValues_format_JSON[ids].get('SC'),
                    'KP': ElectricQualityValues_format_JSON[ids].get('kPC'),
                    'Angle': ElectricQualityValues_format_JSON[ids].get('AngAC'),
                    'F': None,
                }

                ElectricQualityValues_PhaseSUM = {
                    'Id': ElectricQualityValues_format_JSON[ids].get('Id'),
                    'Phase': 'Summ',
                    'U': None,
                    'I': None,
                    'P': ElectricQualityValues_format_JSON[ids].get('PS'),
                    'Q': ElectricQualityValues_format_JSON[ids].get('QS'),
                    'S': ElectricQualityValues_format_JSON[ids].get('SS'),
                    'KP': ElectricQualityValues_format_JSON[ids].get('kPS'),
                    'Angle': None,
                    'F': ElectricQualityValues_format_JSON[ids].get('Freq'),
                }

                # А теперь берем добавляем это все в наш список
                ElectricQualityValues_list.append(ElectricQualityValues_PhaseA)
                ElectricQualityValues_list.append(ElectricQualityValues_PhaseB)
                ElectricQualityValues_list.append(ElectricQualityValues_PhaseC)
                ElectricQualityValues_list.append(ElectricQualityValues_PhaseSUM)

        # начинаем формировать команду
        if len(ElectricQualityValues_list) > 0:
            columns_list = [
                'Id',
                'Phase',
                'U',
                'I',
                'P',
                'Q',
                'S',
                'KP',
                'Angle',
                'F',
                ]

            columns = ''
            values = ''

            # ТЕПЕРЬ ПЕРЕБИРАЕМ ВСЕ КОЛОНКИ

            for i in range(len(columns_list)):
                columns = columns + columns_list[i] + ' , '

            # ТЕПЕРЬ ФОРМИРУЕМ ВСЕ ЗНАЧЕНИЯ
            for i in range(len(ElectricQualityValues_list)):
                values_element = ''
                for x in range(len(columns_list)):
                    # если это стринг - то экранируем его
                    if type(ElectricQualityValues_list[i].get(columns_list[x])) == str:
                        ElectricQualityValues_list[i][columns_list[x]] = '\"' + ElectricQualityValues_list[i].get(
                            columns_list[x]) + '\"'
                    # Если это None То Null
                    elif ElectricQualityValues_list[i].get(columns_list[x]) is None:
                        ElectricQualityValues_list[i][columns_list[x]] = 'Null'


                    values_element = values_element + str(ElectricQualityValues_list[i].get(columns_list[x])) + ' , '
                # Обрезаем последнюю запятую
                values_element = values_element[:-2]
                values = values + ' ( ' + values_element + ' ) , '

            # Обрезаем последнюю запятую
            columns = columns[:-2]
            values = values[:-2]

            command = 'INSERT INTO ElectricQualityValues ( ' + columns + ') VALUES  ' + values + ' ;'

            # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
            from GenerateMeterData.Service.Work_With_Database import SQL

            result = SQL(command=command)

    def _record_ElectricQualityValues(self):
        """
        Это метод записи значений в БД
        """
        from copy import deepcopy

        # # Итак что делаем - Сделаем цикл
        #
        # ElectricQualityValues_format_JSON = deepcopy(self.ElectricQualityValues)
        #
        # # Переводим в значения равные БД
        # # Перебираем все значения что сгенерированли
        # ElectricQualityValues_list = []
        #
        # print(ElectricQualityValues_format_JSON)
        # # Теперь разбираем все это по 150
        # print(len(ElectricQualityValues_format_JSON))


        # Берем наши значения
        ElectricQualityValues = deepcopy(self.ElectricQualityValues)
        ElectricQualityValues_format_JSON = {}

        for key in ElectricQualityValues:
            # Набираем списоак
            ElectricQualityValues_format_JSON[key] = ElectricQualityValues[key]
            # Теперь берем по 150 штук
            if len(ElectricQualityValues_format_JSON) > 150:
                self._record_value_queue(ElectricQualityValues_format_JSON=ElectricQualityValues_format_JSON)
                ElectricQualityValues_format_JSON = {}
        if len(ElectricQualityValues_format_JSON) > 0:
            self._record_value_queue(ElectricQualityValues_format_JSON=ElectricQualityValues_format_JSON)







