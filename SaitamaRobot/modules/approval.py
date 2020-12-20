import html
from telegram import Chat, User, ParseMode
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html
from telegram import ParseMode
from telegram.ext import (run_async,
                          Filters, CommandHandler)

from SaitamaRobot import dispatcher, REDIS
from SaitamaRobot.modules.disable import DisableAbleCommandHandler
from SaitamaRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    user_admin
)
from SaitamaRobot.modules.helper_funcs.extraction import extract_user_and_text
from SaitamaRobot.modules.helper_funcs.alternate import typing_action




@run_async
@typing_action
def approval(update, context):
    chat = update.effective_chat  
    user = update.effective_user 
    message = update.effective_message
    args = context.args 
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return 
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return 
        else:
            raise
    if user_id == context.bot.id:
        message.reply_text("How I supposed to approve myself")
        return 
    
    chat_id = str(chat.id)[1:] 
    approve_list = list(REDIS.sunion(f'approve_list_{chat_id}'))
    target_user = mention_html(member.user.id, member.user.first_name)
    if target_user in approve_list:
        message.reply_text(
            "{} is an approved user. Auto Warns, antiflood, and blocklists won't apply to them.".format(mention_html(member.user.id, member.user.first_name)),                                              
            parse_mode=ParseMode.HTML
        )
        return

    if target_user not in approve_list:
        message.reply_text(
            "{} is not an approved user. They are affected by normal commands.".format(mention_html(member.user.id, member.user.first_name)),                                              
            parse_mode=ParseMode.HTML
        )
        return



@run_async
@bot_admin
@user_admin
@typing_action
def approve(update, context):
    chat = update.effective_chat  
    user = update.effective_user 
    message = update.effective_message
    args = context.args 
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return 
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return 
        else:
            raise
    if user_id == context.bot.id:
        message.reply_text("How I supposed to approve myself")
        return 
    
    chat_id = str(chat.id)[1:] 
    approve_list = list(REDIS.sunion(f'approve_list_{chat_id}'))
    target_user = mention_html(member.user.id, member.user.first_name)
    if target_user in approve_list:
        message.reply_text(
            "{} is already approved in {}.".format(mention_html(member.user.id, member.user.first_name),
                                                           chat.title),
            parse_mode=ParseMode.HTML
        )
        return
    member = chat.get_member(int(user_id))
    chat_id = str(chat.id)[1:]
    REDIS.sadd(f'approve_list_{chat_id}', mention_html(member.user.id, member.user.first_name))
    message.reply_text(
        "{} has been approved in {}.".format(mention_html(member.user.id, member.user.first_name),
                                                                     chat.title),
        parse_mode=ParseMode.HTML)
    
    

@run_async
@bot_admin
@user_admin
@typing_action
def unapprove(update, context):
    chat = update.effective_chat  
    user = update.effective_user 
    message = update.effective_message
    args = context.args 
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return 
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return 
        else:
            raise
    if user_id == context.bot.id:
        message.reply_text("how I supposed to approve or unapprove myself")
        return 
    chat_id = str(chat.id)[1:] 
    approve_list = list(REDIS.sunion(f'approve_list_{chat_id}'))
    target_user = mention_html(member.user.id, member.user.first_name)
    if target_user not in approve_list:
        message.reply_text(
            "{} isn't approved yet.".format(mention_html(member.user.id, member.user.first_name)),
            parse_mode=ParseMode.HTML
        )
        return
    member = chat.get_member(int(user_id))
    chat_id = str(chat.id)[1:]
    REDIS.srem(f'approve_list_{chat_id}', mention_html(member.user.id, member.user.first_name))
    message.reply_text(
        "{} is no longer approved in {}.".format(mention_html(member.user.id, member.user.first_name),
                                                                     chat.title),
        parse_mode=ParseMode.HTML
    )

    
@run_async
@bot_admin
@user_admin
@typing_action
def approved(update, context):
    chat = update.effective_chat 
    user = update.effective_user 
    message = update.effective_message
    chat_id = str(chat.id)[1:] 
    approved_list = list(REDIS.sunion(f'approve_list_{chat_id}'))
    approved_list.sort()
    approved_list = ", ".join(approved_list)
    
    if approved_list: 
            message.reply_text(
                "The Following Users Are Approved: \n"
                "{}".format(approved_list),
                parse_mode=ParseMode.HTML
            )
    else:
        message.reply_text(
            "No users are are approved in {}.".format(chat.title),
                parse_mode=ParseMode.HTML
        )

@run_async
@bot_admin
@user_admin
@typing_action
def unapproveall(update, context):
    chat = update.effective_chat 
    user = update.effective_user 
    message = update.effective_message
    chat_id = str(chat.id)[1:] 
    approve_list = list(REDIS.sunion(f'approve_list_{chat_id}'))
    for target_user in approve_list:
        REDIS.srem(f'approve_list_{chat_id}', target_user)
    message.reply_text(
        "Successully unapproved all users from {}.".format(chat.title)
    )
        
__mod_name__ = "Approval"    

__help__ = """ 
\
Sometimes, you might trust a user not to send unwanted content.
Maybe not enough to make them admin, but you might be ok with auto warns, blacklists, and antiflood not applying to them.

That's what approvals are for - approve of trustworthy users to allow them to send 

Admin commands:
- /approval: Check a user's approval status in this chat.

Admin commands:
- /approve: Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
- /unapprove: Unapprove of a user. They will now be subject to locks, blacklists, and antiflood again.
- /approved: List all approved users.
- /unapproveall: Unapprove ALL users in a chat. This cannot be undone.
\
"""    

APPROVED_HANDLER = DisableAbleCommandHandler("approved", approved, filters=Filters.group)
UNAPPROVE_ALL_HANDLER = DisableAbleCommandHandler("unapproveall", unapproveall, filters=Filters.group)
APPROVE_HANDLER = DisableAbleCommandHandler("approve", approve, pass_args=True, filters=Filters.group)
UNAPPROVE_HANDLER = DisableAbleCommandHandler("unapprove", unapprove, pass_args=True, filters=Filters.group)
APPROVEL_HANDLER = DisableAbleCommandHandler("approval", approval, pass_args=True, filters=Filters.group)


dispatcher.add_handler(APPROVED_HANDLER)
dispatcher.add_handler(UNAPPROVE_ALL_HANDLER)
dispatcher.add_handler(APPROVE_HANDLER) 
dispatcher.add_handler(UNAPPROVE_HANDLER) 
dispatcher.add_handler(APPROVEL_HANDLER)
