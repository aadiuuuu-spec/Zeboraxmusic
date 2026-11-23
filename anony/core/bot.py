# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import pyrogram

from anony import config, logger


class Bot(pyrogram.Client):
    def __init__(self):
        super().__init__(
            name="anony",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
        )
        self.owner = config.OWNER_ID
        self.logger = config.LOGGER_ID
        self.bl_users = pyrogram.filters.user()
        self.sudoers = pyrogram.filters.user(self.owner)

    async def boot(self):
        """
        Starts the bot and performs initial setup.

        Raises:
            SystemExit: If the bot fails to access the log group or is not an administrator in the logger group.
        """
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        # Publish the Music bot's own command catalogue to Telegram's "/" menu.
        commands = [
            pyrogram.types.BotCommand("play", "ᴘʟᴀʏ ᴀ sᴏɴɢ ᴏʀ ᴘʟᴀʏʟɪsᴛ"),
            pyrogram.types.BotCommand("playforce", "ᴘʟᴀʏ ɴᴏᴡ, ᴏᴠᴇʀʀɪᴅɪɴɢ ᴛʜᴇ ǫᴜᴇᴜᴇ"),
            pyrogram.types.BotCommand("vplay", "ᴘʟᴀʏ ᴀ ᴠɪᴅᴇᴏ"),
            pyrogram.types.BotCommand("vplayforce", "ᴘʟᴀʏ ᴀ ᴠɪᴅᴇᴏ ɴᴏᴡ"),
            pyrogram.types.BotCommand("pause", "ᴘᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ sᴛʀᴇᴀᴍ"),
            pyrogram.types.BotCommand("resume", "ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴘᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ"),
            pyrogram.types.BotCommand("skip", "sᴋɪᴘ ᴛᴏ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ"),
            pyrogram.types.BotCommand("queue", "ᴠɪᴇᴡ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ ǫᴜᴇᴜᴇ"),
            pyrogram.types.BotCommand("playing", "sʜᴏᴡ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ"),
            pyrogram.types.BotCommand("loop", "sᴇᴛ ᴛʀᴀᴄᴋ ʀᴇᴘᴇᴀᴛ ᴄᴏᴜɴᴛ"),
            pyrogram.types.BotCommand("seek", "sᴇᴇᴋ ғᴏʀᴡᴀʀᴅ ɪɴ ᴛʜᴇ ᴛʀᴀᴄᴋ"),
            pyrogram.types.BotCommand("seekback", "sᴇᴇᴋ ʙᴀᴄᴋᴡᴀʀᴅ ɪɴ ᴛʜᴇ ᴛʀᴀᴄᴋ"),
            pyrogram.types.BotCommand("stop", "sᴛᴏᴘ ᴘʟᴀʏʙᴀᴄᴋ ᴀɴᴅ ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ"),
            pyrogram.types.BotCommand("autoplay", "ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ"),
            pyrogram.types.BotCommand("auth", "ᴀᴜᴛʜᴏʀɪsᴇ ᴀ ᴜsᴇʀ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ᴍᴜsɪᴄ"),
            pyrogram.types.BotCommand("unauth", "ʀᴇᴍᴏᴠᴇ ᴀ ᴜsᴇʀ's ᴍᴜsɪᴄ ᴀᴄᴄᴇss"),
            pyrogram.types.BotCommand("authlist", "sʜᴏᴡ ᴀᴜᴛʜᴏʀɪsᴇᴅ ᴜsᴇʀs"),
            pyrogram.types.BotCommand("admincache", "ʀᴇʟᴏᴀᴅ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ"),
            pyrogram.types.BotCommand("settings", "ᴏᴘᴇɴ ɢʀᴏᴜᴘ ᴍᴜsɪᴄ sᴇᴛᴛɪɴɢs"),
            pyrogram.types.BotCommand("lang", "ᴄʜᴀɴɢᴇ ʙᴏᴛ ʟᴀɴɢᴜᴀɢᴇ"),
            pyrogram.types.BotCommand("help", "ᴠɪᴇᴡ ᴍᴜsɪᴄ ʙᴏᴛ ʜᴇʟᴘ"),
            pyrogram.types.BotCommand("ping", "ᴄʜᴇᴄᴋ ʙᴏᴛ ʀᴇsᴘᴏɴsᴇ ᴀɴᴅ sᴛᴀᴛᴜs"),
            pyrogram.types.BotCommand("alive", "ᴄʜᴇᴄᴋ ᴡʜᴇᴛʜᴇʀ ʙᴏᴛ ɪs ᴏɴʟɪɴᴇ"),
            pyrogram.types.BotCommand("stats", "ᴠɪᴇᴡ ɢʀᴏᴜᴘ ᴀɴᴅ ʙᴏᴛ sᴛᴀᴛs"),
            pyrogram.types.BotCommand("start", "sᴛᴀʀᴛ ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ"),
            pyrogram.types.BotCommand("playmode", "ᴏᴘᴇɴ ᴘʟᴀʏʙᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ sᴇᴛᴛɪɴɢs"),
            pyrogram.types.BotCommand("t", "ᴀᴅᴅ ᴀ ᴜsᴇʀ ᴛᴏ ᴛʜᴇ ᴏᴡɴᴇʀ's ᴛᴀʀɢᴇᴛ ʟɪsᴛ"),
            pyrogram.types.BotCommand("r", "ʀᴇʟᴇᴀsᴇ ᴀ ᴛᴀʀɢᴇᴛᴇᴅ ᴜsᴇʀ"),
            pyrogram.types.BotCommand("targets", "sʜᴏᴡ ᴛᴀʀɢᴇᴛᴇᴅ ᴜsᴇʀs"),
            pyrogram.types.BotCommand("banall", "ʙᴀɴ ɴᴏɴ-ᴀᴅᴍɪɴ ᴍᴇᴍʙᴇʀs (ᴏᴡɴᴇʀ ᴏɴʟʏ)"),
            pyrogram.types.BotCommand("sbanall", "sᴛᴏᴘ ᴛʜᴇ ᴀᴄᴛɪᴠᴇ ʙᴀɴᴀʟʟ ᴛᴀsᴋ"),
        ]
        await self.set_bot_commands(
            commands, scope=pyrogram.types.BotCommandScopeDefault()
        )
        await self.set_bot_commands(
            commands, scope=pyrogram.types.BotCommandScopeAllGroupChats()
        )

        try:
            await self.send_message(self.logger, "Bot Started")
            get = await self.get_chat_member(self.logger, self.id)
        except Exception as ex:
            raise SystemExit(f"Bot has failed to access the log group: {self.logger}\nReason: {ex}")

        if get.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit("Please promote the bot as an admin in logger group.")
        logger.info(f"Bot started as @{self.username}")

    async def exit(self):
        """
        Asynchronously stops the bot.
        """
        await super().stop()
        logger.info("Bot stopped.")
