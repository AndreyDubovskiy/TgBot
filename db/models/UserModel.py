from db.models.BaseModel import BaseModel
from db.models.imports import *

class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(255))
    valid_phone: Mapped[str] = mapped_column(String(255))


    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone
