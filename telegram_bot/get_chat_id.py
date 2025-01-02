import os
import asyncio

from dotenv import load_dotenv
from telegram import Bot


load_dotenv()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def get_chat_id():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updates = await bot.get_updates()

    if not updates:
        print("No updates found")
    else:
        for update in updates:
            if update.message:
                chat_id = update.message.chat.id
                print(f"Chat ID: {chat_id}")


asyncio.run(get_chat_id())
