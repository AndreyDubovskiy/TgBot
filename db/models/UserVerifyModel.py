from db.models.BaseModel import BaseModel
from db.models.imports import *

class UserVerifyModel(BaseModel):
    __tablename__ = 'usersverify'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(255))
    tg_id: Mapped[str] = mapped_column(String(255))
    tg_name: Mapped[str] = mapped_column(String(255))
    count: Mapped[int] = mapped_column(Integer())
    name_k: Mapped[str] = mapped_column(String(255), nullable=True)


    def __init__(self,name: str, phone: str, tg_id: str, tg_name: str, name_k:str = None):
        self.tg_id = tg_id
        self.tg_name = tg_name
        self.name = name
        self.phone = phone
        self.count = 0
        self.name_k = name_k

    def __repr__(self):
        return f"<UserModel(id={self.id}, tg_id={self.tg_id}, tg_name={self.tg_name})>"