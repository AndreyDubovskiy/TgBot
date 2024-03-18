import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller
from telethon import TelegramClient

class TgAccState(UserState):
    async def start_msg(self):
        self.is_current = False
        self.api_id = "24209092"
        self.api_hash = "822ed15f01ee35ae8a50d750d3e8451d"
        self.current_page_acc = 0
        self.max_on_page = 10
        return Response(text="Список акаунтів:", buttons=markups.generate_tg_acc_menu(with_add=True, with_ready=False))

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.is_current:
                return Response(redirect="/tgacc")
            return Response(redirect="/menu")
        elif data_btn == "/accnext":
            if len(config_controller.LIST_TG_ACC)-((self.current_page_acc+1)*self.max_on_page) > 0:
                self.current_page_acc+=1
            return Response(text="Список акаунтів:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_add=True, with_ready=False))
        elif data_btn =="/accprev":
            if self.current_page_acc > 0:
                self.current_page_acc-=1
            return Response(text="Список акаунтів:", buttons=markups.generate_tg_acc_menu(self.current_page_acc*self.max_on_page, self.max_on_page, with_add=True, with_ready=False))
        elif data_btn in config_controller.LIST_TG_ACC:
            self.is_current = True
            self.current_session = data_btn
            return Response(text="Акаунт: " + self.current_session + "\nТелефон: "+ config_controller.LIST_TG_ACC[self.current_session]['phone'] +"\nПроксі: " + str(config_controller.LIST_TG_ACC[self.current_session].get("proxy", None)), buttons=markups.generate_tg_acc_semimenu())
        elif data_btn == "/add":
            self.edit = "session_name"
            return Response(text="Введіть наступним повідомленням назву акаунта (для себе, бажано латинськими літерами):", buttons=markups.generate_cancel())
        elif data_btn == "/delete":
            config_controller.del_tg_acc(self.current_session)
            return Response(text="Видалено!", redirect="/tgacc")



    async def next_msg(self, message: str):
        if self.edit == "session_name":
            self.session_name = message
            self.edit = "session_phone"
            return Response(text="Введіть наступним повідомленням номер телефону бота у форматі +380661231212:", buttons=markups.generate_cancel())
        elif self.edit == "session_phone":
            self.session_phone = message
            config_controller.add_or_edit_tg_acc(self.session_name, self.api_id, self.api_hash, self.session_phone)
            self.edit = "session_password"
            return Response(text="Введіть наступним повідомленням пароль до акаунту (якщо його немає, поставте крапку):",
                            buttons=markups.generate_cancel())
        elif self.edit == "session_password":
            if message != ".":
                self.password = message
                config_controller.add_or_edit_tg_acc(self.session_name, self.api_id, self.api_hash, self.session_phone, password=self.password)
            else:
                config_controller.add_or_edit_tg_acc(self.session_name, self.api_id, self.api_hash, self.session_phone)
            return Response(text="Акаунт збережено!\nМожливо при запуску запросити код, який прийде на акаунт", redirect="/tgacc")
