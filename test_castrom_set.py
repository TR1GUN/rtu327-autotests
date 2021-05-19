# from Service.Setup import Setup
# from Service.Former_Command import FormCommand
# from Service.Constructor_Answer import Constructor_Answer
# from Service.Service_function import total_assert, assert_answer_data
# from copy import deepcopy
#
#
#
# # -------------------------------------------------------------------------------------------------------------------
# #                                       GETMTRLOG
# #
# #                            Запрос журнала событий по счетчикам
# # -------------------------------------------------------------------------------------------------------------------
# def test_GETMTRLOG(count_journal: int = 5, RecordTypeId: str = ['ElJrnlPwr', 'ElJrnlTimeCorr']):
#     """
#     Получение значений ЖУРНАЛОВ
#
#     Крайне важная штука
#
#     НЕОБХОДИМО ЗАДАТЬ ОДИН ЖУРНАЛ
#     """
#     import struct
#     # Определяем тип команды
#     type_command = 'GETMTRLOG'
#     Итак - Первое что делаем
#
#     ["ElJrnlPwr", "ElJrnlTimeCorr", "ElJrnlReset", "ElJrnlOpen", "ElJrnlPwrA", "ElJrnlPwrB", "ElJrnlPwrC"]
#
#     Kk = count_timestamp
#
#     # assert ('ElMomentEnergy' in RecordTypeId) or ('ElDayEnergy' in RecordTypeId) or ('ElMonthEnergy' in RecordTypeId), \
#     #     'НЕ ВЕРНО ЗАДАН ТИП ДАННЫХ '
#     # Первое что делаем - генерируем необходимые нам данные
#     from Service.Generator_Data import GenerateGETMTRLOG
#
#     ElectricEnergyValues = GenerateGETMTRLOG(Count_timestamp=count_timestamp, RecordTypeId=RecordTypeId)
#     # получаем данные
#     Generate_data_dict = deepcopy(ElectricEnergyValues.GETMTRLOG)
#     Serial = deepcopy(ElectricEnergyValues.Serial)
#
#     # Формируем команду
#     from Service.Service_function import get_form_NSH, decode_data_to_GETPOK, code_data_to_GETPOK
#
#     # ---------- ФОРМИРУЕМ ДАННЫЕ ДЛЯ КОМАНДЫ ЗАПРОСА ----------
#     # БЕРЕМ ТАЙМШТАМП
#     Timestamp = 0
#     for i in Generate_data_dict:
#         Timestamp = Generate_data_dict[i].get('Timestamp')
#     print('Timestamp --->', Timestamp)
#
#     # NSH Номер счетчика BCD5
#     NSH = get_form_NSH(Serial=Serial)
#
#     # Запросить события с отметками времени  больше Tstart TIME_T
#     Tstart = int(Timestamp).to_bytes(length=4, byteorder='little')
#
#     # Максимальное кол-во запрашиваемых событий INT16
#     Cnt = int(Kk).to_bytes(length=2, byteorder='little',signed=True)
#     # ---------- ФОРМИРУЕМ КОМАНДУ ----------
#     data_request = NSH + Tstart + Cnt
#     command = FormCommand(type_command=type_command, data=data_request).command
#
#     # ---------- ФОРМИРУЕМ ПРЕДПОЛАГАЕМЫЙ ОТВЕТ ----------
#     # answer_data_expected = {
#     #     'Rm': None,
#     #     'Rp': None,
#     #     'Am': None,
#     #     'Ap': None,
#     # }
#     # if Rm:
#     #     answer_data_expected['Rm'] = Generate_data_SHPRM_dict.get(Timestamp).get('Rm')
#     # if Rp:
#     #     answer_data_expected['Rp'] = Generate_data_SHPRM_dict.get(Timestamp).get('Rp')
#     # if Am:
#     #     answer_data_expected['Am'] = Generate_data_SHPRM_dict.get(Timestamp).get('Am')
#     # if Ap:
#     #     answer_data_expected['Ap'] = Generate_data_SHPRM_dict.get(Timestamp).get('Ap')
#     # # Формируем байтовую строку нагрузочных байтов
#     # data = code_data_to_GETPOK(answer_data_expected)
#     # # Формируем предполагаемый ответ
#     # Answer_expected = Constructor_Answer(data)
#     # ---------- ОТПРАВЛЯЕМ КОМАНДУ ----------
#     Answer = Setup(command=command).answer
#
#     # ---------- ТЕПЕРЬ ДЕКОДИРУЕМ ДАННЫЕ ОТВЕТА ----------
#     #
#     # # ДЕКОДИРУЕМ ПОЛЕ ДАТА
#     # Answer['answer_data'] = decode_data_to_GETPOK(answer_data=Answer['answer_data'],
#     #                                               Chnl={"Rm": Rm, "Rp": Rp, "Am": Am, "Ap": Ap, })
#     # # БЕРЕМ ДАННЫЕ В НОРМАЛЬНОМ ВИДЕ
#     # Answer_expected['answer_data'] = answer_data_expected
#     #
#     # # ------------------->
#     # print(Answer_expected['answer_data'])
#     # print(Answer['answer_data'])
#     # # ------------------->
#     #
#     # # ТЕПЕРЬ СРАВНИВАЕМ НАШИ ДАННЫЕ - ЦЕ ВАЖНО
#     # assert_answer_data(answer_data_expected=Answer_expected['answer_data'], answer_data=Answer['answer_data'])
#     #
#     # # ТЕПЕРЬ ПРОВОДИМ ТОТАЛЬНОЕ СРАВНИВАНИЕ
#     # total_assert(answer_uspd=Answer, answer_normal=Answer_expected)
#
#
#
# # test_GETPOK(count_timestamp=[6], Ap=True, Am=True, Rp=True, Rm=True, RecordTypeId = ['ElMomentEnergy', 'ElDayEnergy', 'ElMonthEnergy'])
#
# test_GETMTRLOG()
#
# # lol = {1620964800: {'Id': 8, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620964800}, 1620968400: {'Id': 9, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620968400}, 1620972000: {'Id': 10, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620972000}, 1620975600: {'Id': 11, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620975600}, 1620979200: {'Id': 12, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620979200}, 1620982800: {'Id': 13, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620982800}, 1620986400: {'Id': 14, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620986400}, 1620990000: {'Id': 15, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620990000}, 1620993600: {'Id': 16, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620993600}, 1620997200: {'Id': 17, 'cTime': 60, 'Pp': 1.0, 'Pm': 2.0, 'Qp': 3.0, 'Qm': 4.0, 'isPart': 1, 'isOvfl': 1, 'isSummer': 1, 'DeviceIdx': 6, 'Timestamp': 1620997200}}
# #
# # lol_2 = sorted(lol.keys())
# #
# # print(lol)
# # print(lol_2)
#
# #
# # print(min(lol.keys()))
# #
# # Timestamp_list = []
# # for i in lol:
# #     Timestamp_list.append(lol[i].get('Timestamp'))
# # Timestamp = min(Timestamp_list)
# #
# # print(Timestamp)