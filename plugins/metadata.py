from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Txt
from utils import Database, get_db

db = Database(get_db())

@Client.on_message(filters.private & filters.command("metadata"))
async def metadata_command(client, message):
    user_id = message.from_user.id
    current = await db.get_metadata(user_id)
    title = await db.get_title(user_id)
    author = await db.get_author(user_id)
    artist = await db.get_artist(user_id)
    video = await db.get_video(user_id)
    audio = await db.get_audio(user_id)
    subtitle = await db.get_subtitle(user_id)
    text = f"""
**㊋ Metadata is currently: {current}**

**◈ Title ▹** `{title or 'Not found'}`
**◈ Author ▹** `{author or 'Not found'}`
**◈ Artist ▹** `{artist or 'Not found'}`
**◈ Audio ▹** `{audio or 'Not found'}`
**◈ Subtitle ▹** `{subtitle or 'Not found'}`
**◈ Video ▹** `{video or 'Not found'}`
    """
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"On{' ✅' if current == 'On' else ''}", callback_data='on_metadata'), InlineKeyboardButton(f"Off{' ✅' if current == 'Off' else ''}", callback_data='off_metadata')],
        [InlineKeyboardButton("How to Set Metadata", callback_data="metainfo")]
    ]))

@Client.on_callback_query(filters.regex(r"on_metadata|off_metadata|metainfo"))
async def metadata_callback(client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data
    if data == "on_metadata":
        await db.set_metadata(user_id, "On")
    elif data == "off_metadata":
        await db.set_metadata(user_id, "Off")
    elif data == "metainfo":
        await query.message.edit_text(Txt.META_TXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Hᴏᴍᴇ", callback_data="home"), InlineKeyboardButton("close", callback_data="close")]
        ]))
        return
    current = await db.get_metadata(user_id)
    title = await db.get_title(user_id)
    author = await db.get_author(user_id)
    artist = await db.get_artist(user_id)
    video = await db.get_video(user_id)
    audio = await db.get_audio(user_id)
    subtitle = await db.get_subtitle(user_id)
    text = f"""
**㊋ Metadata is currently: {current}**

**◈ Title ▹** `{title or 'Not found'}`
**◈ Author ▹** `{author or 'Not found'}`
**◈ Artist ▹** `{artist or 'Not found'}`
**◈ Audio ▹** `{audio or 'Not found'}`
**◈ Subtitle ▹** `{subtitle or 'Not found'}`
**◈ Video ▹** `{video or 'Not found'}`
    """
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"On{' ✅' if current == 'On' else ''}", callback_data='on_metadata'), InlineKeyboardButton(f"Off{' ✅' if current == 'Off' else ''}", callback_data='off_metadata')],
        [InlineKeyboardButton("How to Set Metadata", callback_data="metainfo")]
    ]))

@Client.on_message(filters.private & filters.command(['settitle', 'setauthor', 'setartist', 'setaudio', 'setsubtitle', 'setvideo']))
async def set_metadata(client, message):
    cmd = message.command[0]
    if len(message.command) == 1:
        return await message.reply_text(f"**Give the {cmd[3:].capitalize()}\n\nExample: /{cmd} @Animes_Sub_Society**")
    value = message.text.split(" ", 1)[1]
    await db.__setattr__(f"set_{cmd[3:]}")(message.from_user.id, value)
    await message.reply_text(f"**✅ {cmd[3:].capitalize()} Saved**")