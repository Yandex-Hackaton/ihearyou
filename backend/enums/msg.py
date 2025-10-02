import enum


@enum.unique
class AnswerChoices(enum.Enum):
    HELPFUL = 'Helpful'
    NOT_HELPFUL = 'Not helpful'
    NO_RATING = 'No rating'


@enum.unique
class AuthAdmin(enum.Enum):
    LOGOUT = 'Admin logout'
    LOGIN_FAILED = 'Admin login failed'
    LOGIN_SUCCESSFUL = 'Admin login successful'
    AUTH_FAILED = 'Admin authentication failed'
