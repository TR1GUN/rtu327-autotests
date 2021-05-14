# Здесь находится селект в таблицу Энергии
from Service.Generate.Generate_MeterData import GeneratorWithMeterData


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
    cTime = 30
    def __init__(self, DeviceIdx: int, RecordTypeId: str, Redefine_tag: dict = {}, Count_timestamp: int = 1):

        # Чтоб в будущем не выстрелить себе в ногу - Сначала ставим константы
        self.count = 1
        self.DeviceIdx = 0
        self.RecordTypeId = ''
        self.MeterData_tag = {}
        self.MeterData = {}
        self.ElectricEnergyValues = {}

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
        self.ElectricEnergyValues = self._Generate_ElectricEnergyValues()
        # Теперь все записываем
        self._record_ElectricEnergyValues()

    def _Generate_ElectricEnergyValues(self):
        """
        Генерация Профиля мощности
        """

        from copy import deepcopy


        MeterData = deepcopy(self.MeterData)

        for ids in MeterData:
            # генерируем сначала в формате JSON
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

    def _record_ElectricEnergyValues(self):
        """
        Это метод записи значений в БД
        """
        from copy import deepcopy

        # Итак что делаем - Сделаем цикл

        ElectricEnergyValues_format_JSON = deepcopy(self.ElectricEnergyValues)

        # Переводим в значения равные БД
        # Перебираем все значения что сгенерированли
        ElectricEnergyValues_list = []

        for ids in ElectricEnergyValues_format_JSON:
            # Формируем 5 списков как раз по тарифам

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

        # начинаем формировать команду

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

                values_element = values_element + str(ElectricEnergyValues_list[i].get(columns_list[x])) + ' , '
            # Обрезаем последнюю запятую
            values_element = values_element[:-2]
            values = values + ' ( ' + values_element + ' ) , '

        # Обрезаем последнюю запятую
        columns = columns[:-2]
        values = values[:-2]

        command = 'INSERT INTO ElectricEnergyValues ( ' + columns + ') VALUES  ' + values + ' ;'

        # ТЕПЕРЬ ОТПРАВЛЯЕМ КОМАНДУ НА ЗАПИСЬ
        from Service.Work_With_Database import SQL

        result = SQL(command=command)
