# Здесь расположим класс коннекта
import socket
from Service.Config_Parser import ip_address, ip_port

address = (ip_address, ip_port)


# print('ip_address', ip_address, type(ip_address))
# print('ip_address', ip_port, type(ip_port))

class Connect:
    data = b''
    answer = None
    answer_dict = {}

    def __init__(self, data):
        self.data = b''
        self.answer = None
        self.answer_dict = {}

        self.data = data
        self.answer = self._setup()

    def _setup(self):
        # Создаем сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20)
        # Подключаемся по нужному адресу

        # print(address)
        sock.connect(address)

        # оправляем пакет
        # sock.sendall(self.data)
        # получаем пакет
        # sock.shutdown(socket.SHUT_WR)
        # немного ждем перед чтением всех данных. по возможности сделать умнее
        # time.sleep(1)
        answer_bytes = []
        # Успд не вседа отвечает сразу #Работает ?
        answer = {}
        # //----------------------------------------------------------------------------
        sock.sendall(self.data)

        while True:
            try:
                buffer = bytes
                buffer = sock.recv(1)
                # print(buffer)

                # print('buffer', buffer)
                answer_bytes.append(buffer)
            except:

                break

        # //----------------------------------------------------------------------------
        #         for i in range(3):
        #             buffer = sock.recv(1)
        #             print(buffer)
        #             # Сначала читаем первые 3 байта.
        #             # Первый байт - префикс
        #             # Префиксный байт (имеет значение 0х02)
        #             for _ in range(1):
        #                 temp_char = sock.recv(1)
        #                 answer['prefix_byte'] = temp_char
        #                 answer_bytes.append(temp_char)
        #
        #             # Второй и третий байт - это длина пакета.
        #             # Длина пакета без учета X,NN,KK - где X Префиксный байт , NN - Длина пакета ,КК - CRC – контрольная сумма
        #             buffer = []
        #             for _ in range(2):
        #                 temp_char = sock.recv(1)
        #                 answer_bytes.append(temp_char)
        #                 buffer.append(temp_char)
        #
        #             answer['len_packet'] = deepcopy(buffer)
        #             # for _ in range(3):
        #             #     temp_char = sock.recv(1)
        #             #     answer_bytes.append(temp_char)
        #             #     print(answer_bytes)
        #
        #             # ТЕПЕРЬ -  ВАЖНО - ПОЛУЧАЕМ ДЛИНУ САМОГО ПАКЕТА в человесческом виде
        #             # result_byte_str = b''
        #             # for _ in answer_bytes[1:]:
        #             #     result_byte_str += _
        #             # answer_length_without_crc = hex_to_dec(result_byte_str)
        #             len_data_value = b''
        #             for _ in answer['len_packet']:
        #                 len_data_value += _
        #
        #             # В ИТОГЕ ДЛИНА ПАКЕТА В 10 система:
        #             # длина пакета без контрольной суммы
        #             answer_length_without_crc = hex_to_dec(len_data_value)
        #             ##Длина тела пакета + 2 байта на crc
        #             # for _ in range(answer_length_without_crc + 2):
        #             #     temp_char = sock.recv(1)
        #             #     answer_bytes.append(temp_char)
        #             # Читаем данные - Полезная нагрузка
        #             buffer = []
        #             for _ in range(answer_length_without_crc):
        #                 temp_char = sock.recv(1)
        #                 answer_bytes.append(temp_char)
        #                 buffer.append(temp_char)
        #             answer['data'] = deepcopy(buffer)
        #
        #             # И теперь добавлдяем нашу контрольную сумму
        #             buffer = []
        #             for _ in range(2):
        #                 temp_char = sock.recv(1)
        #                 answer_bytes.append(temp_char)
        #                 buffer.append(temp_char)
        #             answer['crc'] = deepcopy(buffer)
        #
        #             if answer_bytes != []:
        #                 break
        #             elif answer_bytes == []:
        #                 print(str(i), 'try to get answer')
        #                 continue
        #             elif answer_bytes == [] and i == 3:
        #                 sock.close()
        #                 raise Exception("USPD didn't answer")
        #         sock.close()

        self.answer_dict = answer
        return answer_bytes
