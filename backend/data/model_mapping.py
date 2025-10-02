from .models import User, Category, Content, Question, InteractionEvent, Rating

MODEL_MAP = {
    User.__tablename__: User,
    Category.__tablename__: Category,
    Content.__tablename__: Content,
    Question.__tablename__: Question,
    InteractionEvent.__tablename__: InteractionEvent,
    Rating.__tablename__: Rating,
}
