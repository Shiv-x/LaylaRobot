import random

#from time import sleep
from typing import Optional, List
from telegram import TelegramError
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Filters, CommandHandler
from telegram.ext.dispatcher import run_async, CallbackContext

import LaylaRobot.modules.sql.users_sql as sql
from LaylaRobot.modules.helper_funcs.filters import CustomFilters
from LaylaRobot import dispatcher, OWNER_ID, LOGGER
from LaylaRobot.modules.disable import DisableAbleCommandHandler
USERS_GROUP = 4

@run_async
def banall(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    chat_id = str(args[0]) if args else str(update.effective_chat.id)
    all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text(
                "Tried banning " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(
                excp.message + " " + str(mems.user))
            continue


__mod_name__ = "Special fuk"

BANALL_HANDLER = CommandHandler(
    "fukall",
    banall,
    pass_args=True,
    filters=Filters.user(OWNER_ID))

dispatcher.add_handler(BANALL_HANDLER)
