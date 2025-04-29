import os
import re
import time
import shutil
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from pymongo import MongoClient
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=Config.MAX_CONCURRENT * 2)  # 2x for per-user tasks

# NSFW keywords (simplified for brevity)
NSFW_KEYWORDS = {
    "general": ["porn", "sex", "nude", "naked", "boobs", "ass"],
    "hentai": ["hentai", "doujinshi", "ecchi"],
    "abbreviations": ["pr0n", "s3x"],
    "offensive_slang": ["slut", "whore"]
}
EXCEPTION_KEYWORDS = ["nxivm", "classroom", "assassination", "geass"]

# Season, episode, and quality patterns
SEASON_EPISODE_PATTERNS = [
    (re.compile(r'S(\d+)(?:E|EP)(\d+)'), ('season', 'episode')),
    (re.compile(r'S(\d+)[\s-]*(?:E|EP)(\d+)'), ('season', 'episode')),
    (re.compile(r'Season\s*(\d+)\s*Episode\s*(\d+)', re.IGNORECASE), ('season', 'episode')),
    (re.compile(r'\[S(\d+)\]\[E(\d+)\]'), ('season', 'episode')),
    (re.compile(r'S(\d+)[^\d]*(\d+)'), ('season', 'episode')),
    (re.compile(r'(?:E|EP|Episode)\s*(\d+)', re.IGNORECASE), (None, 'episode')),
    (re.compile(r'\b(\d+)\b'), (None, 'episode'))
]
QUALITY_PATTERNS = [
    (re.compile(r'\b(\d{3,4}[pi])\b', re.IGNORECASE), lambda m: m.group(1)),
    (re.compile(r'\b(4k|2160p)\b', re.IGNORECASE), lambda m: "4k"),
    (re.compile(r'\b(2k|1440p)\b', re.IGNORECASE), lambda m: "2k")
]

async def check_nsfw(new_name, message):
    lower_name = new_name.lower()
    for keyword in EXCEPTION_KEYWORDS:
        if keyword.lower() in lower_name:
            return False
    for category, keywords in NSFW_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in lower_name:
                await message.reply_text("You can't rename files with NSFW content.")
                return True
    return False

def extract_season_episode(filename):
    for pattern, (season_group, episode_group) in SEASON_EPISODE_PATTERNS:
        match = pattern.search(filename)
        if match:
            season = match.group(1) if season_group else None
            episode = match.group(2) if episode_group else match.group(1)
            return season, episode
    return None, None

def extract_quality(filename):
    for pattern, extractor in QUALITY_PATTERNS:
        match = pattern.search(filename)
        if match:
            return extractor(match)
    return "Unknown"

async def cleanup_files(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"Error removing {path}: {e}")

async def process_thumbnail(thumb_path):
    if not thumb_path or not os.path.exists(thumb_path):
        return None
    try:
        with Image.open(thumb_path) as img:
            img = img.convert("RGB").resize((320, 320))
            img.save(thumb_path, "JPEG")
        return thumb_path
    except Exception as e:
        logger.error(f"Thumbnail processing failed: {e}")
        await cleanup_files(thumb_path)
        return None

async def add_metadata(input_path, output_path, user_id, db):
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        logger.warning("FFmpeg not found; skipping metadata")
        shutil.copy(input_path, output_path)
        return
    metadata = {
        'title': await db.get_title(user_id) or "",
        'artist': await db.get_artist(user_id) or "",
        'author': await db.get_author(user_id) or "",
        'video_title': await db.get_video(user_id) or "",
        'audio_title': await db.get_audio(user_id) or "",
        'subtitle': await db.get_subtitle(user_id) or ""
    }
    cmd = [
        ffmpeg, '-i', input_path,
        '-metadata', f'title={metadata["title"]}',
        '-metadata', f'artist={metadata["artist"]}',
        '-metadata', f'author={metadata["author"]}',
        '-metadata:s:v', f'title={metadata["video_title"]}',
        '-metadata:s:a', f'title={metadata["audio_title"]}',
        '-metadata:s:s', f'title={metadata["subtitle"]}',
        '-map', '0', '-c', 'copy', '-loglevel', 'error',
        output_path
    ]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"FFmpeg error: {stderr.decode()}")
        shutil.copy(input_path, output_path)

async def process_file(client, message, file_id, file_name, file_size, media_type, format_template, user_id, db):
    if await check_nsfw(file_name, message):
        return None
    season, episode = extract_season_episode(file_name)
    quality = extract_quality(file_name)
    replacements = {
        '{season}': season or 'XX',
        '{episode}': episode or 'XX',
        '{quality}': quality,
        'Season': season or 'XX',
        'Episode': episode or 'XX',
        'QUALITY': quality
    }
    for placeholder, value in replacements.items():
        format_template = format_template.replace(placeholder, value)
    ext = os.path.splitext(file_name)[1] or ('.mp4' if media_type == 'video' else '.mp3')
    new_filename = f"{format_template}{ext}"
    download_path = f"downloads/{user_id}/{new_filename}"
    metadata_path = f"metadata/{user_id}/{new_filename}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    msg = await message.reply_text("**Downloading...**")
    try:
        file_path = await client.download_media(message, file_name=download_path, progress=progress_for_pyrogram, progress_args=("Downloading...", msg, time.time()))
        if not file_path:
            raise ValueError("Download failed")
        await msg.edit("**Processing metadata...**")
        if await db.get_metadata(user_id) == "On":
            await add_metadata(file_path, metadata_path, user_id, db)
            file_path = metadata_path
        else:
            shutil.copy(file_path, metadata_path)
            file_path = metadata_path
        await msg.edit("**Preparing upload...**")
        caption = await db.get_caption(user_id) or f"**{new_filename}**"
        thumb = await db.get_thumbnail(user_id)
        thumb_path = None
        if thumb:
            thumb_path = await client.download_media(thumb)
        elif media_type == "video" and message.video and message.video.thumbs:
            thumb_path = await client.download_media(message.video.thumbs[0].file_id)
        thumb_path = await process_thumbnail(thumb_path)
        await msg.edit("**Uploading...**")
        upload_params = {
            'chat_id': message.chat.id,
            'caption': caption,
            'thumb': thumb_path,
            'progress': progress_for_pyrogram,
            'progress_args': ("Uploading...", msg, time.time())
        }
        if media_type == "document":
            await client.send_document(document=file_path, **upload_params)
        elif media_type == "video":
            await client.send_video(video=file_path, **upload_params)
        elif media_type == "audio":
            await client.send_audio(audio=file_path, **upload_params)
        await msg.delete()
        return file_path
    except Exception as e:
        await msg.edit(f"Error: {e}")
        return None
    finally:
        await cleanup_files(download_path, metadata_path, thumb_path)

async def handle_concurrent_processing(client, message, file_id, file_name, file_size, media_type, format_template, user_id, db):
    tasks = []
    for _ in range(min(Config.MAX_CONCURRENT, 2)):  # At least 2, up to MAX_CONCURRENT
        task = asyncio.create_task(process_file(client, message, file_id, file_name, file_size, media_type, format_template, user_id, db))
        tasks.append(task)
    return await asyncio.gather(*tasks, return_exceptions=True)

def get_db():
    client = MongoClient(Config.DB_URL)
    return client[Config.DB_NAME]

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        progress = f"{ud_type}\n\n" + \
                   f"**Progress**: {round(percentage, 2)}%\n" + \
                   f"**Completed**: {humanbytes(current)} / {humanbytes(total)}\n" + \
                   f"**Speed**: {humanbytes(speed)}/s\n" + \
                   f"**ETA**: {estimated_total_time if estimated_total_time != '' else '0 s'}"
        await message.edit_text(progress)

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)}{Dic_powerN[n]}B"

class TimeFormatter:
    def __init__(self, milliseconds: int):
        self.milliseconds = milliseconds

    def __str__(self) -> str:
        seconds, milliseconds = divmod(self.milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return (
            f"{days}d " if days else ""
            + f"{hours}h " if hours else ""
            + f"{minutes}m " if minutes else ""
            + f"{seconds}s " if seconds else ""
            + f"{milliseconds}ms" if milliseconds else ""
        ).strip()

# Database helper class (assumed structure from codeflixbots)
class Database:
    def __init__(self, db):
        self.db = db

    async def add_user(self, client, message):
        user_id = message.from_user.id
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

    async def get_format_template(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"format_template": 1})
        return user.get("format_template") if user else None

    async def set_format_template(self, user_id, format_template):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"format_template": format_template}}, upsert=True)

    async def get_media_preference(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"media_preference": 1})
        return user.get("media_preference") if user else None

    async def set_media_preference(self, user_id, media_type):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"media_preference": media_type}}, upsert=True)

    async def get_caption(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"caption": 1})
        return user.get("caption") if user else None

    async def set_caption(self, user_id, caption):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"caption": caption}}, upsert=True)

    async def get_thumbnail(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"thumbnail": 1})
        return user.get("thumbnail") if user else None

    async def set_thumbnail(self, user_id, file_id):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"thumbnail": file_id}}, upsert=True)

    async def get_metadata(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"metadata": 1})
        return user.get("metadata", "Off") if user else "Off"

    async def set_metadata(self, user_id, status):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"metadata": status}}, upsert=True)

    async def get_title(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"title": 1})
        return user.get("title") if user else None

    async def set_title(self, user_id, title):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"title": title}}, upsert=True)

    async def get_author(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"author": 1})
        return user.get("author") if user else None

    async def set_author(self, user_id, author):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"author": author}}, upsert=True)

    async def get_artist(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"artist": 1})
        return user.get("artist") if user else None

    async def set_artist(self, user_id, artist):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"artist": artist}}, upsert=True)

    async def get_video(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"video": 1})
        return user.get("video") if user else None

    async def set_video(self, user_id, video):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"video": video}}, upsert=True)

    async def get_audio(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"audio": 1})
        return user.get("audio") if user else None

    async def set_audio(self, user_id, audio):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"audio": audio}}, upsert=True)

    async def get_subtitle(self, user_id):
        user = await self.db.users.find_one({"user_id": user_id}, {"subtitle": 1})
        return user.get("subtitle") if user else None

    async def set_subtitle(self, user_id, subtitle):
        await self.db.users.update_one({"user_id": user_id}, {"$set": {"subtitle": subtitle}}, upsert=True)

    async def total_users_count(self):
        return await self.db.users.count_documents({})

    async def get_all_users(self):
        return self.db.users.find()

    async def delete_user(self, user_id):
        await self.db.users.delete_one({"user_id": user_id})