import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller
import db.database as db
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest, JoinChannelRequest, InviteToChannelRequest, LeaveChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
import asyncio

class ParseChatsState(UserState):
    async def start_msg(self):
        self.client: TelegramClient = None
        self.edit = None
        self.current_session = None
        self.hash_phone = None
        return Response(text="(Будуть спарсені користувачі, які є у чатах акаунту)\nОберіть акаунт для парсингу:", buttons=markups.generate_tg_acc_menu2())

    async def next_msg(self, message: str):
        if self.edit == "code_enter":
            code = message.replace(".", "").replace("-", "").replace(" ", "")
            try:
                await self.client.sign_in(config_controller.LIST_TG_ACC[self.current_session]["phone"], code)
            except SessionPasswordNeededError:
                if config_controller.LIST_TG_ACC[self.current_session].get("password", None) != None:
                    await self.client.sign_in(password=config_controller.LIST_TG_ACC[self.current_session]["password"])
                else:
                    return Response(text="Потрібен пароль до цього акаунту! Видаліть його та створіть новий з паролем", redirect="/menu")
            if not await self.client.is_user_authorized():
                self.hash_phone = await self.client.send_code_request(config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.edit = "code_enter"
                return Response(
                    text="Ви не правильно ввели код\nНа акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):", buttons=markups.generate_cancel())
            else:
                chanels, users, erorrs = await self.parse_chats()
                return Response(text="Спарсено чатів: " + str(chanels)+"\nСпарсено контактів: "+str(users)+"\nЧатів, де не вдалося спарсити контакти: " +str(erorrs), redirect="/menu")

    async def parse_chats(self):
        message_tmp = await self.bot.send_message(chat_id=self.user_chat_id, text="Триває парсинг чатів...")
        dialogs = await self.client.get_dialogs()
        channels_count = 0
        user_count = 0
        last_user_count = 0
        channels_errors_count = 0
        current_count = 0
        for i in dialogs:
            if i.entity.__class__.__name__ != "User":
                last_user_count = user_count
                current_count = 0
                channels_count+=1
                print(i.entity.title)
                try:
                    entity = i.entity
                    name_chanel = entity.title
                    participants = await self.client(GetParticipantsRequest(
                        entity,
                        ChannelParticipantsSearch(''),
                        0, 0, 0
                    ))
                    count_users = participants.count
                    print("COUNT USER IN CHAT ", count_users)
                    index = 0
                    ban_list = []
                    while (index < count_users):
                        participants = await self.client(GetParticipantsRequest(
                            entity,
                            ChannelParticipantsSearch(''),
                            index, 0, 0
                        ))

                        for i in participants.participants:
                            if i.__class__.__name__ != "ChannelParticipant":
                                ban_list.append(i.user_id)

                        for participant in participants.users:
                            if participant.id in ban_list:
                                index += 1
                                continue
                            if participant.is_self == False and participant.deleted == False and participant.bot == False and participant.username != None:
                                if participant.last_name == None:
                                    db.create_other_user(participant.first_name, participant.id, participant.username,
                                                         name_chanel, participant.phone)
                                else:
                                    db.create_other_user(participant.first_name + " " + participant.last_name,
                                                         participant.id, participant.username, name_chanel,
                                                         participant.phone)
                                user_count+=1
                                print(user_count)
                                current_count +=1
                            index += 1

                    if current_count == 0:
                        try:
                            users_list = []
                            errors = 0
                            tmp_count = 0
                            async for message in self.client.iter_messages(entity.id, limit=10000):
                                tmp_count += 1
                                print(tmp_count, name_chanel)
                                try:
                                    if message.__class__.__name__ == "Message":
                                        if message.from_id.__class__.__name__ == "PeerUser":
                                            if (not (message.from_id.user_id in users_list)) and (not(message.from_id.user_id in ban_list)):
                                                users_list.append(message.from_id.user_id)
                                                try:
                                                    user = await self.client.get_entity(message.from_id.user_id)
                                                    print(message)
                                                    username = user.username
                                                    if username:
                                                        if user.last_name == None:
                                                            db.create_other_user(user.first_name, user.id,
                                                                                 user.username,
                                                                                 name_chanel, user.phone)
                                                        else:
                                                            db.create_other_user(
                                                                user.first_name + " " + user.last_name,
                                                                user.id, user.username, name_chanel,
                                                                user.phone)
                                                        user_count += 1
                                                    if user_count % 10 == 0:
                                                        await self.bot.edit_message_text(
                                                            text="Триває парсинг чатів...\nЗараз парситься чат: " + str(
                                                                i.entity.title) + "\nЗ цього чата спарсено контактів: " + str(
                                                                user_count - last_user_count) + "\nВсього спарсено контактів: " + str(
                                                                user_count), chat_id=self.user_chat_id,
                                                            message_id=message_tmp.id)
                                                except FloodWaitError as ex:
                                                    time_sleep = int(str(ex).split("A wait of ")[1].split(" ")[0])
                                                    print("WAIT", time_sleep)
                                                    await self.bot.edit_message_text(
                                                        text="Триває парсинг чатів...\nЗараз парситься чат: " + str(
                                                            i.entity.title) + "\nЗ цього чата спарсено контактів: " + str(
                                                            user_count - last_user_count) + "\nВсього спарсено контактів: " + str(
                                                            user_count)+"\n(Анти флуд, очікування " + str(time_sleep) + " секунд)", chat_id=self.user_chat_id,
                                                        message_id=message_tmp.id)
                                                    await asyncio.sleep(time_sleep + 5)
                                                    try:
                                                        user = await self.client.get_entity(message.from_id.user_id)
                                                        username = user.username
                                                        if username:
                                                            if user.last_name == None:
                                                                db.create_other_user(user.first_name, user.id,
                                                                                     user.username,
                                                                                     name_chanel, user.phone)
                                                            else:
                                                                db.create_other_user(
                                                                    user.first_name + " " + user.last_name,
                                                                    user.id, user.username, name_chanel,
                                                                    user.phone)
                                                            user_count += 1
                                                    except:
                                                        pass
                                                except Exception as e:
                                                    errors += 1
                                                    print(f"Error: {e}")
                                                    print("ERRORS", errors)
                                                    if errors > 1000:
                                                        break
                                except Exception as ex:
                                    print(ex)
                        except:
                            channels_errors_count += 1
                    for tt in ban_list:
                        if db.delete_userother_by_tg_id(str(tt)):
                            user_count -= 1
                    await self.bot.edit_message_text(
                        text="Триває парсинг чатів...\nЗараз парситься чат: " + str(
                            i.entity.title) + "\nЗ цього чата спарсено контактів: " + str(
                            user_count - last_user_count) + "\nВсього спарсено контактів: " + str(
                            user_count), chat_id=self.user_chat_id,
                        message_id=message_tmp.id)
                except Exception as ex:
                    print(ex)
                    channels_errors_count += 1

        await self.client.disconnect()
        await self.bot.delete_message(chat_id=self.user_chat_id, message_id=message_tmp.id)
        return channels_count, user_count, channels_errors_count

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/menu")
        if data_btn in config_controller.LIST_TG_ACC:
            self.current_session = data_btn
            self.client = TelegramClient(session=self.current_session,
                                         api_id=config_controller.LIST_TG_ACC[self.current_session]["api_id"],
                                         api_hash=config_controller.LIST_TG_ACC[self.current_session]["api_hash"])
            try:
                await self.client.connect()
            except:
                pass
            if not await self.client.is_user_authorized():
                self.hash_phone = await self.client.send_code_request(
                    config_controller.LIST_TG_ACC[self.current_session]["phone"])
                self.edit = "code_enter"
                return Response(
                    text="На акаунт має прийти пароль, уведіть його у форматі 1.2.3.4.5.6, (це приклад якби у вас був пароль 123456):", buttons=markups.generate_cancel())
            else:
                chanels, users, erorrs = await self.parse_chats()
                return Response(text="Спарсено чатів: " + str(chanels) + "\nСпарсено контактів: " + str(
                    users) + "\nЧатів, де не вдалося спарсити контакти: " + str(erorrs), redirect="/menu")