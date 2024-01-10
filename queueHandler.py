QUEUE = {}

import asyncio
from bingai import generate_image, download_images, WORKER, get_worker, COOKIE_EMAIL
from pyrogram import Client
from pyrogram.types import Message, InputMediaPhoto
import os
from db import addGenStatus


def sorter(key):
    return key[1]["pos"]


async def QueueRunner(bot):
    global WORKER, QUEUE

    while True:
        if len(QUEUE) > 0:
            TASKS = sorted(QUEUE.items(), key=sorter)

            for userid, data in TASKS:
                if data["status"] == "waiting":
                    while True:
                        cookie = get_worker()
                        if cookie:
                            break
                        else:
                            await asyncio.sleep(10)
                            continue

                    QUEUE[userid]["status"] = "processing"
                    try:
                        asyncio.create_task(HandleProcessing(bot, userid, data, cookie))
                    except:
                        pass

        await asyncio.sleep(5)


STATUS = {}


async def QueueStatus(bot: Client):
    global QUEUE, STATUS

    while True:
        if len(QUEUE) > 0:
            TASKS = sorted(QUEUE.items(), key=sorter)
            total = len(TASKS)

            pos = 1
            for userid, data in TASKS:
                if data["status"] == "processing":
                    continue

                if userid in STATUS:
                    if STATUS[userid] == pos:
                        pos += 1
                        continue
                else:
                    STATUS[userid] = pos

                try:
                    text = f"**🔢 Queue Position:** `{pos}`\n\n**Total Queued Tasks:** {total}\n\nThis may take a while, Please Wait!"
                    await bot.edit_message_text(
                        data["chatid"],
                        data["msgid"],
                        text,
                    )
                except:
                    pass

                pos += 1
                await asyncio.sleep(1)

        await asyncio.sleep(5)


async def HandleProcessing(bot: Client, userid, data: dict, cookie: str):
    global QUEUE, WORKER, COOKIE_EMAIL, STATUS

    try:
        try:
            msg = await bot.edit_message_text(
                data["chatid"],
                data["msgid"],
                "**🔄 Generating Images...**\n\nThis may take a while, Please Wait!")
        except:
            msg = None

        image_url = await generate_image(data["promt"], cookie)

        if not image_url:
            if userid in QUEUE:
                del QUEUE[userid]
            if userid in STATUS:
                del STATUS[userid]

            WORKER[cookie] = 0

            # try:
            #     # Send error to log group/channel
            
            #     await bot.send_message(
            #         int('Chat ID'),
            #         str(userid)
            #         + "\n\n"
            #         + str(COOKIE_EMAIL.get(cookie))
            #         + "\n\n"
            #         + str(data),
            #     )
            # except:
            #     pass

            try:
                await bot.send_message(
                    data["chatid"],
                    "**❌ Failed to generate**\n\nTry Again or Improve your Promt, Give more details!\n\nReport Errors @TechZBots_Support",
                    reply_to_message_id=data["replyid"],
                )
            except:
                pass

            try:
                await msg.delete()
            except:
                pass
            return

        addGenStatus(userid, data["chatid"], len(image_url))

        try:
            await msg.edit(
                "**📥 Downloading Images...**\n\nThis may take a while, Please Wait!"
            )
        except:
            pass

        image_path = download_images(image_url, userid, cookie)

        try:
            await msg.edit(
                """**📤 Uploading Images...**\n\nThis may take a while, Please Wait!
            """
            )
        except:
            pass

        media_group = []
        for image in image_path:
            media_group.append(InputMediaPhoto(image))

        await bot.send_media_group(
            data["chatid"], media_group, reply_to_message_id=data["replyid"]
        )

        try:
            await msg.delete()
        except:
            pass

        for image in image_path:
            try:
                os.remove(image)
            except:
                pass
    except Exception as e:
        if msg:
            await msg.delete()
        await bot.send_message(
            data["chatid"], str(e), reply_to_message_id=data["replyid"]
        )

    if userid in QUEUE:
        del QUEUE[userid]
    if userid in STATUS:
        del STATUS[userid]

    WORKER[cookie] = 0
