import logging
import time

from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from LaylaRobot import DRAGONS as SUDO_USERS
from LaylaRobot import pgram
from LaylaRobot.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@Client.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗@ {channel} kanalıvıza qoşulun və 'Səsimi Aç' düyməsini yenidən basın.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Admin başqa bir səbəbə görə səssizləşdirdi.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} özünü səssizləşdirməyə çalışır, amma səsini aça bilmirəm, çünki bu söhbətdə admin deyiləm, məni yenidən admin et.**\n__#bu sohbeti tərk edirəm...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="Xəbərdarlıq: Danışa bildiyiniz zaman düyməni basmayın.",
                    show_alert=True,
                )


@Client.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Xoş gəldin {} 🙏 \n \n **Siz bizimsiniz @{} *Kanal hələ qoşulmayıb* 😭 \n Xahiş edirəm altındakı Qoşulmağı edin**UNMUTE ME** Düyməsinə toxunun. \n \n **[👉 Sizin Kanal 👈](https://t.me/{})**".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "UnMute Me", callback_data="onUnMuteRequest"
                                    )
                                ]
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **Bu Admindəyəm qətiyyən deyil .. ** \ n__Mənə Adminlə İcazələri qadağan et Yenidən cəhd edin \n#Ending FSub...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"❗ **Menim @{channel} Bir Admində Heç Yoxdur. ** \ n__Mən Admin Deela'yı geri əlavə et.\n#Leaving this chat...__",
                )


@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **Force Abunə Olunsa Uğursuzdur.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Unmuting all members who are muted by me...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **Mənim elədim bütün üzvlər səssizdir.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **I am not an admin in this chat.**\n__I can't unmute members because i am not an admin in this chat make me admin with ban user permission.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled, all the group members have to subscribe this [channel](https://t.me/{input_str}) in order to send messages in this group.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{input_str}). Add me as a admin in order to enable ForceSubscribe.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Invalid Channel Username.**")
                except Exception as err:
                    message.reply_text(f"❗ **ERROR:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("❌ **Force Subscribe is disabled in this chat.**")
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )


__help__ = """
*ForceSubscribe:*
*Channel Manageer Inbuilt*
✪ Bir və ya bir neçə kanala abunə olana qədər qrup üzvlərinizə mesaj göndərməyi dayandıra bilərəm.
✪ Üzvlər kanalınıza qoşulmayıbsa, mən onları səssizləşdirib kanala qoşulmalarını söyləyə bilərəm və bir düyməyə basaraq səssizləşdirə bilərəm.
*Qurmaq*
1) Hər şeydən əvvəl məni qrupa qadağan istifadəçilərinin icazəsi ilə admin və kanalda admin olaraq əlavə edin.
Not!: yalnız qrupun yaradıcısı məni qura bilər və bunu etmədiyim təqdirdə yenidən abunə olmağa icazə verməyəcəyəm.
 
*Əmrlər*
• `/ForceSubscribe - Mövcud parametrləri əldə etmək..
• `/ForceSubscribe no/off/disable - ForceSubscribe’i çevirmək üçün.
• `/ForceSubscribe {kanal adı} - Kanalı açmaq və qurmaq üçün.
• `/ForceSubscribe clear - səsimi susduran bütün üzvlərin səsini çıxartmaq.
Not: /FSub digər ləqəbidir /ForceSubscribe
 
"""
__mod_name__ = "Subscribe"
