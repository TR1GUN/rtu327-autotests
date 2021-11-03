from datetime import datetime, timedelta
import time

# Что делаем - Делим все наши значения на несколько групп :

# Группа первая - Значения показателей на день
measure_containin_day_list = \
    [
        'ElDayEnergy',
        'ElDayConsEnergy',
    ]
# Группа вторая -  Значения показателей на месяц
measure_containin_month_list = \
    [
        'ElMonthEnergy',
        'ElMonthConsEnergy',

        # добаляем Журнал включения/выключения питания
        # 'ElJrnlPwr',
        # добаляем Журнал отказов в доступе
        # 'ElJrnlUnAyth',
    ]

# Группа третья -  Значения показателей на 30 минут
measure_containin_half_hour_list = \
    [
        'ElArr1ConsPower'
    ]
# Группа пятая   -  Моментное время
measure_moment_list = \
    [
        'ElConfig',
        'ElMomentEnergy',
        'ElMomentQuality',
    ]
# Группа Шестая   -  ЖУРНАЛЫ
measure_Journal_list = ['ElJrnlPwr', 'ElJrnlTimeCorr', 'ElJrnlReset', 'ElJrnlC1Init', 'ElJrnlC2Init', 'ElJrnlTrfCorr',
                        'ElJrnlOpen',
                        'ElJrnlUnAyth', 'ElJrnlPwrA', 'ElJrnlPwrB', 'ElJrnlPwrC', 'ElJrnlProg', 'ElJrnlRelay',
                        'ElJrnlLimESumm',
                        'ElJrnlLimETrf', 'ElJrnlLimETrf1', 'ElJrnlLimETrf2', 'ElJrnlLimETrf3', 'ElJrnlLimETrf4',
                        'ElJrnlLimUAMax',
                        'ElJrnlLimUAMin', 'ElJrnlLimUBMax', 'ElJrnlLimUBMin', 'ElJrnlLimUCMax', 'ElJrnlLimUCMin',
                        'ElJrnlLimUABMax',
                        'ElJrnlLimUABMin', 'ElJrnlLimUBCMax', 'ElJrnlLimUBCMin', 'ElJrnlLimUCAMax', 'ElJrnlLimUCAMin',
                        'ElJrnlLimIAMax', 'ElJrnlLimIBMax', 'ElJrnlLimICMax', 'ElJrnlLimFreqMax', 'ElJrnlLimFreqMin',
                        'ElJrnlLimPwr',
                        'ElJrnlLimPwrPP', 'ElJrnlLimPwrPM', 'ElJrnlLimPwrQP', 'ElJrnlLimPwrQM', 'ElJrnlReverce',
                        'PlsJrnlTimeCorr'
                        ]


# # -------------------------------------------------------------------------------------------------------------------
#                             Класс для ОПРЕДЕЛЕНИЯ СТАРТОВОГО ВРЕМЕНИ
# # -------------------------------------------------------------------------------------------------------------------

# # -------------------------------------------------------------------------------------------------------------------
#                             Класс для Генерации нужного массива таймштампов - ЭТО ВАЖНО
# # -------------------------------------------------------------------------------------------------------------------

class GenerateTimestamp:
    measure = ''
    Time = None
    Count_timestamp = 1
    Timestamp_list = []
    cTime = 30

    def __init__(self,
                 # Обязательные параметры:
                 # ТИП ДАННЫХ
                 measure,
                 # Количество таймштампов
                 Count_timestamp: int = 1,
                 cTime: int = 30
                 ):
        self.cTime = cTime
        self.Timestamp_list = []
        self.Count_timestamp = Count_timestamp
        self.measure = measure

        self.Time = datetime.now()

        self.Timestamp_list = self.Generate_Timestamp_list()
        # НЕ ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ
        # Глубина запроса времени

    def Generate_Timestamp_list(self):
        """
        Здесь генерируем нужное количество нужного времени относительно нашего jSON запроса
        :return:
        """

        # Пункт первый смотрим что у нас за 'measures'  и относительно него нам нужны таймштампы

        # Группа первая - Значения показателей на день
        if self.measure in measure_containin_day_list:
            # Число тайм штампов равно глубине разницы дней -
            # Корректируем часы
            self.Time = self.Time.replace(hour=0, minute=0, second=0, microsecond=0)
            # Если у нас показатель на начало суток - то включаем и сегодня тоже
            if self.measure in [measure_containin_day_list[0]]:
                timestamp_list = self.__generate_correct_timestamp_through_timedelta(range_ts=self.Count_timestamp,
                                                                                     day=1,
                                                                                     remove_day=False)
            # Если нет , то и не включаем - СЧЕТ ИДЕТ ОТ ВЧЕРА
            else:
                timestamp_list = self.__generate_correct_timestamp_through_timedelta(range_ts=self.Count_timestamp,
                                                                                     day=1,
                                                                                     remove_day=True)

        # Группа вторая -  Значения показателей на месяц
        elif self.measure in measure_containin_month_list:
            # Корректируем часы
            self.Time = self.Time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Здесь делаем тоже самое что и с днями - для показаний потребления - отнимаем минус месяц
            if self.measure in [measure_containin_month_list[0]]:
                timestamp_list = self.__generate_correct_timestamp(range_ts=self.Count_timestamp, month=1)
            else:
                # А теперь генерируем список этих данных
                timestamp_list = self.__generate_correct_timestamp(range_ts=self.Count_timestamp, month=1,
                                                                   remove_month=True)

        # Группа третья -  Значения показателей на 30 минут - ПРОФИЛИ МОЩНОСТИ
        elif self.measure in measure_containin_half_hour_list:
            # СТАВИМ ПЕРВУЮ ПОПАВШУЮСЯ подходящее время
            self.Time = self.Time.replace(second=0, microsecond=0)
            unix_date_min = time.mktime(self.Time.timetuple()) / 60
            unix_date_power_profile = (unix_date_min - (unix_date_min % self.cTime)) * 60
            # ТЕПЕРЬ ПЕРЕВОДИМ ЭТО В ЧЕЛОВЕЧЕСКИЙ ВИД
            self.Time = datetime.fromtimestamp(unix_date_power_profile)

            timestamp_list = self.__generate_correct_timestamp_through_timedelta(range_ts=self.Count_timestamp,
                                                                                 minute=int(self.cTime))

        # # Группа пятая -  Моментное время
        # elif self.measure in measure_moment_list:
        #     # Число таймштампов равно глубине разницы дней -
        #     self.timestamp_list = self.__generate_correct_timestamp_through_timedelta(range_ts=self.Count_timestamp,
        #                                                                               day=1)
        #
        # Группа Шестая   -  ЖУРНАЛЫ
        elif self.measure in measure_Journal_list:
            from random import randint
            # Число таймштампов равно глубине разницы дней -
            # А теперь генерируем список этих данных
            # Получаем наш список дат , измеряя каждый день
            timestamp_list = self.__generate_correct_timestamp_through_timedelta(range_ts=self.Count_timestamp,
                                                                                      day=1, minute=randint(0, 60))

        # Иначе - Мы обрабаотываем мгновенные показатели
        else:
            self.Time = self.Time.replace(second=0, microsecond=0)
            timestamp_list = self.__generate_correct_timestamp_through_timedelta(range_ts=self.Count_timestamp, day=1)

        return timestamp_list

    def __generate_correct_timestamp(self, range_ts: int = 0,
                                     month: int = 0, remove_month=False):
        """
        Итак - данная функция делает список из timestamp которые будут коректны
        :return:
        """
        timestamp_list = []
        # Пункт первый - Берем стартовую дату
        # date_start = self.Time['start']

        date = self.Time
        # После чего начинаем ее изменять
        date = date.replace(day=1)
        # Если у нас стоит показатель на начало месяца то отнимаем один месяц
        if remove_month:
            # НАЧИНАЕМ СО ПРОШЛОГО МЕСЯЦА
            last_month = date.month - 1
            if last_month < 1:
                last_year = date.year - 1
                last_month = 12
                date = date.replace(year=last_year, month=last_month)
            else:
                date = date.replace(month=last_month)

        for i in range(range_ts):
            # Изначально добавляем нашу дату, переведя ее в unixtime
            # ТЕПЕРЬ СТАВИМ ПЕРВОЕ ЧИСЛО !!!!

            unix_date = time.mktime(date.timetuple())
            timestamp_list.append(int(unix_date))
            # сначала делаем дельту
            # date_month = date.month + month
            date_month = date.month - month

            # Если у нас поулчается 13 месяц то меняем на 1
            # if date_month > 12:
            # date_year = date.year + 1
            # date_month = 1
            if date_month < 1:
                date_year = date.year - 1
                date_month = 12
                date = date.replace(year=date_year, month=date_month)
            else:
                date = date.replace(month=date_month)

            # # ТЕПЕРЬ СТАВИМ ПЕРВОЕ ЧИСЛО !!!!
            # date = date.replace(day=1)

        timestamp_list.reverse()
        # После чего возвращаем наш массив
        return timestamp_list

    def __generate_correct_timestamp_through_timedelta(self, range_ts: int = 0, day: int = 0,
                                                       hour: int = 0, minute: int = 0, remove_day: bool = False):
        """
        Итак - данная функция делает список из timestamp которые будут коректны через таймдельту

        :param range_ts:
        :param day:
        :param hour:
        :param minute:
        :return:
        """
        timestamp_list = []
        # Пункт первый - Берем стартовую дату
        # Начинаем с конца
        date = self.Time
        if remove_day:
            # НАЧИНАЕМ СО ВЧЕРА
            remove_day = timedelta(days=1)
            date = date - remove_day
        # После чего начинаем ее изменять
        for i in range(range_ts):
            # Изначально добавляем нашу дату, переведя ее в unixtime
            unix_date = time.mktime(date.timetuple())
            timestamp_list.append(int(unix_date))
            # сначала делаем дельту

            time_delta = timedelta(days=day, hours=hour, minutes=minute, seconds=0, microseconds=0)
            # Добавляем нашу дельту времени
            date = date - time_delta

        # После чего возвращаем наш массив

        timestamp_list.reverse()
        return timestamp_list
