import errno


class PageLoaderError(Exception):
    error_number = errno.EPERM


class HttpError(PageLoaderError):
    pass


class MissingSchema(PageLoaderError):
    pass


class RequestError(PageLoaderError):
    pass


class DestinationNotADirectoryError(PageLoaderError):
    error_number = errno.ENOTDIR


class PermissionDenied(PageLoaderError):
    error_number = errno.EACCES
