import errno

from requests import exceptions


class PageLoaderError(Exception):
    error_number = errno.EPERM


class RequestError(PageLoaderError, exceptions.RequestException):
    pass


class HttpError(RequestError, exceptions.HTTPError):
    pass


class MissingSchema(RequestError, exceptions.MissingSchema):
    pass


class DestinationNotADirectoryError(PageLoaderError, NotADirectoryError):
    error_number = errno.ENOTDIR


class PermissionDenied(PageLoaderError, PermissionError):
    error_number = errno.EACCES
