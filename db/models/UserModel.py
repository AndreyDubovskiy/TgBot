from db.models.BaseModel import BaseModel
from db.models.imports import *

class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(255))


    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return f"<UserModel(id={self.id}, tg_id={self.tg_id}, tg_name={self.tg_name})>"