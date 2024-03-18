from telebot.async_telebot import AsyncTeleBot
from telebot import types
from services.forChat.UserState import UserState
from services.forChat.StartState import StartState
from services.forChat.LogState import LogState
from services.forChat.MenuState import MenuState
from services.forChat.PostState import PostState
from services.forChat.TgAccState import TgAccState
from services.forChat.ParserState import ParserState
from services.forChat.ParserTGState import ParserTGState
from services.forChat.TimeState import TimeState
from services.forChat.ParseChatsState import ParseChatsState
from services.forChat.GenerateExelState import GenerateExelState
from services.forChat.EditNameUsersState import EditNameUsersState
from services.forChat.ProxyState import ProxyState

class BuilderState:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def create_state(self, data_txt: str, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str = None) -> UserState:
        clssses = {
            "/start": StartState,
            "/menu": MenuState,
            "/postlist": PostState,
            "/log": LogState,
            "/tgacc": TgAccState,
            "/parse": ParserState,
            "/parsetg": ParserTGState,
            "/time": TimeState,
            "/parsechats": ParseChatsState,
            "/exel": GenerateExelState,
            "/exelinput": EditNameUsersState,
            "/proxys": ProxyState,
        }
        return clssses[data_txt](user_id, user_chat_id, bot, user_name)