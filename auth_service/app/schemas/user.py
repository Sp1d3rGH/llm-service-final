from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    """
    Схема пользователя, возвращаемая клиенту (без чувствительных полей).
    """
    id: int
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
