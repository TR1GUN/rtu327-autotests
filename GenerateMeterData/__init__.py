
# Импортируем настрйоки из НАшего Конфиг парсера
from Service.Config_Parser import user_login, user_password ,ip_address ,port_ssh

IP_address = ip_address
IP_port = port_ssh
user_login = user_login
user_password = user_password
# Парсим наши настройки


def MeterTable(redefine_tag: dict = {}):
    """

    Генерация Записи счетчика в MeterTable

    Список Тэгов

    MeterId - int - Внешний ID
    ParentId -int - Внешний ID родительского устройства, если нет то 0
    TypeId - int - Id Счетчика
    Address - str - Адрес счетчика
    ReadPassword - str - Пароль для чтения
    WritePassword - str - Пароль для записи
    InterfaceId - int - Id интерфейса
    InterfaceConfig - str - Конфиг интерфейса RS - Скорость , Размер бита + Проверка четности + СтопБит - 9600, 8n1
    RTUObjType - int - тип объекта RTU
    RTUFeederNum - int - номер фидера RTU
    RTUObjNum - int - номер объекта RTU

    :param Count_Meter:
    :param redefine_tag: Словарь тэгов для переопределения
    :return:
    """

    from GenerateMeterData.Generate.Generate_MeterTable import GeneratorMeterTable

    MeterTable_ = GeneratorMeterTable(redefine_tag=redefine_tag)

    return {'MeterTable': MeterTable_.Record_MeterTable}


# //-------------------------------------------------------------------------------------------------------------
# //                            Конфиг Электросчетчика
# //-------------------------------------------------------------------------------------------------------------

def ElConfig(MeterTable=None, Config_tag: dict = {}):
    """
    Генерация Записи конфига счетчика в ElConfig

    Список Тэгов

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    Serial - str - Серийный номер
    Model - str - Модель счетчика
    IntervalPowerArrays - int - Время интеграции - Через сколько снимается профиль мощности
    DST - int_bool - Переход на летнее - зимнее время, True - 1 , False - 0
    Clock - int_bool - Наличие часов, True - 1 , False - 0
    Tariff - int_bool - Наличие тарификатора, True - 1 , False - 0
    Reactive - int_bool - Наличие реактивной энергии, True - 1 , False - 0
    ActiveReverse - int_bool - Наличие активной обратной энергии, True - 1 , False - 0
    ReactiveReverse - int_bool - Наличие реактивной обратной энергии, True - 1 , False - 0
    CurrentCoeff - float - Коэффициент  трансформации Силы тока
    VoltageCoeff - float - Коэффициент  трансформации Напряжения
    MeterConst - float - Коэффициент  трансформации

    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param Config_tag: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_Config import GeneratorElectricConfig

    ElectricConfig = GeneratorElectricConfig(Config_tag=Config_tag, MeterTable=MeterTable)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricConfig.Config, "MeterTable": ElectricConfig.MeterTable}

    return result


# //-------------------------------------------------------------------------------------------------------------
# //                            Конфиг диджитал значений
# //-------------------------------------------------------------------------------------------------------------

def DigConfig(MeterTable=None, Config_tag: dict = {}):
    """
    Генерация Записи конфига счетчика в DigConfig

    Список Тэгов

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    Serial - str - Серийный номер
    Model - str - Модель счетчика
    DST - int_bool - Переход на летнее - зимнее время, True - 1 , False - 0
    ChannelsIn - int - Канал входа
    ChannelsOut - int - Канал входа

    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param Config_tag: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_Config import GeneratorDigitalConfig

    DigitalConfig = GeneratorDigitalConfig(Config_tag=Config_tag, MeterTable=MeterTable)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"DigConfig": DigitalConfig.Config, "MeterTable": DigitalConfig.MeterTable}

    return result


# //-------------------------------------------------------------------------------------------------------------
# //                            Конфиг импульсных счетчиков
# //-------------------------------------------------------------------------------------------------------------
def PlsConfig(MeterTable=None, Config_tag: dict = {}):
    """

    Генерация Записи конфига счетчика в PlsConfig

    Список Тэгов

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    Serial - str - Серийный номер
    Model - str - Модель счетчика
    DST - int_bool - Переход на летнее - зимнее время, True - 1 , False - 0
    Channels - int - Количество каналов

    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param Config_tag: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_Config import GeneratorPulseConfig

    PulseConfig = GeneratorPulseConfig(Config_tag=Config_tag, MeterTable=MeterTable)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"PlsConfig": PulseConfig.Config, "MeterTable": PulseConfig.MeterTable}

    return result


# //-------------------------------------------------------------------------------------------------------------
# //                            Данные Электросчетчиков - Энергия
# //-------------------------------------------------------------------------------------------------------------

def ElMomentEnergy(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElMomentEnergy	текущие показания энергии электросчетчика

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    A+0	- float -	Прямая активная энергия по сумме тарифов, Вт*ч
    A+1	- float -	Прямая активная энергия по тарифу 1, Вт*ч
    A+2	- float -	Прямая активная энергия по тарифу 2, Вт*ч
    A+3	- float -	Прямая активная энергия по тарифу 3, Вт*ч
    A+4	- float -	Прямая активная энергия по тарифу 4, Вт*ч
    A-0	- float -	Обратная активная энергия по сумме тарифов, Вт*ч
    A-1	- float -	Обратная активная энергия по тарифу 1, Вт*ч
    A-2	- float -	Обратная активная энергия по тарифу 2, Вт*ч
    A-3	- float -	Обратная активная энергия по тарифу 3, Вт*ч
    A-4	- float -	Обратная активная энергия по тарифу 4, Вт*ч
    R+0	- float -	Прямая реактивная энергия по сумме тарифов, Вт*ч
    R+1	- float -	Прямая реактивная энергия по тарифу 1, Вт*ч
    R+2	- float -	Прямая реактивная энергия по тарифу 2, Вт*ч
    R+3	- float -	Прямая реактивная энергия по тарифу 3, Вт*ч
    R+4	- float -	Прямая реактивная энергия по тарифу 4, Вт*ч
    R-0	- float -	Обратная реактивная энергия по сумме тарифов, Вт*ч
    R-1	- float -	Обратная реактивная энергия по тарифу 1, Вт*ч
    R-2	- float -	Обратная реактивная энергия по тарифу 2, Вт*ч
    R-3	- float -	Обратная реактивная энергия по тарифу 3, Вт*ч
    R-4	- float -	Обратная реактивная энергия по тарифу 4, Вт*ч

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues

    RecordTypeId = 'ElMomentEnergy'

    ElectricEnergyValues = GeneratorElectricEnergyValues(RecordTypeId=RecordTypeId,
                                                         Redefine_tag=Redefine_tag,
                                                         Count_timestamp=Count_timestamp,
                                                         MeterTable=MeterTable,
                                                         ElConfig=ElConfig)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricEnergyValues.Config,
              "MeterTable": ElectricEnergyValues.MeterTable,
              RecordTypeId: ElectricEnergyValues.ElectricEnergyValues
              }
    return result


def ElDayEnergy(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElDayEnergy	показания на начало суток электросчетчика

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    A+0	- float -	Прямая активная энергия по сумме тарифов, Вт*ч
    A+1	- float -	Прямая активная энергия по тарифу 1, Вт*ч
    A+2	- float -	Прямая активная энергия по тарифу 2, Вт*ч
    A+3	- float -	Прямая активная энергия по тарифу 3, Вт*ч
    A+4	- float -	Прямая активная энергия по тарифу 4, Вт*ч
    A-0	- float -	Обратная активная энергия по сумме тарифов, Вт*ч
    A-1	- float -	Обратная активная энергия по тарифу 1, Вт*ч
    A-2	- float -	Обратная активная энергия по тарифу 2, Вт*ч
    A-3	- float -	Обратная активная энергия по тарифу 3, Вт*ч
    A-4	- float -	Обратная активная энергия по тарифу 4, Вт*ч
    R+0	- float -	Прямая реактивная энергия по сумме тарифов, Вт*ч
    R+1	- float -	Прямая реактивная энергия по тарифу 1, Вт*ч
    R+2	- float -	Прямая реактивная энергия по тарифу 2, Вт*ч
    R+3	- float -	Прямая реактивная энергия по тарифу 3, Вт*ч
    R+4	- float -	Прямая реактивная энергия по тарифу 4, Вт*ч
    R-0	- float -	Обратная реактивная энергия по сумме тарифов, Вт*ч
    R-1	- float -	Обратная реактивная энергия по тарифу 1, Вт*ч
    R-2	- float -	Обратная реактивная энергия по тарифу 2, Вт*ч
    R-3	- float -	Обратная реактивная энергия по тарифу 3, Вт*ч
    R-4	- float -	Обратная реактивная энергия по тарифу 4, Вт*ч

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues

    RecordTypeId = 'ElDayEnergy'

    ElectricEnergyValues = GeneratorElectricEnergyValues(RecordTypeId=RecordTypeId,
                                                         Redefine_tag=Redefine_tag,
                                                         Count_timestamp=Count_timestamp,
                                                         MeterTable=MeterTable,
                                                         ElConfig=ElConfig)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricEnergyValues.Config,
              "MeterTable": ElectricEnergyValues.MeterTable,
              RecordTypeId: ElectricEnergyValues.ElectricEnergyValues
              }

    return result


def ElMonthEnergy(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElMonthEnergy	показания на начало месяца электросчетчика

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    A+0	- float -	Прямая активная энергия по сумме тарифов, Вт*ч
    A+1	- float -	Прямая активная энергия по тарифу 1, Вт*ч
    A+2	- float -	Прямая активная энергия по тарифу 2, Вт*ч
    A+3	- float -	Прямая активная энергия по тарифу 3, Вт*ч
    A+4	- float -	Прямая активная энергия по тарифу 4, Вт*ч
    A-0	- float -	Обратная активная энергия по сумме тарифов, Вт*ч
    A-1	- float -	Обратная активная энергия по тарифу 1, Вт*ч
    A-2	- float -	Обратная активная энергия по тарифу 2, Вт*ч
    A-3	- float -	Обратная активная энергия по тарифу 3, Вт*ч
    A-4	- float -	Обратная активная энергия по тарифу 4, Вт*ч
    R+0	- float -	Прямая реактивная энергия по сумме тарифов, Вт*ч
    R+1	- float -	Прямая реактивная энергия по тарифу 1, Вт*ч
    R+2	- float -	Прямая реактивная энергия по тарифу 2, Вт*ч
    R+3	- float -	Прямая реактивная энергия по тарифу 3, Вт*ч
    R+4	- float -	Прямая реактивная энергия по тарифу 4, Вт*ч
    R-0	- float -	Обратная реактивная энергия по сумме тарифов, Вт*ч
    R-1	- float -	Обратная реактивная энергия по тарифу 1, Вт*ч
    R-2	- float -	Обратная реактивная энергия по тарифу 2, Вт*ч
    R-3	- float -	Обратная реактивная энергия по тарифу 3, Вт*ч
    R-4	- float -	Обратная реактивная энергия по тарифу 4, Вт*ч

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues

    RecordTypeId = 'ElMonthEnergy'

    ElectricEnergyValues = GeneratorElectricEnergyValues(RecordTypeId=RecordTypeId,
                                                         Redefine_tag=Redefine_tag,
                                                         Count_timestamp=Count_timestamp,
                                                         MeterTable=MeterTable,
                                                         ElConfig=ElConfig)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricEnergyValues.Config,
              "MeterTable": ElectricEnergyValues.MeterTable,
              RecordTypeId: ElectricEnergyValues.ElectricEnergyValues
              }
    return result


def ElDayConsEnergy(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElDayConsEnergy	потребление за сутки электросчетчика

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    A+0	- float -	Прямая активная энергия по сумме тарифов, Вт*ч
    A+1	- float -	Прямая активная энергия по тарифу 1, Вт*ч
    A+2	- float -	Прямая активная энергия по тарифу 2, Вт*ч
    A+3	- float -	Прямая активная энергия по тарифу 3, Вт*ч
    A+4	- float -	Прямая активная энергия по тарифу 4, Вт*ч
    A-0	- float -	Обратная активная энергия по сумме тарифов, Вт*ч
    A-1	- float -	Обратная активная энергия по тарифу 1, Вт*ч
    A-2	- float -	Обратная активная энергия по тарифу 2, Вт*ч
    A-3	- float -	Обратная активная энергия по тарифу 3, Вт*ч
    A-4	- float -	Обратная активная энергия по тарифу 4, Вт*ч
    R+0	- float -	Прямая реактивная энергия по сумме тарифов, Вт*ч
    R+1	- float -	Прямая реактивная энергия по тарифу 1, Вт*ч
    R+2	- float -	Прямая реактивная энергия по тарифу 2, Вт*ч
    R+3	- float -	Прямая реактивная энергия по тарифу 3, Вт*ч
    R+4	- float -	Прямая реактивная энергия по тарифу 4, Вт*ч
    R-0	- float -	Обратная реактивная энергия по сумме тарифов, Вт*ч
    R-1	- float -	Обратная реактивная энергия по тарифу 1, Вт*ч
    R-2	- float -	Обратная реактивная энергия по тарифу 2, Вт*ч
    R-3	- float -	Обратная реактивная энергия по тарифу 3, Вт*ч
    R-4	- float -	Обратная реактивная энергия по тарифу 4, Вт*ч

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues

    RecordTypeId = 'ElDayConsEnergy'

    ElectricEnergyValues = GeneratorElectricEnergyValues(RecordTypeId=RecordTypeId,
                                                         Redefine_tag=Redefine_tag,
                                                         Count_timestamp=Count_timestamp,
                                                         MeterTable=MeterTable,
                                                         ElConfig=ElConfig)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricEnergyValues.Config,
              "MeterTable": ElectricEnergyValues.MeterTable,
              RecordTypeId: ElectricEnergyValues.ElectricEnergyValues
              }
    return result


def ElMonthConsEnergy(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElMonthConsEnergy	потребление за месяц электросчетчика

    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    A+0	- float -	Прямая активная энергия по сумме тарифов, Вт*ч
    A+1	- float -	Прямая активная энергия по тарифу 1, Вт*ч
    A+2	- float -	Прямая активная энергия по тарифу 2, Вт*ч
    A+3	- float -	Прямая активная энергия по тарифу 3, Вт*ч
    A+4	- float -	Прямая активная энергия по тарифу 4, Вт*ч
    A-0	- float -	Обратная активная энергия по сумме тарифов, Вт*ч
    A-1	- float -	Обратная активная энергия по тарифу 1, Вт*ч
    A-2	- float -	Обратная активная энергия по тарифу 2, Вт*ч
    A-3	- float -	Обратная активная энергия по тарифу 3, Вт*ч
    A-4	- float -	Обратная активная энергия по тарифу 4, Вт*ч
    R+0	- float -	Прямая реактивная энергия по сумме тарифов, Вт*ч
    R+1	- float -	Прямая реактивная энергия по тарифу 1, Вт*ч
    R+2	- float -	Прямая реактивная энергия по тарифу 2, Вт*ч
    R+3	- float -	Прямая реактивная энергия по тарифу 3, Вт*ч
    R+4	- float -	Прямая реактивная энергия по тарифу 4, Вт*ч
    R-0	- float -	Обратная реактивная энергия по сумме тарифов, Вт*ч
    R-1	- float -	Обратная реактивная энергия по тарифу 1, Вт*ч
    R-2	- float -	Обратная реактивная энергия по тарифу 2, Вт*ч
    R-3	- float -	Обратная реактивная энергия по тарифу 3, Вт*ч
    R-4	- float -	Обратная реактивная энергия по тарифу 4, Вт*ч

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricEnergyValues import GeneratorElectricEnergyValues

    RecordTypeId = 'ElMonthConsEnergy'

    ElectricEnergyValues = GeneratorElectricEnergyValues(RecordTypeId=RecordTypeId,
                                                         Redefine_tag=Redefine_tag,
                                                         Count_timestamp=Count_timestamp,
                                                         MeterTable=MeterTable,
                                                         ElConfig=ElConfig)

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricEnergyValues.Config,
              "MeterTable": ElectricEnergyValues.MeterTable,
              RecordTypeId: ElectricEnergyValues.ElectricEnergyValues
              }
    return result


# //-------------------------------------------------------------------------------------------------------------
# //                            текущие ПКЭ электросчетчика
# //-------------------------------------------------------------------------------------------------------------


def ElMomentQuality(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElMomentQuality	текущие ПКЭ электросчетчика


    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    UA - float - Напряжение фазы A, В
    UB - float - Напряжение фазы B, В
    UC - float - Напряжение фазы C, В
    IA - float - Ток фазы A, А
    IB - float - Ток фазы B, А
    IC - float - Ток фазы C, А
    PS - float - Активная мощность суммы фаз, Вт
    PA - float - Активная мощность фазы А, Вт
    PB - float - Активная мощность фазы B, Вт
    PC - float - Активная мощность фазы C, Вт
    QS - float - Реактивная мощность суммы фаз, Вт
    QA - float - Реактивная мощность фазы А, Вт
    QB - float - Реактивная мощность фазы B, Вт
    QC - float - Реактивная мощность фазы C, Вт
    SS - float - Полная мощность суммы фаз, Вт
    SA - float - Полная мощность фазы А, Вт
    SB - float - Полная мощность фазы B, Вт
    SC - float - Полная мощность фазы C, Вт
    AngAB - float - Угол между фазами AB, град
    AngBC - float - Угол между фазами BC, град
    AngAC - float - Угол между фазами AC, град
    kPS - float - Коэффициент мощности суммы фаз
    kPA - float - Коэффициент мощности фазы А
    kPB - float - Коэффициент мощности фазы B
    kPC - float - Коэффициент мощности фазы C
    Freq - float - Частота сети, Гц

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricQualityValues import GeneratorElectricQualityValues

    ElectricQualityValues = GeneratorElectricQualityValues(
        Redefine_tag=Redefine_tag,
        Count_timestamp=Count_timestamp,
        MeterTable=MeterTable,
        ElConfig=ElConfig
    )

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricQualityValues.Config,
              "MeterTable": ElectricQualityValues.MeterTable,
              ElectricQualityValues.RecordTypeId: ElectricQualityValues.ElectricQualityValues
              }
    return result


# //-------------------------------------------------------------------------------------------------------------
# //                            профили мощности первого архива электросчетчика
# //-------------------------------------------------------------------------------------------------------------

def ElArr1ConsPower(
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    ElArr1ConsPower	профили мощности первого архива электросчетчика


    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    P+	- float -	Прямая активная мощность среза профиля мощности, Вт
    P-	- float -	Прямая реактивная мощность среза профиля мощности, Вт
    Q+	- float -	Обратная активная мощность среза профиля мощности, Вт
    Q-	- float -	Обратная реактивная мощность среза профиля мощности, Вт
    isSummer - int_bool - Флаг летнего времени среза профиля мощности
    isOvfl	- int_bool - Флаг переполнения среза профиля мощности
    isPart - int_bool - Флаг неполного среза профиля мощности

    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_ElectricPowerValues import GeneratorElectricPowerValues

    if Redefine_tag.get('сTime') is None:
        сTime = 30
    else:
        сTime = Redefine_tag.get('сTime')

    ElectricPowerValues = GeneratorElectricPowerValues(
        Redefine_tag=Redefine_tag,
        Count_timestamp=Count_timestamp,
        cTime = сTime,
        MeterTable=MeterTable,
        ElConfig=ElConfig
    )

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": ElectricPowerValues.Config,
              "MeterTable": ElectricPowerValues.MeterTable,
              ElectricPowerValues.RecordTypeId: ElectricPowerValues.ElectricPowerValues
              }
    return result


# //-------------------------------------------------------------------------------------------------------------
# //                                        Журналы
# //-------------------------------------------------------------------------------------------------------------

def Journal(
        RecordTypeId: str,
        Redefine_tag: dict = {},
        Count_timestamp: int = 1,
        MeterTable=None,
        ElConfig=None
):
    """
    Journal	Журналы


    DeviceIdx - int - Внутренний ID
    Timestamp - int - Таймштамп в Unixtime
    RecordTypeId - int - ID типа данных
    Valid - int_bool - Наличие соответствия записи, True - 1 , False - 0

    eventId	- int_bool - Номер события
    event - int_bool -	Код события


    :param Redefine_tag: - Словарь Переопределение тэгов - Значения
    :param Count_timestamp: - Количество Генерируемых записей
    :param MeterTable: - Словарь записи счетчика в таблице - Если нет -то он генерируется и записывается
    :param ElConfig: - Словарь Конфига - Если нет -то он генерируется и записывается
    :return:
    """

    from GenerateMeterData.Generate.Generate_JournalValues import GeneratorJournalValues

    JournalValues = GeneratorJournalValues(
        RecordTypeId=RecordTypeId,
        Redefine_tag=Redefine_tag,
        Count_timestamp=Count_timestamp,
        MeterTable=MeterTable,
        ElConfig=ElConfig
    )

    # Теперь что даелаем - Вытаскиваем значения конфига

    result = {"ElConfig": JournalValues.Config,
              "MeterTable": JournalValues.MeterTable,
              JournalValues.RecordTypeId: JournalValues.JournalValues
              }
    return result


# //-------------------------------------------------------------------------------------------------------------
# //                                        Журналы
# //-------------------------------------------------------------------------------------------------------------

class JournalName:
    ElJrnlPwr = 'ElJrnlPwr'
    ElJrnlTimeCorr = 'ElJrnlTimeCorr'
    ElJrnlReset = 'ElJrnlReset'
    ElJrnlC1Init = 'ElJrnlC1Init'
    ElJrnlC2Init = 'ElJrnlC2Init'
    ElJrnlTrfCorr = 'ElJrnlTrfCorr'
    ElJrnlOpen = 'ElJrnlOpen'
    ElJrnlUnAyth = 'ElJrnlUnAyth'
    ElJrnlPwrA = 'ElJrnlPwrA'
    ElJrnlPwrB = 'ElJrnlPwrB'
    ElJrnlPwrC = 'ElJrnlPwrC'
    ElJrnlProg = 'ElJrnlProg'
    ElJrnlRelay = 'ElJrnlRelay'
    ElJrnlLimESumm = 'ElJrnlLimESumm'
    ElJrnlLimETrf = 'ElJrnlLimETrf'
    ElJrnlLimETrf1 = 'ElJrnlLimETrf1'
    ElJrnlLimETrf2 = 'ElJrnlLimETrf2'
    ElJrnlLimETrf3 = 'ElJrnlLimETrf3'
    ElJrnlLimETrf4 = 'ElJrnlLimETrf4'
    ElJrnlLimUAMax = 'ElJrnlLimUAMax'
    ElJrnlLimUAMin = 'ElJrnlLimUAMin'
    ElJrnlLimUBMax = 'ElJrnlLimUBMax'
    ElJrnlLimUBMin = 'ElJrnlLimUBMin'
    ElJrnlLimUCMax = 'ElJrnlLimUCMax'
    ElJrnlLimUCMin = 'ElJrnlLimUCMin'
    ElJrnlLimUABMax = 'ElJrnlLimUABMax'
    ElJrnlLimUABMin = 'ElJrnlLimUABMin'
    ElJrnlLimUBCMax = 'ElJrnlLimUBCMax'
    ElJrnlLimUBCMin = 'ElJrnlLimUBCMin'
    ElJrnlLimUCAMax = 'ElJrnlLimUCAMax'
    ElJrnlLimUCAMin = 'ElJrnlLimUCAMin'
    ElJrnlLimIAMax = 'ElJrnlLimIAMax'
    ElJrnlLimIBMax = 'ElJrnlLimIBMax'
    ElJrnlLimICMax = 'ElJrnlLimICMax'
    ElJrnlLimFreqMax = 'ElJrnlLimFreqMax'
    ElJrnlLimFreqMin = 'ElJrnlLimFreqMin'
    ElJrnlLimPwr = 'ElJrnlLimPwr'
    ElJrnlLimPwrPP = 'ElJrnlLimPwrPP'
    ElJrnlLimPwrPM = 'ElJrnlLimPwrPM'
    ElJrnlLimPwrQP = 'ElJrnlLimPwrQP'
    ElJrnlLimPwrQM = 'ElJrnlLimPwrQM'
    ElJrnlReverce = 'ElJrnlReverce'
    PlsJrnlTimeCorr = 'PlsJrnlTimeCorr'
