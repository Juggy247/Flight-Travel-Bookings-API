# constants.py

COMMON_RESPONSES = {
    400: {"description": "Bad request"},
    401: {"description": "Not authenticated"},
    403: {"description": "Forbidden"},
    404: {"description": "Resource not found"},
    409: {"description": "Conflict"},
    422: {"description": "Validation error"}
}