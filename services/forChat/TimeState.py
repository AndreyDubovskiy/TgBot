import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller

class TimeState(UserState):
    async def start_msg(self):
        return Response(text="Введіть наступним повідомленням час затримки між повідомленнями під час розсилки (у секундах, стандартно 180 секунд (3 хв.)):", buttons=markups.generate_cancel())

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")

    async def next_msg(self, message: str):
        try:
            new = int(message)
            if new <= 0:
                return Response("Число повинно бути більшим за 0!", redirect="/time")
            else:
                config_controller.change_time_cooldown(new)
                return Response("Збережено!", redirect="/menu")
        except:
            Response("Щось пішло не так! Ви вірно вказали число?", redirect="/time")