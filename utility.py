import re


def separate_array_name(string):
    return re.sub(r'\s+\d+$', '', string)


def separate_index(string):
    m = re.search(r'\d+$', string)
    return int(m.group()) if m else None


def is_float_and_int(obj):
    return type(obj) == float and int(obj) == float(obj) \
           or isinstance(obj, int) and not isinstance(obj, bool)