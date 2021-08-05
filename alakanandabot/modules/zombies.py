from asyncio import sleep

from telethon import events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
from alakanandabot import telethn
from alakanandabot.events import register

from alakanandabot import telethn, OWNER_ID, DEV_USERS, DRAGONS, DEMONS

# =================== CONSTANT ===================

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)


UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

OFFICERS = [OWNER_ID] + DEV_USERS + DRAGONS + DEMONS

# Check if user has admin rights
async def is_administrator(user_id: int, message):
    admin = False
    async for user in telethn.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in OFFICERS:
            admin = True
            break
    return admin



@telethn.on(events.NewMessage(pattern="^[!/]zombies ?(.*)"))
async def zombies(event):
    """ For .zombies command, list all the zombies in a chat. """

    con = event.pattern_match.group(1).lower()
    del_u = 0
    del_status = "ഇത് ശവപ്പറമ്പ് അല്ല . ഇവിടെ ശവങ്ങൾ ഒന്നും ഇല്ല."

    if con != "clean":
        find_zombies = await event.respond("മരിച്ചവരെ തിരയുന്നു")
        async for user in event.client.iter_participants(event.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f"Found **{del_u}** Zombies In This Group.\
            \nClean Them By Using :\n👉 `/zombies clean`"
        await find_zombies.edit(del_status)
        return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not await is_administrator(user_id=event.from_id, message=event):
        await event.respond("നീ അഡ്മിൻ അല്ലടാ ചെറുക്കാ....ചെന്നു അഡ്മിൻ ആയിട്ട് വാ")
        return

    if not admin and not creator:
        await event.respond("എന്നെ ആദ്യം അഡ്മിൻ ആക്കൂ..എന്നിട്ട് പറ... ")
        return

    cleaning_zombies = await event.respond("⚰ ശവങ്ങളെ കുഴിച്ചു മൂടി കൊണ്ട് ഇരിക്കുന്നു")
    del_u = 0
    del_a = 0

    async for user in event.client.iter_participants(event.chat_id):
        if user.deleted:
            try:
                await event.client(
                    EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                await cleaning_zombies.edit("കാണാൻ ആണോ ഡാ എനിക്ക് അഡ്മിൻ പദവി... പെർമിഷൻ താടാ...")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"`{del_u} ശവങ്ങളെ കുഴിച്ച് മൂടി` "

    if del_a > 0:
        del_status = f"Cleaned `{del_u}` Zombies \
        \n`{del_a}` '{del_u}',ശവങ്ങളെ കുഴിച്ച് മൂടി!"

    await cleaning_zombies.edit(del_status)
