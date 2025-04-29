import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config, Txt
from utils import Database, get_db

db = Database(get_db())

@Client.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    user = message.from_user
    await db.add_user(client, message)
    m = await message.reply_text("ʜᴇʜᴇ..ɪ'ᴍ ᴀɴʏᴀ!\nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ. . .")
    await asyncio.sleep(0.4)
    await m.edit_text("🎊")
    await asyncio.sleep(0.5)
    await m.edit_text("⚡")
    await asyncio.sleep(0.5)
    await m.edit_text("ᴡᴀᴋᴜ ᴡᴀᴋᴜ!...")
    await asyncio.sleep(0.4)
    await m.delete()
    await message.reply_sticker("CAACAgUAAxkBAAECroBmQKMAAQ-Gw4nibWoj_pJou2vP1a4AAlQIAAIzDxlVkNBkTEb1Lc4eBA")
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data='help')],
        [InlineKeyboardButton('• ᴜᴘᴅᴀᴛᴇs', url='https://t.me/animes_sub_society')],
        [InlineKeyboardButton('• ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('sᴏᴜʀᴄᴇ •', callback_data='source')]
    ])
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=buttons)
    else:
        await message.reply_text(Txt.START_TXT.format(user.mention), reply_markup=buttons, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.command("help"))
async def help_command(client, message):
    bot = await client.get_me()
    await message.reply_text(
        Txt.HELP_TXT.format(mention=bot.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴤ", callback_data='file_names')],
            [InlineKeyboardButton('• ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'), InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ •', callback_data='caption')],
            [InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta'), InlineKeyboardButton('ᴅᴏɴᴀᴛᴇ •', callback_data='donate')],
            [InlineKeyboardButton('• ʜᴏᴍᴇ', callback_data='home')]
        ])
    )

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    if data == "home":
        await query.message.edit_text(Txt.START_TXT.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data='help')],
            [InlineKeyboardButton('• ᴜᴘᴅᴀᴛᴇs', url='https://t.me/animes_sub_society')],
            [InlineKeyboardButton('• ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('sᴏᴜʀᴄᴇ •', callback_data='source')]
        ]))
    elif data == "help":
        await query.message.edit_text(Txt.HELP_TXT.format((await client.get_me()).mention), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴤ", callback_data='file_names')],
            [InlineKeyboardButton('• ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'), InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ •', callback_data='caption')],
            [InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta'), InlineKeyboardButton('ᴅᴏɴᴀᴛᴇ •', callback_data='donate')],
            [InlineKeyboardButton('• ʜᴏᴍᴇ', callback_data='home')]
        ]))
    elif data == "file_names":
        format_template = await db.get_format_template(user_id) or ""
        await query.message.edit_text(Txt.FILE_NAME_TXT.format(format_template=format_template), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ •", callback_data="help")]
        ]))
    elif data == "thumbnail":
        await query.message.edit_caption(Txt.THUMBNAIL_TXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ •", callback_data="help")]
        ]))
    elif data == "caption":
        await query.message.edit_text(Txt.CAPTION_TXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs", url='https://t.me/animes_sub_society'), InlineKeyboardButton("ʙᴀᴄᴋ •", callback_data="help")]
        ]))
    elif data == "meta":
        await query.message.edit_text(Txt.SEND_METADATA, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ •", callback_data="help")]
        ]))
    elif data == "donate":
        await query.message.edit_text(Txt.DONATE_TXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("ᴏᴡɴᴇʀ •", url='https://t.me/sewxiy')]
        ]))
    elif data == "about":
        await query.message.edit_text(Txt.ABOUT_TXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs", url='https://t.me/animes_sub_society'), InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅs •", callback_data="help")],
            [InlineKeyboardButton("• ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/cosmic_freak')],
            [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="home")]
        ]))
    elif data == "source":
        await query.message.edit_caption(Txt.SOURCE_TXT, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ •", callback_data="home")]
        ]))
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()