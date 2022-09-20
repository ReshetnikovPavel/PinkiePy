class FimException(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message

    def __str__(self):
        return f'Error at line {self.token.line} column {self.token.column} ' \
               f'{self.token.value} : {self.message}'


class FimParserException(FimException):
    pass


class FimResolverException(FimException):
    pass


class FimRuntimeException(FimException):
    pass


class FimEnvironmentException(FimRuntimeException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class FimCSharpTranslatorException(FimException):
    pass
