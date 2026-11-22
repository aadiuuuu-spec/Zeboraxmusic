# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db, lang
from anony.helpers import can_manage_vc


@app.on_message(filters.command(["autoplay"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _autoplay(_, m: types.Message):
    if len(m.command) == 1:
        key = "autoplay_status_on" if await db.get_autoplay(m.chat.id) else "autoplay_status_off"
        return await m.reply_text(m.lang[key])

    value = m.command[1].lower()
    if value not in ["on", "off"]:
        return await m.reply_text(m.lang["autoplay_usage"])

    enabled = value == "on"
    await db.set_autoplay(m.chat.id, enabled)
    key = "autoplay_on" if enabled else "autoplay_off"
    await m.reply_text(m.lang[key])
