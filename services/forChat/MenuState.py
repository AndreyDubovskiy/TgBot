import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

class MenuState(UserState):
    async def start_msg(self):
        if self.user_id in config_controller.list_is_loggin_admins:
            return Response(text="Меню", buttons=markups.generate_markup_menu(), is_end=True)
        else:
            return Response(text="Для початку роботи, введіть пароль", is_end=True, redirect="/log")