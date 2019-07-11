"""
Копия из проекта с проверкой JSON
"""

import datetime

import requests
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.backends import default_backend


class JsonHelper:

    def __init__(self, testing_url):
        self.testing_url = testing_url
        self._cookie = self._authorization()
        self.datetime = datetime.datetime.now()

    def _authorization(self):
        json_text = '{"password":"admin","login":"admin"}'
        response = requests.post(self.testing_url+'auth', data=json_text)
        return response.cookies

    def _set_cookie(self,cookie):
        self._cookie = cookie

    def _set_datetime(self,datetime):
        self.datetime = datetime

    def get_cookie(self):
        previous_date = self.datetime
        difference_between_dates = datetime.datetime.now().minute - previous_date.minute
        if difference_between_dates >= 5 or self._cookie is None:  # Обновление cookie
            print('re-write cookie')
            cookie = self._authorization()
            self._set_cookie(cookie)
            self._set_datetime(datetime.datetime.now())
        return self._cookie

    @staticmethod
    def get_current_formated_date_str():
        curr_date = datetime.datetime.now()
        curr_date_str = datetime.datetime.strftime(curr_date, '%Y-%m-%dT%H:%M:%S+03:00') # +03:00 время локальное
        return curr_date_str

    # @staticmethod
    # def generate_rsa_key():
    #     key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537,
    #                                    key_size=2048)
    #     pem = key.private_bytes(encoding=serialization.Encoding.PEM,
    #                             format=serialization.PrivateFormat.TraditionalOpenSSL,
    #                             encryption_algorithm=serialization.NoEncryption())
    #     return pem

