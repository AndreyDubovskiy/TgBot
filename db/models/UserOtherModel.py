from db.models.BaseModel import BaseModel
from db.models.imports import *

class UserOtherModel(BaseModel):
    __tablename__ = 'usersother'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    tg_id: Mapped[str] = mapped_column(String(255))
    tg_name: Mapped[str] = mapped_column(String(255))
    count: Mapped[int] = mapped_column(Integer())
    fromchanel: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=True)


    def __init__(self,name: str, tg_id: str, tg_name: str, fromchanel: str = None, phone: str = None):
        self.tg_id = tg_id
        self.tg_name = tg_name
        self.name = name
        self.count = 0
        self.fromchanel = fromchanel
        self.phone = phone

    def __repr__(self):
        return f"<UserModel(id={self.id}, tg_id={self.tg_id}, tg_name={self.tg_name})>"