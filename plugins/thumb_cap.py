from pyrogram import Client, filters
from utils import Database, get_db

db = Database(get_db())

@Client.on_message(filters.private & filters.command('set_caption'))
async def add_caption(client, message):
    if len(message.command) == 1:
        return await message.reply_text("**Give the caption\n\nExample: `/set_caption 📕Name ➠ : {filename} \n🔗 Size ➠ : {filesize} \n⏰ Duration ➠ : {duration}`**")
    caption = message.text.split(" ", 1)[1]
    await db.set_caption(message.from_user.id, caption)
    await message.reply_text("**Caption added ✅**")

@Client.on_message(filters.private & filters.command('del_caption'))
async def delete_caption(client, message):
    caption = await db.get_caption(message.from_user.id)
    if not caption:
        return await message.reply_text("**No caption set ❌**")
    await db.set_caption(message.from_user.id, None)
    await message.reply_text("**Caption deleted 🗑️**")

@Client.on_message(filters.private & filters.command(['see_caption', 'view_caption']))
async def see_caption(client, message):
    caption = await db.get_caption(message.from_user.id)
    if caption:
        await message.reply_text(f"**Your caption:**\n\n`{caption}`")
    else:
        await message.reply_text("**No caption set ❌**")

@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def viewthumb(client, message):
    thumb = await db.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("**No thumbnail set ❌**")

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
async def removethumb(client, message):
    await db.set_thumbnail(message.from_user.id, None)
    await message.reply_text("**Thumbnail deleted 🗑️**")

@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    mkn = await message.reply_text("Please wait...")
    await db.set_thumbnail(message.from_user.id, message.photo.file_id)
    await mkn.edit("**Thumbnail saved ✅**")