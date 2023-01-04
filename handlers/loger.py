import os
import datetime


class Loger():
    def __init__(self) -> None:
        # Созданиме папки для логов
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Дата время и имя файла
        self._date = str(datetime.datetime.now().today().replace(microsecond=0)).replace(':', '.')
        self._file_name = self._date

    # Передача типа лога в записть
    def info(self, text: str):
        ''' Записать лог - [INFO][DATE] Log text. '''
        self._write_log(str(f'[INFO][{self._date}] {text} \n'))

    def error(self, text: str):
        ''' Записать лог - [ERROR][DATE] Log text. '''
        self._write_log(str(f'[ERROR][{self._date}] {text} \n'))

    def debug(self, text: str):
        ''' Записать лог - [DEBUG][DATE] Log text. '''
        self._write_log(str(f'[DEBUG][{self._date}] {text} \n'))

    # Записть лога в файл
    def _write_log(self, log: str):
        with open(f'logs/{self._file_name}.txt', 'a') as log_file:
            log_file.write(log)
