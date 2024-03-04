import markups
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import config_controller
import services.testing.ExportDbToExel as exel

class GenerateExelState(UserState):
    async def start_msg(self):
        msg = await self.bot.send_message(chat_id=self.user_chat_id, text="Таблиця генерується...")
        doc_name = exel.create_exel("DataBase")
        await self.bot.delete_message(chat_id=self.user_chat_id, message_id=msg.id)
        return Response(documents=[open(doc_name, 'rb')], redirect="/menu")