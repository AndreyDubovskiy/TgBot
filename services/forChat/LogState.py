import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

class LogState(UserState):
    async def start_msg(self):
        return Response(text="Введіть пароль для доступу:", buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        if config_controller.log(self.user_id, message):
            return Response(text="Пароль прийнято!", is_end=True, redirect="/menu")
        else:
            return Response(text="Невірний пароль!\nВведіть ще раз:", buttons=markups.generate_cancel())

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return None