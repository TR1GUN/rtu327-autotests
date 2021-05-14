from copy import deepcopy
from Service.Connect import Connect


class Setup:
    """
    Основной класс запуска
    """

    command = b''
    answer = None
    error = []

    def __init__(self, command):
        self.command = b''
        self.answer = None
        self.command = command
        self.error = []
        # Запускаем
        self.answer = self._setup()



    def _setup(self):
        """Функция самого запуска , чо"""

        # Получаем команду
        command = deepcopy(self.command)

        sending_receiving = Connect(data=command)

        answer = deepcopy(sending_receiving.answer)
        # answer_dict = deepcopy(sending_receiving.answer_dict)

        # print(answer)
        # # теперь - парсим и вынимаем сам ответ
        # answer = _parsed_answer(answer_bytes=answer)

        # ДЕКОДИРУЕМ
        from Service.CheckUp_Structure_Answer import CheckUpStructureAnswer

        CheckUpStructureAnswer = CheckUpStructureAnswer(answer)

        self.error = CheckUpStructureAnswer.error
        if len(self.error) > 0:
            # ЛОГИРУЕМ ОШИБКУ
            print(self.error)
            # И ПРЕКРАЩАЕМ РАБОТУ
            assert self.error == [],'\n ОШИБКА ПРИ ПОЛУЧЕНИИ ПАКЕТА : \n' + str(self.error)
        else:
            answer = CheckUpStructureAnswer.Answer_STR

            self._error_handler(answer)
        return answer

    def _error_handler(self, answer):
        # переопределяем
        error_code_list = deepcopy(answer['result_code'])

        # Вытаскивваем все значения
        error_code = ''
        for i in range(len(error_code_list)):
            error_code = error_code + error_code_list[i]
        # Теперь получаем значения INT
        error_code = int(error_code, 16)

        from Service.Constant_Value_Bank import error_code_dict
        assert 0 == error_code, ' ОШИБКА В РЕЗУЛЬТАТЕ \n' + 'Значение :\n' + str(error_code) + \
                                 '\nРасшифровка :\n' + str(error_code_dict.get(error_code))



