import html
import random, re
import requests as r

from telegram import Update, ParseMode, TelegramError, MAX_MESSAGE_LENGTH
from telegram.ext import Filters, CallbackContext, CommandHandler, run_async
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown

from SaitamaRobot.modules.helper_funcs.extraction import extract_user
from SaitamaRobot.modules.helper_funcs.filters import CustomFilters
from SaitamaRobot.modules.helper_funcs.alternate import typing_action
from SaitamaRobot import dispatcher, LOGGER, TIGER_USERS
from SaitamaRobot.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler

import SaitamaRobot.modules.helper_funcs.string_store as fun




@run_async
@typing_action
def slap(update, context):
    args = context.args
    msg = update.effective_message

    # reply to correct message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(
            msg.from_user.first_name, msg.from_user.id)
        

    user_id = extract_user(update.effective_message, args)
    if user_id:
        slapped_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(
                slapped_user.first_name, slapped_user.id
            )

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user

    temp = random.choice(fun.SLAP_TEMPLATES)
    item = random.choice(fun.ITEMS)
    hit = random.choice(fun.HIT)
    throw = random.choice(fun.THROW)

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@run_async
@typing_action
def hug(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(
            msg.from_user.first_name, msg.from_user.id
        )

    user_id = extract_user(update.effective_message, args)
    if user_id:
        hugged_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if hugged_user.username:
            user2 = "@" + escape_markdown(hugged_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(
                hugged_user.first_name, hugged_user.id
            )

    # if no target found, bot targets the sender
    else:
        user1 = "Awwh! [{}](tg://user?id={})".format(
            context.bot.first_name, context.bot.id
        )
        user2 = curr_user

    temp = random.choice(fun.HUG_TEMPLATES)
    hug = random.choice(fun.HUG)

    repl = temp.format(user1=user1, user2=user2, hug=hug)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)
    

@run_async
@typing_action
def dice(update, context):
    context.bot.sendDice(update.effective_chat.id)

@run_async
@typing_action
def recite(update, context):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.BEING_LOGICAL))



@run_async
@typing_action
def clapmoji(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to clap!")
    else:
        reply_text = "👏 "
        reply_text += message.reply_to_message.text.replace(" ", " 👏 ")
        reply_text += " 👏"
        message.reply_to_message.reply_text(reply_text)


@run_async
@typing_action
def goodnight(update, context):
    message = update.effective_message
    reply = random.choice(fun.GDNIGHT)
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


@run_async
@typing_action
def goodmorning(update, context):
    message = update.effective_message
    reply = random.choice(fun.GDMORNING)
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)

__help__ = """
*Some dank memes for fun or whatever!
 ✪ `/slap`: Slap a user, or get slapped if not a reply.
 ✪ `/hug`: Hug a user warmly, or get hugged if not a reply.
 ✪ `/roll`: Rolls a dice.
 ✪ `/clap`: Claps on someones message!
 
"""

__mod_name__ = "LOL Memes"


SLAP_HANDLER = DisableAbleCommandHandler("slap", slap)
HUG_HANDLER = DisableAbleCommandHandler("hug", hug)
DICE_HANDLER = DisableAbleCommandHandler("roll", dice)
CLAP_HANDLER = DisableAbleCommandHandler("clap", clapmoji)
GDMORNING_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(gm|good morning)"), goodmorning, friendly="goodmorning"
)
GDNIGHT_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(gn|good night)"), goodnight, friendly="goodnight"
)

dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(HUG_HANDLER)
dispatcher.add_handler(DICE_HANDLER)
dispatcher.add_handler(CLAP_HANDLER)
dispatcher.add_handler(GDMORNING_HANDLER)
dispatcher.add_handler(GDNIGHT_HANDLER)

#this line should not be removed! or else a opt will be created !! Taken from saitaima and preven's repo and contributed here! those things which are not given here are either
#tested not working or logs error in this repo !
