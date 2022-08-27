import re


def separate_array_name(string):
    return re.sub(r'\s+\d+$', '', string)


def separate_index(string):
    m = re.search(r'\d+$', string)
    return int(m.group()) if m else None


def is_float_and_int(obj):
    return type(obj) == float and int(obj) == float(obj) \
           or isinstance(obj, int) and not isinstance(obj, bool)


class FimException(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
    def __str__(self):
        return f'Error at line {self.token.line} column {self.token.column} ' \
               f'{self.token.value} : {self.message}'
