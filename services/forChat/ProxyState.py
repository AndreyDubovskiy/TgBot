import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller
from telethon import TelegramClient
import db.database as db

class ProxyState(UserState):
    async def start_msg(self):
        self.edit_name = None
        self.list_proxy_names = db.get_ipport_proxys_list()
        self.current_page = 0
        self.max_page = 10
        self.is_acc = False
        return Response(text="Список проксі:", buttons=markups.generate_proxy_list_btn(self.current_page, self.max_page))

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")
        elif data_btn == "/add":
            self.edit_name = "add"
            return Response(text="Уведіть проксі у форматі тип:айпі:порт:логін:пароль (приклад, http:127.0.0.1:22:admin:pass123)\n\nКожне проксі з нового рядка\nПідтримувані типи: socks4, socks5, http", buttons=markups.generate_cancel())
        elif data_btn == "/next":
            if (self.current_page + 1) * self.max_page > len(self.list_proxy_names):
                self.current_page = 0
            else:
                self.current_page += 1
            return Response(text="Список проксі:",
                            buttons=markups.generate_proxy_list_btn(self.current_page * self.max_page, self.max_page))
        elif data_btn == "/prev":
            if (self.current_page - 1) * self.max_page < 0:
                self.current_page = 0
            else:
                self.current_page -= 1
            return Response(text="Список проксі:",
                            buttons=markups.generate_proxy_list_btn(self.current_page * self.max_page, self.max_page))
        elif data_btn == "/accnext":
            if self.is_acc:
                if (self.current_page + 1) * self.max_page > len(config_controller.LIST_TG_ACC):
                    self.current_page = 0
                else:
                    self.current_page += 1
                return Response(text="До якого акаунту під'єднати?",
                                buttons=markups.generate_tg_acc_menu(self.current_page * self.max_page,
                                                                        self.max_page, with_ready=False))
        elif data_btn == "/accprev":
            if self.is_acc:
                if (self.current_page - 1) * self.max_page < 0:
                    self.current_page = 0
                else:
                    self.current_page -= 1
                return Response(text="До якого акаунту під'єднати?",
                                buttons=markups.generate_tg_acc_menu(self.current_page * self.max_page,
                                                                        self.max_page, with_ready=False))
        elif data_btn in self.list_proxy_names:
            self.proxy_ip = data_btn.split(":")[0]
            self.proxy_port = data_btn.split(":")[1]
            return Response(text="Проксі: "+self.proxy_ip+":"+self.proxy_port, buttons=markups.generate_proxy_semimenu())
        elif data_btn == "/delete":
            db.delete_proxy(self.proxy_ip, self.proxy_port)
            return Response(redirect="/proxys")
        elif data_btn == "/toacc":
            self.edit_name = "toacc"
            self.current_page = 0
            self.is_acc = True
            return Response(text="До якого акаунту під'єднати?", buttons=markups.generate_tg_acc_menu(self.current_page, self.max_page, with_ready=False))
        elif data_btn in config_controller.LIST_TG_ACC:
            self.is_acc = False
            config_controller.set_proxy_acc(data_btn, self.proxy_ip+":"+self.proxy_port)
            return Response(text="Додано!", redirect="/proxys")
        elif data_btn == "/autoroz":
            def get_low_proxy():
                proxys_count = {}
                for proxy in db.get_ipport_proxys_list():
                    proxys_count[proxy] = 0
                    for acc in config_controller.LIST_TG_ACC:
                        if config_controller.LIST_TG_ACC[acc].get("proxy", None) == proxy:
                            proxys_count[proxy] += 1
                low_count = -1
                low_proxy = None
                for proxy in proxys_count:
                    if low_proxy == -1:
                        low_count = proxys_count[proxy]
                        low_proxy = proxy
                    else:
                        if low_count > proxys_count[proxy]:
                            low_count = proxys_count[proxy]
                            low_proxy = proxy
                return low_proxy

            for acc in config_controller.LIST_TG_ACC:
                if config_controller.LIST_TG_ACC[acc].get("proxy", None) == None:
                    config_controller.set_proxy_acc(acc, get_low_proxy())
            return Response(text="Проксі розділені між акаунтами!", redirect="/menu")




    async def next_msg(self, message: str):
        if self.edit_name == "add":
            count = 0
            list_proxy = message.split("\n")
            for i in list_proxy:
                proxy = i.replace(" ", "").split(":")
                if len(proxy) != 5:
                    continue
                type_proxy = -1
                if proxy[0].lower() == 'socks4':
                    type_proxy = 1
                elif proxy[0].lower() == 'socks5':
                    type_proxy = 2
                elif proxy[0].lower() == 'http':
                    type_proxy = 3
                if type_proxy == -1:
                    continue
                db.create_proxy(proxy[1], proxy[2], proxy[3], proxy[4], type_proxy)
                count+=1
            self.edit_name = None
            self.list_proxy_names = db.get_ipport_proxys_list()
            return Response(text="Було додано " + str(count) + " проксі!", redirect="/proxys")

