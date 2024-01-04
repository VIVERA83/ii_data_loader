from base.base_exception import ExceptionBase


class YandexDiskException(ExceptionBase):
    args = ("Unknown error",)


class YaTokenNotValidException(YandexDiskException):
    args = ("The Yandex disk token failed verification, update token.",)
