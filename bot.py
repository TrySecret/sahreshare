#(©)Codexbotz

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT

 from helper_func import is_vip, add_vip_user
 import os
 from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

 @Client.on_message(filters.command("start") & filters.private)
 async def start_handler(client, message):
     keyboard = InlineKeyboardMarkup([[
-        InlineKeyboardButton("Donasi", url="https://trakteer.id/username")
+        InlineKeyboardButton("💸 Donasi via Trakteer", url=os.getenv("TRAKTEER_URL"))
     ]])
     await message.reply(os.getenv("START_MESSAGE", "Halo! Silakan donasi dulu untuk akses VIP."), reply_markup=keyboard)

+ @Client.on_message(filters.command("verify") & filters.private)
+ async def manual_verify(client, message):
+     await add_vip_user(message.from_user.id)
+     await message.reply("✅ Verifikasi manual berhasil! Kamu sekarang VIP.")

 @Client.on_message(filters.command("getfile") & filters.private)
 async def send_file(client, message):
     uid = message.from_user.id
+    if not await is_vip(uid):
+        keyboard = InlineKeyboardMarkup([[
+            InlineKeyboardButton("💸 Donasi via Trakteer", url=os.getenv("TRAKTEER_URL"))
+        ]])
+        return await message.reply("🚫 Akses hanya untuk VIP. Silakan donasi dulu.", reply_markup=keyboard)
     file_id = "YOUR_FILE_ID"
-    await client.send_document(message.chat.id, file_id)
+    await client.send_document(
+        chat_id=message.chat.id,
+        document=file_id,
+        caption="📄 File VIP kamu",
+        protect_content=True
+    )

ascii_art = """
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
                sys.exit()
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
        print(ascii_art)
        print("""Welcome to CodeXBotz File Sharing Bot""")
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
