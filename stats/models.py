from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class ClickEvent(SQLModel, table=True):
    """Событие нажания кнопки в Telegram боте."""

    id: int | None = Field(default=None, primary_key=True)
    # На текущий момент нету моделей пользователя и кнопок.
    # user_id: int = Field(
    #     foreign_key="user.id",
    # )
    # user: "User" = Relationship(
    #     description="Объект пользователя",
    #     back_populates="clicks_stat",
    # )
    # button_id: int = Field(
    #     description="FK к записи представляющей кнопку",
    #     foreign_key="button.id",
    # )
    # button: "Button" = Relationship(back_populates="clicks_stat")
    callback_data: str = Field(description="callback_data кнопки от Telegram")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Когда была нажата кнопка",
    )
