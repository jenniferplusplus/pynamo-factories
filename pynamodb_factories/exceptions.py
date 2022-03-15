class ModelError(Exception):
    """The given class is not a valid Pynamodb model and cannot be used to generate fakes"""
    pass


class UnsupportedException(Exception):
    """The attribute is not supported by pynamodb-factories, and cannot be faked"""
    pass


class RequiredArgumentError(Exception):
    """A required arguments was not included in the build kwargs"""
    pass
