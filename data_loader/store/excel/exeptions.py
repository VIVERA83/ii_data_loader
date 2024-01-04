class ExceptionExcel(Exception):
    """Класс исключения при работе с файлом excel"""

    args = "Excel file error"

    def __init__(self, *args):
        if args:
            self.args = args

    def __str__(self):
        return f"Ошибка: {self.args[0]}"


class ExceptionExcelFormat(ExceptionExcel):
    args = (
        "The excel file format is incorrect, the table is expected to consist of three columns",
    )
