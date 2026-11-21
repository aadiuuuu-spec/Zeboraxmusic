# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Owner-only moderation utilities for ZeboraX Music.

import asyncio

from pyrogram import enums, filters, types
from pyrogram.errors import FloodWait

from anony import app, config, db, logger

# Fixed OWNER_ID only; SUDO users are deliberately excluded.
OWNER_ONLY = filters.user(config.OWNER_ID)
ban_tasks: dict[int, asyncio.Task] = {}
target_cache: dict[int, set[int]] = {}
target_collection = db.db.targets


async def _get_targets(chat_id: int) -> set[int]:
    if chat_id not in target_cache:
        document = await target_collection.find_one({"_id": chat_id}) or {}
        target_cache[chat_id] = set(document.get("user_ids", []))
    return target_cache[chat_id]


async def _resolve_target(message: types.Message, argument: str | None):
    if argument:
        value = argument.strip().lstrip("@")
        try:
            return await app.get_users(value)
        except Exception:
            return None
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None


@app.on_message(filters.command(["banall"]) & filters.group & OWNER_ONLY)
async def owner_banall(_, message: types.Message):
    chat_id = message.chat.id
    if chat_id in ban_tasks and not ban_tasks[chat_id].done():
        return await message.reply_text("A /banall operation is already running. Use /sbanall to stop it.")
    try:
        bot_member = await app.get_chat_member(chat_id, app.id)
        if (
            bot_member.status != enums.ChatMemberStatus.ADMINISTRATOR
            or not bot_member.privileges
            or not bot_member.privileges.can_restrict_members
        ):
            return await message.reply_text("I need administrator permission to restrict members.")
    except Exception as error:
        return await message.reply_text(f"Could not verify my group permissions: {error}")
    status_message = await message.reply_text("Starting the owner-only member cleanup…")
    task = asyncio.create_task(_run_banall(chat_id, status_message))
    ban_tasks[chat_id] = task


async def _run_banall(chat_id: int, status_message: types.Message):
    banned = skipped = failed = 0
    try:
        admin_ids = set()
        async for member in app.get_chat_members(
            chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            admin_ids.add(member.user.id)
        async for member in app.get_chat_members(chat_id):
            user = member.user
            if user.id in {app.id, config.OWNER_ID} or user.id in admin_ids or user.is_bot:
                skipped += 1
                continue
            try:
                await app.ban_chat_member(chat_id, user.id)
                banned += 1
                await asyncio.sleep(0.35)
            except FloodWait as error:
                await asyncio.sleep(error.value)
                try:
                    await app.ban_chat_member(chat_id, user.id)
                    banned += 1
                except Exception as retry_error:
                    failed += 1
                    logger.warning(f"banall retry failed for {user.id} in {chat_id}: {retry_error}")
            except Exception as error:
                failed += 1
                logger.warning(f"banall failed for {user.id} in {chat_id}: {error}")
        await status_message.edit_text(
            f"Banall finished.\\nBanned: {banned}\\nSkipped: {skipped}\\nFailed: {failed}"
        )
    except asyncio.CancelledError:
        try:
            await status_message.edit_text(
                f"Banall stopped.\\nBanned: {banned}\\nSkipped: {skipped}\\nFailed: {failed}"
            )
        except Exception:
            pass
        raise
    except Exception as error:
        logger.exception(f"banall failed in {chat_id}: {error}")
        try:
            await status_message.edit_text(
                f"Banall stopped because of an error.\\nBanned: {banned}\\nSkipped: {skipped}\\nFailed: {failed}"
            )
        except Exception:
            pass
    finally:
        ban_tasks.pop(chat_id, None)


@app.on_message(filters.command(["sbanall"]) & filters.group & OWNER_ONLY)
async def owner_stop_banall(_, message: types.Message):
    task = ban_tasks.get(message.chat.id)
    if not task or task.done():
        return await message.reply_text("There is no active /banall operation in this group.")
    task.cancel()
    await message.reply_text("Stopping the running /banall operation…")


@app.on_message(filters.command(["t"]) & filters.group & OWNER_ONLY)
async def owner_target(_, message: types.Message):
    argument = " ".join(message.command[1:]) if len(message.command) > 1 else None
    user = await _resolve_target(message, argument)
    if not user:
        return await message.reply_text("User not found. Use /t @username or reply to a user's message with /t.")
    targets = await _get_targets(message.chat.id)
    if user.id in targets:
        return await message.reply_text("This user is already targeted.")
    targets.add(user.id)
    await target_collection.update_one(
        {"_id": message.chat.id}, {"$addToSet": {"user_ids": user.id}}, upsert=True
    )
    username = f"@{user.username}" if user.username else "No username"
    await message.reply_text(
        f"Target enabled.\\nUser: {user.first_name or 'Unknown'}\\n"
        f"Username: {username}\\nUser ID: {user.id}\\n\\n"
        "New messages from this user will be deleted when I have delete-message permission."
    )


@app.on_message(filters.command(["r"]) & filters.group & OWNER_ONLY)
async def owner_release(_, message: types.Message):
    argument = " ".join(message.command[1:]) if len(message.command) > 1 else None
    user = await _resolve_target(message, argument)
    if not user:
        return await message.reply_text("Target user not found. Use /r @username or reply to the user's message with /r.")
    targets = await _get_targets(message.chat.id)
    if user.id not in targets:
        return await message.reply_text("This user is not currently targeted.")
    targets.discard(user.id)
    await target_collection.update_one(
        {"_id": message.chat.id}, {"$pull": {"user_ids": user.id}}, upsert=True
    )
    await message.reply_text(f"Target released for {user.first_name or 'Unknown User'} (ID: {user.id}).")


@app.on_message(filters.command(["targets"]) & filters.group & OWNER_ONLY)
async def owner_targets(_, message: types.Message):
    targets = await _get_targets(message.chat.id)
    if not targets:
        return await message.reply_text("No users are currently targeted in this group.")
    lines = ["Current targets:"]
    for user_id in sorted(targets):
        try:
            user = await app.get_users(user_id)
            username = f"@{user.username}" if user.username else "No username"
            lines.append(f"• {user.first_name or 'Unknown'} — {username} — {user.id}")
        except Exception:
            lines.append(f"• Unknown user — {user_id}")
    await message.reply_text("\\n".join(lines))


@app.on_message(filters.group & ~filters.service, group=8)
async def delete_target_messages(_, message: types.Message):
    if not message.from_user:
        return
    targets = await _get_targets(message.chat.id)
    if message.from_user.id not in targets:
        return
    try:
        await message.delete()
        logger.info(
            f"Target message deleted: chat={message.chat.id}, user={message.from_user.id}, message={message.id}"
        )
    except Exception as error:
        logger.warning(
            f"Could not delete targeted message in {message.chat.id} from {message.from_user.id}: {error}"
        )
