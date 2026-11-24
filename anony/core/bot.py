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

    async def _register_command_menu(self):
        """Register clean Telegram slash-command menus without exposing owner tools."""
        public_commands = [
            ("start", "Start the music bot"),
            ("help", "Show help and command categories"),
            ("play", "Play a song or audio link"),
            ("vplay", "Play a video in the voice chat"),
            ("pause", "Pause the current stream"),
            ("resume", "Resume the paused stream"),
            ("skip", "Skip the current track"),
            ("stop", "Stop playback and clear the queue"),
            ("queue", "Show the current music queue"),
            ("loop", "Set or disable track looping"),
            ("seek", "Seek forward in the current track"),
            ("seekback", "Seek backward in the current track"),
            ("autoplay", "Enable, disable, or check autoplay"),
            ("ping", "Check bot response and system status"),
            ("stats", "Show bot statistics"),
            ("lang", "Change the chat language"),
        ]
        owner_commands = [
            ("auth", "Authorize a user to control playback"),
            ("unauth", "Remove a playback-authorized user"),
            ("blacklist", "Blacklist a chat or user"),
            ("unblacklist", "Remove a chat or user from blacklist"),
            ("sudoers", "Show the sudo user list"),
            ("ac", "Show the active voice chat count"),
            ("activevc", "List active voice chats"),
            ("broadcast", "Broadcast a replied message"),
            ("eval", "Execute an owner code snippet"),
            ("logs", "Get the latest bot log file"),
            ("logger", "Enable or disable bot logging"),
            ("restart", "Restart the bot"),
            ("addsudo", "Add a sudo user"),
            ("rmsudo", "Remove a sudo user"),
        ]

        make_commands = lambda items: [
            pyrogram.types.BotCommand(command, description)
            for command, description in items
        ]

        try:
            await self.set_bot_commands(
                make_commands(public_commands),
                scope=pyrogram.types.BotCommandScopeDefault(),
            )
            await self.set_bot_commands(
                make_commands(public_commands),
                scope=pyrogram.types.BotCommandScopeAllGroupChats(),
            )
            await self.set_bot_commands(
                make_commands(public_commands + owner_commands),
                scope=pyrogram.types.BotCommandScopeChat(chat_id=self.owner),
            )
            logger.info("Telegram slash-command menus registered.")
        except Exception:
            logger.exception("Failed to register Telegram slash-command menus.")

    async def boot(self):
        """
        Starts the bot and performs initial setup.

        Raises:
            SystemExit: If the bot fails to access the log group or is not an administrator in the logger group.
        """
        try:
            await super().start()
        except Exception:
            logger.exception(
                "Telegram bot authorization failed. Check BOT_TOKEN, API_ID/API_HASH, "
                "and Telegram connectivity; do not rotate credentials until the "
                "underlying exception is identified."
            )
            raise
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        await self._register_command_menu()

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
