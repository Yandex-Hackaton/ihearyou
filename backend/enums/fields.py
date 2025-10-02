import enum


class Length(enum.Enum):
    TITLE_FIELD = 48
    PASSWORD_FIELD = 128
    TEXT_FIELD = 512
    URL_LINK_FIELD = 512


@enum.unique
class ViewLimits(enum.Enum):
    TEXT_FIELD = 50


@enum.unique
class InitValue(enum.Enum):
    DEFAULT_START_VALUE = 0


@enum.unique
class Formats(enum.Enum):
    DATETIME = "%d.%m.%Y %H:%M"
