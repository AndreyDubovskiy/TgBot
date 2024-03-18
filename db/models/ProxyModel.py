from db.models.BaseModel import BaseModel
from db.models.imports import *

class ProxyModel(BaseModel):
    __tablename__ = 'proxys'

    id: Mapped[int] = mapped_column(primary_key=True)
    ip: Mapped[str] = mapped_column(String(255))
    port: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    type_proxy: Mapped[int] = mapped_column(Integer())


    def __init__(self, ip: str, port: str, login: str, password: str, type_proxy: int):
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.type_proxy = type_proxy
