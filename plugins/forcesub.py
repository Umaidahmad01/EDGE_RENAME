from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import UserNotParticipant
from config import Config

async def not_subscribed(client, message):
    for channel in Config.FORCE_SUB:
        try:
            user = await client.get_chat_member(channel, message.from_user.id)
            if user.status in {"kicked", "left"}:
                return True
        except UserNotParticipant:
            return True
    return False

@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client, message):
    not_joined_channels = []
    for channel in Config.FORCE_SUB:
        try:
            user = await client.get_chat_member(channel, message.from_user.id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
    buttons = [[InlineKeyboardButton(f"• Join {channel.capitalize()} •", url=f"https://t.me/{channel}")] for channel in not_joined_channels]
    buttons.append([InlineKeyboardButton("• Joined •", callback_data="check_subscription")])
    await message.reply_photo(
        photo="https://graph.org/file/a27d85469761da836337c.jpg",
        caption="**Please join all required channels to continue**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    not_joined_channels = []
    for channel in Config.FORCE_SUB:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
    if not not_joined_channels:
        await callback_query.message.edit_caption(
            caption="**You have joined all required channels. Thank you! 😊 /start now**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Now click here •", callback_data='help')]])
        )
    else:
        buttons = [[InlineKeyboardButton(f"• Join {channel.capitalize()} •", url=f"https://t.me/{channel}")] for channel in not_joined_channels]
        buttons.append([InlineKeyboardButton("• Joined •", callback_data="check_subscription")])
        await callback_query.message.edit_caption(
            caption="**Please join all required channels to continue**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )