import re
import os
import time
from os import environ
from datetime import timedelta

id_pattern = re.compile(r'^\d+$')

class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "20718334")
    API_HASH  = os.environ.get("API_HASH", "4e81464b29d79c58d0ad8a0c55ece4a5")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7830743177:AAHkVvb0AwI-bDqa7O0JUZdb_tvSdS4E0fA") 

    # database config
    DB_NAME = os.environ.get("DB_NAME", "Cluster0")     
    DB_URL  = os.environ.get("DB_URL", "mongodb+srv://obito:umaid2008@cluster0.engyc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    PORT = os.environ.get("PORT", "8080")

    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://graph.org/file/29a3acbbab9de5f45a5fe.jpg")
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5585016974 7328629001').split()]
    FORCE_SUB = os.environ.get('FORCE_SUB', 'animes_sub_society').split(',')
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002200709110"))
    DUMP_CHANNEL = int(os.environ.get("DUMP_CHANNEL", "-1002200709110"))
    OWNER_ID = int(os.environ.get("OWNER_ID", "5585016974"))
    MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "5"))

class Txt:
    START_TXT = """<b>Hey! {}  

» I am an advanced rename bot! Which can autorename your files with custom caption and thumbnail and also sequence them perfectly</b>"""

    FILE_NAME_TXT = """<b>» <u>Setup auto rename format</u></b>

<b>Variables :</b>
➲ episode - to replace episode number  
➲ season - to replace season number  
➲ quality - to replace quality  

<b>‣ For ex:- </b> `/autorename Overflow [Sseason Eepisode] - [Dual] quality`

<b>‣ /Autorename: rename your media files by including 'episode' and 'quality' variables in your text, to extract episode and quality present in the original filename.</b>"""

    ABOUT_TXT = """<b>❍ My name: <a href="https://t.me/animes_sub_society">Auto Rename</a>
❍ Developer: <a href="https://t.me/cosmic_freak">Yato</a>
❍ Github: <a href="https://github.com/cosmic_freak">Yato</a>
❍ Language: <a href="https://www.python.org/">Python</a>
❍ Database: <a href="https://www.mongodb.com/">Mongo DB</a>
❍ Main channel: <a href="https://t.me/animes_sub_society">Anime Sub Society</a></b>"""

    THUMBNAIL_TXT = """<b><u>» To set custom thumbnail</u></b>
    
➲ /start: send any photo to automatically set it as a thumbnail..
➲ /del_thumb: use this command to delete your old thumbnail.
➲ /view_thumb: use this command to view your current thumbnail.

Note: if no thumbnail saved in bot then, it will use thumbnail of the original file to set in renamed file"""

    CAPTION_TXT = """<b><u>» To set custom caption and media type</u></b>
    
<b>Variables :</b>         
size: {filesize}
duration: {duration}
filename: {filename}

➲ /set_caption: to set a custom caption.
➲ /see_caption: to view your custom caption.
➲ /del_caption: to delete your custom caption.

» For ex:- /set_caption File Name: {filename}"""

    PROGRESS_BAR = """\n
<b>» Size</b> : {1} | {2}
<b>» Done</b> : {0}%
<b>» Speed</b> : {3}/s
<b>» ETA</b> : {4} """

    DONATE_TXT = """<blockquote> Thanks for showing interest in donation</blockquote>

<b><i>💞 If you like our bot feel free to donate any amount ₹10, ₹20, ₹50, ₹100, etc.</i></b>

Donations are really appreciated it helps in bot development

 <u>You can also donate through UPI</u>

 UPI ID : <code>LodaLassan@fam</code>

If you wish you can send us ss
on - @ProYato"""

    PREMIUM_TXT = """<b>Upgrade to our premium service and enjoy exclusive features:
○ Unlimited Renaming: rename as many files as you want without any restrictions.
○ Early Access: be the first to test and use our latest features before anyone else.

• Use /plan to see all our plans at once.

➲ First step: pay the amount according to your favorite plan to this rohit162@fam UPI ID.

➲ Second step: take a screenshot of your payment and share it directly here: @sewxiy 

➲ Alternative step: or upload the screenshot here and reply with the /bought command.

Your premium plan will be activated after verification</b>"""

    PREPLANS_TXT = """<b>👋 bro,
    
🎖️ <u>Available plans</u> :

Pricing:
➜ Monthly premium: ₹50/month
➜ Daily premium: ₹5/day
➜ For bot hosting: contact @ProYato

➲ UPI ID - <code>LodaLassan@fam</code>

‼️Upload the payment screenshot here and reply with the /bought command.</b>"""

    HELP_TXT = """<b>Here is help menu important commands:

Awesome features🫧

Rename bot is a handy tool that helps you rename and manage your files effortlessly.

➲ /Autorename: auto rename your files.
➲ /Metadata: commands to turn on off metadata.
➲ /Help: get quick assistance.</b>"""

    SEND_METADATA = """
<b>--Metadata Settings:--</b>

➜ /metadata: Turn on or off metadata.

<b>Description</b> : Metadata will change MKV video files including all audio, streams, and subtitle titles."""

    SOURCE_TXT = """
<b>Hey,
 This is auto rename bot,
an open source telegram auto rename bot.</b>

Written in python with the help of :
[Pyrogram](https://github.com/pyrogram/pyrogram)
[Python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
And using [Mongo](https://cloud.mongodb.com) as database.

<b>Here is my source code :</b> [Github](https://github.com/codeflix_bots/autorenamebot)

Auto rename bot is licensed under the [MIT License](https://github.com/codeflix_bots/autorenamebot/blob/main/LICENSE).
© 2024 | [Support Chat](https://t.me/animes_sub_society), all rights reserved."""

    META_TXT = """
**Managing metadata for your videos and files**

**Various metadata:**

- **Title**: Descriptive title of the media.
- **Author**: The creator or owner of the media.
- **Artist**: The artist associated with the media.
- **Audio**: Title or description of audio content.
- **Subtitle**: Title of subtitle content.
- **Video**: Title or description of video content.

**Commands to turn on off metadata:**
➜ /metadata: Turn on or off metadata.

**Commands to set metadata:**

➜ /settitle: Set a custom title of media.
➜ /setauthor: Set the author.
➜ /setartist: Set the artist.
➜ /setaudio: Set audio title.
➜ /setsubtitle: Set subtitle title.
➜ /setvideo: Set video title.

**Example:** /settitle Your Title Here

**Use these commands to enrich your media with additional metadata information!**
"""