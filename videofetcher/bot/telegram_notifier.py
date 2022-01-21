GREEN_TILE = "🟩" 
EMPTY_TILE = "      "

class TelegramNotifier:
    def __init__(self, bot, chat_id, update_message_id):
        self.bot = bot
        self.chat_id = chat_id
        self.update_message_id = update_message_id
        self.progress_message = ""

    def progress_update(self, update_message):
        self.progress_message = update_message
        self.bot.edit_message_text(
            update_message,
            self.chat_id,
            self.update_message_id,
            disable_web_page_preview=True,
        )
    
    def __draw_pb(self, percent=0):
        percent = percent//10
        greens = "".join([GREEN_TILE for f in range(percent)])
        emptys = "".join([EMPTY_TILE for f in range(10-percent)])
        return f"|{greens}{emptys}| {percent*10}%"

    def set_progress_bar(self, percent=0):
        msg = f"{self.progress_message}\n{self.__draw_pb(percent)}"
        self.bot.edit_message_text(
            msg,
            self.chat_id,
            self.update_message_id,
            disable_web_page_preview=True,
        )

    def rm_progress_bar(self):
        msg = f"{self.progress_message}"
        self.bot.edit_message_text(
            msg,
            self.chat_id,
            self.update_message_id,
            disable_web_page_preview=True,
        )

