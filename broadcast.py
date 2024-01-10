from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import time
from config import *

db = MongoClient(MONGOURI)["bingbot"]
usersdb = db.users

bot = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)

bot.start()
print("Bot Started!")

for user in usersdb.find():
    id = user["userid"]
    try:
        bot.send_message(
            chat_id=id,
            text="""your message""",
            disable_web_page_preview=True,
        )
        print(f"Sent broadcast to {id}")
    except FloodWait as e:
        print(f"Sleeping for {e.x} seconds")
        time.sleep(e.x)
    except Exception as e:
        print(e)
