# Здесь расположим различные константы различных типов данных - ЕТО ВАЖНО
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
        'ElJrnlPwr',
        # добаляем Журнал отказов в доступе
        'ElJrnlUnAyth',
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
measure_Journal_list = [            'ElJrnlPwr', 'ElJrnlTimeCorr', 'ElJrnlReset', 'ElJrnlC1Init', 'ElJrnlC2Init', 'ElJrnlTrfCorr', 'ElJrnlOpen',
            'ElJrnlUnAyth', 'ElJrnlPwrA', 'ElJrnlPwrB', 'ElJrnlPwrC', 'ElJrnlProg', 'ElJrnlRelay', 'ElJrnlLimESumm',
            'ElJrnlLimETrf', 'ElJrnlLimETrf1', 'ElJrnlLimETrf2', 'ElJrnlLimETrf3', 'ElJrnlLimETrf4', 'ElJrnlLimUAMax',
            'ElJrnlLimUAMin', 'ElJrnlLimUBMax', 'ElJrnlLimUBMin', 'ElJrnlLimUCMax', 'ElJrnlLimUCMin', 'ElJrnlLimUABMax',
            'ElJrnlLimUABMin', 'ElJrnlLimUBCMax', 'ElJrnlLimUBCMin', 'ElJrnlLimUCAMax', 'ElJrnlLimUCAMin',
            'ElJrnlLimIAMax', 'ElJrnlLimIBMax', 'ElJrnlLimICMax', 'ElJrnlLimFreqMax', 'ElJrnlLimFreqMin', 'ElJrnlLimPwr',
            'ElJrnlLimPwrPP', 'ElJrnlLimPwrPM', 'ElJrnlLimPwrQP', 'ElJrnlLimPwrQM', 'ElJrnlReverce', 'PlsJrnlTimeCorr'
                        ]


Journal_dict = \
    {
        'ElJrnlPwr': 1,
        'ElJrnlTimeCorr': 2,
        'ElJrnlReset': 3,
        'ElJrnlTrfCorr': 6,
        'ElJrnlOpen': 7,
        'ElJrnlUnAyth': 8,
        'ElJrnlPwrA': 9,
        'ElJrnlPwrB': 10,
        'ElJrnlPwrC': 11,
        'ElJrnlLimUAMax': 20,
        'ElJrnlLimUAMin': 21,
        'ElJrnlLimUBMax': 22,
        'ElJrnlLimUBMin': 23,
        'ElJrnlLimUCMax': 24,
        'ElJrnlLimUCMin': 25
    }


JournalValues_list = \
    [
    'ElJrnlPwr',
    'ElJrnlTimeCorr',
    'ElJrnlReset',
    'ElJrnlTrfCorr',
    # 'ElJrnlOpen',
    'ElJrnlUnAyth',
    'ElJrnlPwrA',
    'ElJrnlPwrB',
    'ElJrnlPwrC',
    'ElJrnlLimUAMax',
    'ElJrnlLimUAMin',
    'ElJrnlLimUBMax',
    'ElJrnlLimUBMin',
    'ElJrnlLimUCMax',
    'ElJrnlLimUCMin'
        ]