class DataValidationError(Exception):
    pass

class MissingFieldError(DataValidationError):
    pass
