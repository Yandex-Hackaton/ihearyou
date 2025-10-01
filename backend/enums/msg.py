import enum


@enum.unique
class AnswerChoices(enum.Enum):
    HELPFUL = "Helpful"
    NOT_HELPFUL = "Not helpful"
    NO_RATING = "No rating"
