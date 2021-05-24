import pytest


# -------------------------------------------------------------------------------------------------------------------
#                                        Сервисные функции
# -------------------------------------------------------------------------------------------------------------------

def parametrize(parametrize_dict: list):
    """
    Функция для прикручивания параметров

    """
    parametrs = []
    for i in parametrize_dict:
        line_parametrs = tuple(i.values())
        parametrs.append(line_parametrs)
    return parametrs


# //-----------------------------------------------------------------------------------------------------------------
#                                         GETVERSION
#                                Тест на команду запроса версии
# //-----------------------------------------------------------------------------------------------------------------

def test_GETVERSION():
    """
    Функция для прогона тестов для команды GETVERSION
    """
    from command_service import command_GETVERSION
    command_GETVERSION()


# //-----------------------------------------------------------------------------------------------------------------
#                                         GETTIME
#                               # Тест на команду запроса времени
# //-----------------------------------------------------------------------------------------------------------------

def test_GETTIME():
    """
    Функция для прогона тестов для команды GETTIME
    """
    from command_service import command_GETTIME
    command_GETTIME()


# -------------------------------------------------------------------------------------------------------------------
#                                        SETTIME
#
#                   Запрос на передачу профиля расходов коммерческого интервала.
# -------------------------------------------------------------------------------------------------------------------

parametrize_SETTIME = \
    [
        {
            'time_correct': -100,
        },
        {
            'time_correct': 100,
        },
        {
            'time_correct': 600,
        },
        {
            'time_correct': -600,
        },
        {
            'time_correct': 601,
        },
        {
            'time_correct': -601,
        },
    ]


@pytest.mark.parametrize("time_correct", parametrize(parametrize_SETTIME))
def test_SETTIME(time_correct):
    """
    Функция для прогона тестов для команды SETTIME

    """
    from command_service import command_SETTIME
    command_SETTIME(time_correct=int(time_correct))


# -------------------------------------------------------------------------------------------------------------------
#                                       GETSHPRM
#
#                     Получение основных параметров точки учета (счетчика).
# -------------------------------------------------------------------------------------------------------------------

def test_GETSHPRM():
    """
    Функция для прогона тестов для команды GETSHPRM

    """
    from command_GETSHPRM import command_GETSHPRM
    command_GETSHPRM()


# -------------------------------------------------------------------------------------------------------------------
#                                       GETPOK
#
#               Запрос расчетных показаний счетчика по указанным измерениям на указанное время.
# -------------------------------------------------------------------------------------------------------------------

parametrize_GETPOK = \
    [
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 1,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': False,
            'Am': False,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 5,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': False,
            'Rm': False,
            'count_timestamp': 10,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': False,
            'Am': True,
            'Rp': False,
            'Rm': True,
            'count_timestamp': 15,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': False,
            'Am': True,
            'Rp': True,
            'Rm': False,
            'count_timestamp': 25,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 48,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 48,
            'RecordTypeId': ['ElMonthEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 48,
            'RecordTypeId': ['ElDayEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 48,
            'RecordTypeId': ['ElMomentEnergy']
        },
        {
            'Ap': True,
            'Am': False,
            'Rp': True,
            'Rm': False,
            'count_timestamp': 5,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 48,
            'RecordTypeId': ['ElDayEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 5,
            'RecordTypeId': ['ElMomentEnergy', 'ElMonthEnergy']
        },
        {
            'Ap': True,
            'Am': True,
            'Rp': True,
            'Rm': True,
            'count_timestamp': 50,
            'RecordTypeId': ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy']
        },
    ]


@pytest.mark.parametrize("Ap, Am, Rp, Rm, count_timestamp, RecordTypeId", parametrize(parametrize_GETPOK))
def test_GETPOK(Ap, Am, Rp, Rm, count_timestamp, RecordTypeId):
    """
    Функция для прогона тестов для команды GETLP

    """
    from command_GETPOK import command_GETPOK
    command_GETPOK(Ap=bool(Ap), Am=bool(Am), Rp=bool(Rp), Rm=bool(Rm),
                   count_timestamp=int(count_timestamp), RecordTypeId=list(RecordTypeId))


# -------------------------------------------------------------------------------------------------------------------
#                                        GETTESTS
#
#                   Запрос на передачу профиля расходов коммерческого интервала.
# -------------------------------------------------------------------------------------------------------------------

parametrize_GETTESTS = [
    {
        'NumTests': 1,
    },
    {
        'NumTests': 2,
    },
    {
        'NumTests': 47,
    },
    {
        'NumTests': 48,
    },
]


@pytest.mark.parametrize("NumTests", parametrize(parametrize_GETTESTS))
def test_GETTESTS(NumTests):
    """
    Функция для прогона тестов для команды GETTESTS

    """
    from command_GETTESTS import command_GETTESTS
    command_GETTESTS(NumTests=int(NumTests))


# -------------------------------------------------------------------------------------------------------------------
#                                        GETLP
#
#                   Запрос на передачу профиля расходов коммерческого интервала.
# -------------------------------------------------------------------------------------------------------------------

parametrize_GETLP = [
    {
        'Qp': True,
        'Qm': True,
        'Pp': True,
        'Pm': True,
        'Kk': 10,
    },
    {
        'Qp': False,
        'Qm': True,
        'Pp': True,
        'Pm': True,
        'Kk': 1,
    },
    {
        'Qp': True,
        'Qm': False,
        'Pp': True,
        'Pm': True,
        'Kk': 1,
    },
    {
        'Qp': True,
        'Qm': True,
        'Pp': False,
        'Pm': True,
        'Kk': 1,
    },
    {
        'Qp': True,
        'Qm': True,
        'Pp': True,
        'Pm': False,
        'Kk': 1,
    },
    {
        'Qp': True,
        'Qm': True,
        'Pp': False,
        'Pm': False,
        'Kk': 49,
    },
    {
        'Qp': False,
        'Qm': False,
        'Pp': True,
        'Pm': True,
        'Kk': 100,
    },
]


@pytest.mark.parametrize("Qp, Qm, Pp, Pm, Kk", parametrize(parametrize_GETLP))
def test_GETLP(Qp, Qm, Pp, Pm, Kk):
    """
    Функция для прогона тестов для команды GETLP

    """
    from command_GETLP import command_GETLP
    command_GETLP(Qp=bool(Qp), Qm=bool(Qm), Pp=bool(Pp), Pm=bool(Pm), Kk=int(Kk))


# -------------------------------------------------------------------------------------------------------------------
#                                       GETAUTOREAD
#
#               Получение зафиксированных показаний счетчика ( показаний авточтения)
# -------------------------------------------------------------------------------------------------------------------
def test_GETAUTOREAD():
    print('ПОКА НЕ ГОТОВА')


# -------------------------------------------------------------------------------------------------------------------
#                                       GETMTRLOG
#
#                            Запрос журнала событий по счетчикам
# -------------------------------------------------------------------------------------------------------------------
parametrize_GETMTRLOG = \
    [
        {
            'RecordTypeId': ["ElJrnlPwr", "ElJrnlTimeCorr",
                             "ElJrnlReset", "ElJrnlOpen",
                             "ElJrnlPwrA", "ElJrnlPwrB", "ElJrnlPwrC"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlPwrC"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlPwrB"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlPwrA"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlOpen"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlReset"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlTimeCorr"],
            'count_timestamp': 11,
        },
        {
            'RecordTypeId': ["ElJrnlPwr"],
            'count_timestamp': 11,
        },
    ]


@pytest.mark.parametrize("RecordTypeId, count_timestamp", parametrize(parametrize_GETMTRLOG))
def test_GETMTRLOG(RecordTypeId, count_timestamp):
    """
    Функция для прогона тестов для команды GETMTRLOG

    """
    from command_GETMTRLOG import command_GETMTRLOG
    command_GETMTRLOG(RecordTypeId=list(RecordTypeId), count_timestamp=int(count_timestamp))
