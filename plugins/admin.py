import os
import sys
import time
import asyncio
import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils import Database, get_db

db = Database(get_db())

is_restarting = False

@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(client, message):
    global is_restarting
    if not is_restarting:
        is_restarting = True
        await message.reply_text("**Restarting...**")
        client.stop()
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.private & filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(client, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply('**Accessing details...**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(f"**Bot Status**\n\n**Uptime**: {uptime}\n**Ping**: `{time_taken_s:.3f} ms`\n**Total Users**: `{total_users}`")

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(client, message):
    await client.send_message(Config.LOG_CHANNEL, f"{message.from_user.mention} started broadcast...")
    all_users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    sts_msg = await message.reply_text("Broadcast started...")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['user_id'], broadcast_msg, client)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user['user_id'])
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Broadcast in progress:\n\nTotal: {total_users}\nDone: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Broadcast completed in `{completed_in}`.\n\nTotal: {total_users}\nDone: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}")

async def send_msg(user_id, message, client):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except Exception:
        return 400