from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import handle_concurrent_processing, Database, get_db

db = Database(get_db())

@Client.on_message(filters.private & filters.command("autorename"))
async def auto_rename_command(client, message):
    user_id = message.from_user.id
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2 or not command_parts[1].strip():
        await message.reply_text(
            "**Please provide a new name after /autorename**\n\n"
            "Example: `/autorename Overflow [S{season}E{episode}] - [Dual] {quality}`"
        )
        return
    format_template = command_parts[1].strip()
    await db.set_format_template(user_id, format_template)
    await message.reply_text(
        f"**🌟 Format saved!**\n\n"
        f"Template: `{format_template}`\n\n"
        "Send a file to rename it! ✨"
    )

@Client.on_message(filters.private & filters.command("setmedia"))
async def set_media_command(client, message):
    await message.reply_text(
        "✨ **Choose media type** ✨\nSelect your preference:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Documents", callback_data="setmedia_document")],
            [InlineKeyboardButton("🎬 Videos", callback_data="setmedia_video")],
            [InlineKeyboardButton("🎵 Audio", callback_data="setmedia_audio")]
        ])
    )

@Client.on_callback_query(filters.regex(r"^setmedia_"))
async def handle_media_selection(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    media_type = callback_query.data.split("_", 1)[1].capitalize()
    try:
        await db.set_media_preference(user_id, media_type.lower())
        await callback_query.message.edit_text(f"🎯 **Media set to {media_type}** ✅")
    except Exception as e:
        await callback_query.message.edit_text(f"⚠️ Error: {str(e)}")

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def auto_rename_files(client, message):
    user_id = message.from_user.id
    format_template = await db.get_format_template(user_id)
    if not format_template:
        await message.reply_text("Please set a rename format using /autorename")
        return
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_size = message.document.file_size
        media_type = "document"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or "video"
        file_size = message.video.file_size
        media_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio"
        file_size = message.audio.file_size
        media_type = "audio"
    else:
        return
    results = await handle_concurrent_processing(client, message, file_id, file_name, file_size, media_type, format_template, user_id, db)
    for result in results:
        if isinstance(result, Exception):
            await message.reply_text(f"Error: {str(result)}")