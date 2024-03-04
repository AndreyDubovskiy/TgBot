from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

class StartState(UserState):
    async def start_msg(self):
        return Response(text="Для доступу до меню введіть /menu", is_end=True)