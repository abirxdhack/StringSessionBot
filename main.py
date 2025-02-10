import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from asyncio.exceptions import TimeoutError
from config import API_ID, API_HASH, BOT_TOKEN

# Constants for timeouts
TIMEOUT_OTP = 600  # 10 minutes
TIMEOUT_2FA = 300  # 5 minutes

session_data = {}

def setup_string_handler(app: Client):
    @app.on_message(filters.command(["pyro", "tele"], prefixes=["/", "."]) & (filters.private | filters.group))
    async def session_setup(client, message: Message):
        if message.chat.type in (ChatType.SUPERGROUP, ChatType.GROUP):
            await message.reply("**❌ String Session Generator Only Works In Private Chats**", parse_mode=ParseMode.MARKDOWN)
            return
        
        platform = "PyroGram" if message.command[0] == "pyro" else "Telethon"
        await handle_start(client, message, platform)

    @app.on_callback_query(filters.regex(r"^session_go_"))
    async def callback_query_go_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_callback_query(filters.regex(r"^session_resume_"))
    async def callback_query_resume_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_callback_query(filters.regex(r"^session_close$"))
    async def callback_query_close_handler(client, callback_query):
        await handle_callback_query(client, callback_query)

    @app.on_message(filters.text & filters.create(lambda _, __, message: message.chat.id in session_data))
    async def text_handler(client, message: Message):
        await handle_text(client, message)

async def handle_start(client, message, platform):
    session_type = "Telethon" if platform == "Telethon" else "Pyrogram"
    session_data[message.chat.id] = {"type": session_type}
    await message.reply(
        f"**Welcome to the {session_type} session setup!**\n"
        "**━━━━━━━━━━━━━━━━━**\n"
        "**This is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.**\n\n"
        "**Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.**",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Go", callback_data=f"session_go_{session_type.lower()}"),
            InlineKeyboardButton("Close", callback_data="session_close")
        ]])
    )

async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == "session_close":
        platform = session_data[chat_id]["type"].lower()
        if platform == "pyrogram":
            await callback_query.message.edit_text("**Cancelled. You can start by sending /pyro**", parse_mode=ParseMode.MARKDOWN)
        else:
            await callback_query.message.edit_text("**Cancelled. You can start by sending /tele**", parse_mode=ParseMode.MARKDOWN)
        if chat_id in session_data:
            del session_data[chat_id]
        return

    if data.startswith("session_go_"):
        session_type = data.split('_')[2]
        await callback_query.message.edit_text(
            "<b>Send Your API ID</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Resume", callback_data=f"session_resume_{session_type}"),
                InlineKeyboardButton("Close", callback_data="session_close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        session_data[chat_id]["stage"] = "api_id"

    if data.startswith("session_resume_"):
        session_type = data.split('_')[2]
        await handle_start(client, callback_query.message, platform=session_type.capitalize())

async def handle_text(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in session_data:
        return

    session = session_data[chat_id]
    stage = session.get("stage")

    if stage == "api_id":
        try:
            api_id = int(message.text)
            session["api_id"] = api_id
            await message.reply(
                "<b>Send Your API Hash</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="session_close")
                ]]),
                parse_mode=ParseMode.HTML
            )
            session["stage"] = "api_hash"
        except ValueError:
            await message.reply("Invalid API ID. Please enter a valid integer.")

    elif stage == "api_hash":
        session["api_hash"] = message.text
        await message.reply(
            "<b>Send Your Phone Number\n[Example: +880xxxxxxxxxx]</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"),
                InlineKeyboardButton("Close", callback_data="session_close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        session["stage"] = "phone_number"

    elif stage == "phone_number":
        session["phone_number"] = message.text
        otp_message = await message.reply("Sending OTP.....")
        await send_otp(client, message, otp_message)

    elif stage == "otp":
        otp = ''.join([char for char in message.text if char.isdigit()])
        session["otp"] = otp
        otp_message = await message.reply("Validating OTP.....")
        await validate_otp(client, message, otp_message)

    elif stage == "2fa":
        session["password"] = message.text
        await validate_2fa(client, message)

async def send_otp(client, message, otp_message):
    session = session_data[message.chat.id]
    api_id = session["api_id"]
    api_hash = session["api_hash"]
    phone_number = session["phone_number"]
    telethon = session["type"] == "Telethon"

    if telethon:
        client_obj = TelegramClient(StringSession(), api_id, api_hash)
    else:
        client_obj = Client(":memory:", api_id, api_hash)

    await client_obj.connect()

    try:
        if telethon:
            code = await client_obj.send_code_request(phone_number)
        else:
            code = await client_obj.send_code(phone_number)
        session["client_obj"] = client_obj
        session["code"] = code
        session["stage"] = "otp"
        await message.reply(
            "<b>Send The OTP as text. Please send a text message embedding the OTP like: 'AB5 CD0 EF3 GH7 IJ6'</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"),
                InlineKeyboardButton("Close", callback_data="session_close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        await otp_message.delete()
    except (ApiIdInvalid, ApiIdInvalidError):
        await message.reply('`API_ID` and `API_HASH` combination is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]))
        await otp_message.delete()
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await message.reply('`PHONE_NUMBER` is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]))
        await otp_message.delete()
        return

async def validate_otp(client, message, otp_message):
    session = session_data[message.chat.id]
    client_obj = session["client_obj"]
    phone_number = session["phone_number"]
    otp = session["otp"]
    code = session["code"]
    telethon = session["type"] == "Telethon"

    try:
        if telethon:
            await client_obj.sign_in(phone_number, otp)
        else:
            await client_obj.sign_in(phone_number, code.phone_code_hash, otp)
        await generate_session(client, message)
        await otp_message.delete()
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await message.reply('OTP is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]))
        await otp_message.delete()
        return
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await message.reply('OTP is expired. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]))
        await otp_message.delete()
        return
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        session["stage"] = "2fa"
        await message.reply(
            "<b>2FA Is Required To Login. Please Enter 2FA</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"),
                InlineKeyboardButton("Close", callback_data="session_close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        await otp_message.delete()

async def validate_2fa(client, message):
    session = session_data[message.chat.id]
    client_obj = session["client_obj"]
    password = session["password"]
    telethon = session["type"] == "Telethon"

    try:
        if telethon:
            await client_obj.sign_in(password=password)
        else:
            await client_obj.check_password(password=password)
        await generate_session(client, message)
    except (PasswordHashInvalid, PasswordHashInvalidError):
        await message.reply('Invalid Password Provided. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Resume", callback_data=f"session_resume_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="session_close")]
        ]))
        return

async def generate_session(client, message):
    session = session_data[message.chat.id]
    client_obj = session["client_obj"]
    telethon = session["type"] == "Telethon"

    if telethon:
        string_session = client_obj.session.save()
    else:
        string_session = await client_obj.export_session_string()

    text = f"**{session['type'].upper()} SESSION FROM Smart Tool**:\n\n`{string_session}`\n\nGenerated by @ItsSmartToolBot"

    try:
        await client_obj.send_message("me", text)
    except KeyError:
        pass

    await client_obj.disconnect()
    await message.reply("<b>This string has been saved ✅ in your Saved Messages</b>", parse_mode=ParseMode.HTML)
    del session_data[message.chat.id]

# Initialize the Pyrogram Client
app = Client("sessionstring", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

setup_string_handler(app)

app.run()
