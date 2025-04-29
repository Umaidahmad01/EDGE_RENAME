import asyncio
import time
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="AutoRenamerBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=50,  # Reduced for bot-hosting.net
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.start_time = time.time()

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        print(f"{me.first_name} is started... ✨")

        # Notify log channel
        uptime = str(timedelta(seconds=int(time.time() - self.start_time)))
        try:
            await self.send_photo(
                chat_id=Config.LOG_CHANNEL,
                photo=Config.START_PIC,
                caption=f"**Bot is restarted!**\n\nUptime: `{uptime}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Updates", url="https://t.me/animes_sub_society")]]
                ),
            )
        except Exception as e:
            print(f"Failed to send message to log channel: {e}")

    async def stop(self):
        await super().stop()
        print("Bot stopped.")

if __name__ == "__main__":
    Bot().run()