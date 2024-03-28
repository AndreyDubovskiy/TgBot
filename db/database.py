import datetime

from sqlalchemy import create_engine
from db.models.BaseModel import BaseModel
from db.models.UserModel import UserModel
from db.models.UserVerifyModel import UserVerifyModel
from db.models.UserOtherModel import UserOtherModel
from db.models.ProxyModel import ProxyModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from typing import List
import services.testing.PhoneNumber as pn

engine = create_engine("sqlite:///mainbase.db", echo=False)

BaseModel.metadata.create_all(engine)

def get_all_proxy():
    with Session(engine) as session:
        query = select(ProxyModel)
        res: List[ProxyModel] = session.scalars(query).all()
    return res
def get_proxy_by_ip_port(ip:str, port:str):
    with Session(engine) as session:
        query = select(ProxyModel).where(ProxyModel.ip == ip).where(ProxyModel.port == port)
        res: List[ProxyModel] = session.scalars(query).all()
    return res

def get_ipport_proxys_list():
    list_proxy = get_all_proxy()
    list_names = []
    for proxy in list_proxy:
        list_names.append(proxy.ip+":"+proxy.port)
    return list_names
def is_proxy(ip:str, port:str):
    tmp = get_proxy_by_ip_port(ip, port)
    return len(tmp) != 0

def delete_proxy(ip:str, port:str):
    tmp = get_proxy_by_ip_port(ip, port)
    if len(tmp) == 0:
        return False
    with Session(engine) as session:
        query = select(ProxyModel).where(ProxyModel.ip == ip).where(ProxyModel.port == port)
        proxy: ProxyModel = session.scalars(query).first()
        session.delete(proxy)
        session.commit()
    return True
def create_proxy(ip:str, port:str, login:str, password:str, type_proxy: int):
    tmp = get_proxy_by_ip_port(ip, port)
    if len(tmp) != 0:
        return

    with Session(engine) as session:
        proxy = ProxyModel(ip, port, login, password, type_proxy)
        session.add(proxy)
        session.commit()
    return


def add_count_by_tg_id(tg_id: str):
    with Session(engine) as session:
        query = select(UserVerifyModel).where(UserVerifyModel.tg_id == tg_id)
        res: List[UserVerifyModel] = session.scalars(query).all()
        if len(res) != 0:
            res[0].count = res[0].count + 1
            session.add(res[0])
            session.commit()
            return res[0].count
        else:
            return 0

def add_count_otheruser_by_tg_id(tg_id: str):
    with Session(engine) as session:
        query = select(UserOtherModel).where(UserOtherModel.tg_id == tg_id)
        res: List[UserOtherModel] = session.scalars(query).all()
        if len(res) != 0:
            res[0].count = res[0].count + 1
            session.add(res[0])
            session.commit()
            return res[0].count
        else:
            return 0

def get_user_verify_order(is_name_k = False):
    with Session(engine) as session:
        if not is_name_k:
            query = select(UserVerifyModel).order_by(UserVerifyModel.count)
        else:
            query = select(UserVerifyModel).where(UserOtherModel.name_k != None).order_by(UserVerifyModel.count)
        res: List[UserVerifyModel] = session.scalars(query).all()
    return res

def get_user_other_order(is_name_k = False):
    with Session(engine) as session:
        if not is_name_k:
            query = select(UserOtherModel).order_by(UserOtherModel.count)
        else:
            query = select(UserOtherModel).where(UserOtherModel.name_k != None).order_by(UserOtherModel.count)
        res: List[UserOtherModel] = session.scalars(query).all()
    return res

def get_user_other_order_by_chats(chat: str, is_name_k = False):
    with Session(engine) as session:
        if not is_name_k:
            query = select(UserOtherModel).where(UserOtherModel.fromchanel == chat).order_by(UserOtherModel.count)
        else:
            query = select(UserOtherModel).where(UserOtherModel.fromchanel == chat).where(UserOtherModel.name_k != None).order_by(UserOtherModel.count)
        res: List[UserOtherModel] = session.scalars(query).all()
    return res


def get_all_users():
    with Session(engine) as session:
        query = select(UserModel)
        res: List[UserModel] = session.scalars(query).all()
    return res

def get_user_by_phone(phone: str):
    with Session(engine) as session:
        query = select(UserModel).where(UserModel.phone == phone)
        res: List[UserModel] = session.scalars(query).all()
    return res

def get_userother_by_name_tg(tg_name: str):
    with Session(engine) as session:
        query = select(UserOtherModel).where(UserOtherModel.tg_name == tg_name)
        res: List[UserOtherModel] = session.scalars(query).all()
    return res

def get_userother_by_id_tg(id_tg: str):
    with Session(engine) as session:
        query = select(UserOtherModel).where(UserOtherModel.tg_id == id_tg)
        res: List[UserOtherModel] = session.scalars(query).all()
    return res

def get_user_verify_by_phone(phone_verify: str):
    with Session(engine) as session:
        query = select(UserVerifyModel).where(UserVerifyModel.phone == phone_verify)
        res: List[UserVerifyModel] = session.scalars(query).all()
    return res

def get_user_verify_by_tg_id(tg_id: str):
    with Session(engine) as session:
        query = select(UserVerifyModel).where(UserVerifyModel.tg_id == tg_id)
        res: List[UserVerifyModel] = session.scalars(query).all()
    return res

def is_in_user_verify(phone_verify: str):
    tmp = get_user_verify_by_phone(phone_verify)
    return len(tmp) != 0

def is_in_user(phone: str):
    tmp = get_user_by_phone(phone)
    return len(tmp) != 0

def is_in_userother(tg_id: str):
    tmp = get_userother_by_id_tg(tg_id)
    return len(tmp) != 0

def get_all_verify_users():
    with Session(engine) as session:
        query = select(UserVerifyModel)
        res: List[UserVerifyModel] = session.scalars(query).all()
    return res

def session_commit(obj):
    with Session(engine) as session:
        session.add(obj)
        session.commit()
    return


def create_verify_user(name, phone, tg_id, tg_name):
    tmp = get_user_verify_by_phone(phone)
    if len(tmp) != 0:
        return

    with Session(engine) as session:
        user = UserVerifyModel(name, phone, tg_id, str(tg_name))
        session.add(user)
        session.commit()
    return


def create_user(name, phone):

    tmp = get_user_by_phone(phone)
    if len(tmp) != 0:
        return

    with Session(engine) as session:
        user = UserModel(name, phone)
        tmp = pn.str_to_phone_list(phone)
        if len(tmp) != 0:
            user.valid_phone = ",".join(tmp)
            session.add(user)
            session.commit()
    return

def delete_userother_by_tg_id(tg_id: str):
    tmp = get_userother_by_id_tg(tg_id)
    if len(tmp) == 0:
        return False
    with Session(engine) as session:
        query = select(UserOtherModel).where(UserOtherModel.tg_id == tg_id)
        user: UserOtherModel = session.scalars(query).first()
        session.delete(user)
        session.commit()
    return True


def create_other_user(name, tg_id, tg_name, fromchanel, phone = None):
    tmp = get_userother_by_id_tg(tg_id)
    tmp1 = get_user_verify_by_tg_id(tg_id)
    if len(tmp) != 0 or len(tmp1) != 0:
        return

    with Session(engine) as session:
        user = UserOtherModel(name, tg_id, str(tg_name), fromchanel, phone)
        session.add(user)
        session.commit()
    return

def get_other_user_chats():
    with Session(engine) as session:
        query = select(UserOtherModel.fromchanel, func.count(UserOtherModel.id)).group_by(UserOtherModel.fromchanel)
        res = session.scalars(query).all()
    return res
def get_other_user_chats_with_len(by_chat):
    users = get_user_other_order_by_chats(by_chat)
    with Session(engine) as session:
        query = select(UserOtherModel).where(UserOtherModel.fromchanel == by_chat).where(UserOtherModel.name_k != None)
        tmp: List[UserOtherModel] = session.scalars(query).all()
    return len(users), len(tmp)

def count_to_new_user_other_by_chat(chat:str, is_name_k:bool = False):
    users = get_user_other_order_by_chats(chat, is_name_k)
    if len(users) > 0:
        max_count = users[-1].count
        with Session(engine) as session:
            if not is_name_k:
                query = select(UserOtherModel).where(UserOtherModel.fromchanel == chat).where(UserOtherModel.count < max_count)
            else:
                query = select(UserOtherModel).where(UserOtherModel.fromchanel == chat).where(UserOtherModel.name_k != None).where(UserOtherModel.count < max_count)
            res = session.scalars(query).all()
        if len(res) == 0:
            return len(users)
        else:
            return len(res)
    else:
        return 0


def count_to_new_user_other(is_name_k:bool = False):
    users = get_user_other_order(is_name_k)
    if len(users) > 0:
        max_count = users[-1].count
        with Session(engine) as session:
            if not is_name_k:
                query = select(UserOtherModel).where(UserOtherModel.count < max_count)
            else:
                query = select(UserOtherModel).where(UserOtherModel.name_k != None).where(UserOtherModel.count < max_count)
            res = session.scalars(query).all()
        if len(res) == 0:
            return len(users)
        else:
            return len(res)
    else:
        return 0

def count_to_new_verify_user_by_chat(is_name_k:bool = False):
    users = get_user_verify_order(is_name_k)
    if len(users) > 0:
        max_count = users[-1].count
        with Session(engine) as session:
            if not is_name_k:
                query = select(UserVerifyModel).where(UserVerifyModel.count < max_count)
            else:
                query = select(UserVerifyModel).where(UserVerifyModel.name_k != None).where(UserVerifyModel.count < max_count)
            res = session.scalars(query).all()
        if len(res) == 0:
            return len(users)
        else:
            return len(res)
    else:
        return 0