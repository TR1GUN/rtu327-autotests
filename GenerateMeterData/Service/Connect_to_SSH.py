# Здесь сделаем коннект по SSH


class ConnectSSH:
    client = None

    def __init__(self):
        self.client = None
        import paramiko

        # Создаем клиент
        self.client = paramiko.SSHClient()

        # Настравиваем сессию
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Берем настройки подключения
        from GenerateMeterData import user_login, user_password, IP_address ,IP_port
        # Делаем подкючение к нужному серверу
        # print('user_login', user_login, type(user_login))
        # print('user_password', user_password, type(user_password))
        # print('addres_ssh', addres_ssh, type(addres_ssh))
        # Конектимся

        self.client.connect(hostname=str(IP_address), port=int(IP_port),
                                username=str(user_login), password=str(user_password),
                                look_for_keys=False, allow_agent=False, )


    def Exec_command_return_result(self, cmd):

        # Отправляем нашу команду
        stdin, stdout, stderr = self.client.exec_command(cmd , timeout = 10)

        # Читаем лог вывода
        data_stdout = stdout.read()
        data_stderr = stderr.read()


        # Если есть ошибки то возвращаем ошибки
        if len(data_stderr.decode('utf-8')) > 0:
            result = data_stderr.decode('utf-8')
        else:
            # если нет никаких ошибок , то возвращаем
            result = data_stdout.decode('utf-8')
        return result

    def Exec_command(self, cmd):

        # Отправляем нашу команду
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout = 10)

        # НИЧЕГО НЕ ВОЗВРАЩАЕМ

    def Terminal(self, cmd):
        # Делаем реал тайм подключение
        ssh = self.client.invoke_shell()
        # Пускаем команду
        ssh.send(cmd)
        from time import sleep

        sleep(1)
        # # Получаем ответ
        # answer = ssh.recv(3000)
        #
        # answer = answer.decode('utf-8')
        # return answer

    def close(self):
        self.client.close()
