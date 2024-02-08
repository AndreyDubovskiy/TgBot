import datetime

from sqlalchemy import create_engine
from db.models.BaseModel import BaseModel
from db.models.UserModel import UserModel
from db.models.UserVerifyModel import UserVerifyModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

engine = create_engine("sqlite:///mainbase.db", echo=False)

BaseModel.metadata.create_all(engine)


def get_all_users():
    with Session(engine) as session:
        query = select(UserModel)
        res: List[UserModel] = session.scalars(query).all()
    return res

def get_all_verify_users():
    with Session(engine) as session:
        query = select(UserVerifyModel)
        res: List[UserVerifyModel] = session.scalars(query).all()
    return res


def create_verify_user(name, phone, tg_id, tg_name):
    with Session(engine) as session:
        user = UserVerifyModel(name, phone, tg_id, tg_name)
        session.add(user)
        session.commit()

def create_user(name, phone):
    with Session(engine) as session:
        user = UserModel(name, phone)
        session.add(user)
        session.commit()

# def get_user(user_name=None, user_tg_id=None, user_id=None):
#     with Session(engine) as session:
#         query = select(UserModel)
#         if user_name:
#             query = query.where(UserModel.tg_name==user_name)
#         if user_tg_id:
#             query = query.where(UserModel.tg_id==user_tg_id)
#         if user_id:
#             query = query.where(UserModel.id==user_id)
#
#         res: UserModel = session.scalar(query)
#
#     return res
