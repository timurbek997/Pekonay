
import json, os, random, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler

# Bot sozlamalari
BOT_TOKEN = "997157878:AAHAXk2jskNNh1I50wCYmojlbNuBcU9tcxM"
ADMIN_ID = 1170125862

# Fayllar
MEMORY_FILE = "memory.json"
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"

# Xotiralar
memory = json.load(open(MEMORY_FILE)) if os.path.exists(MEMORY_FILE) else {}
users = json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else []
groups = json.load(open(GROUPS_FILE)) if os.path.exists(GROUPS_FILE) else []

def save_memory():
    json.dump(memory, open(MEMORY_FILE, "w"))

def save_users():
    json.dump(users, open(USERS_FILE, "w"))

def save_groups():
    json.dump(groups, open(GROUPS_FILE, "w"))

# Foydalanuvchi xabarini qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if user_id not in users:
        users.append(user_id)
        save_users()

    if msg.chat.type in ["group", "supergroup"]:
        if chat_id not in groups:
            groups.append(chat_id)
            save_groups()

    # Yodlash
    if msg.reply_to_message and msg.reply_to_message.text:
        question = msg.reply_to_message.text.strip().lower()
        answer = msg.text.strip()
        if question not in memory:
            memory[question] = []
        if answer not in memory[question]:
            memory[question].append(answer)
            save_memory()

    # Javob berish
    text = msg.text.strip().lower()
    if text in memory:
        reply = random.choice(memory[text])
        await msg.reply_text(reply)

# Admin panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz.")
        return
    keyboard = [
        [InlineKeyboardButton("📢 Reklama (matn)", callback_data="ad_text")],
        [InlineKeyboardButton("🖼 Rasm reklama", callback_data="ad_photo")],
        [InlineKeyboardButton("🎥 Video reklama", callback_data="ad_video")],
        [InlineKeyboardButton("📊 Statistika", callback_data="show_stats")]
    ]
    await update.message.reply_text("Admin paneli:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback tugmalar
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "show_stats":
        await show_stats(update, context, via_callback=True)
        return

    context.user_data["ad_type"] = data
    await query.message.reply_text("Iltimos, reklama kontentini yuboring (matn, rasm, video)")

# Reklama yuborish
async def handle_ad_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    ad_type = context.user_data.get("ad_type")
    if not ad_type:
        return

    sent = 0
    for user_id in users:
        try:
            if ad_type == "ad_text":
                await context.bot.send_message(chat_id=user_id, text=update.message.text)
            elif ad_type == "ad_photo":
                photo = update.message.photo[-1].file_id
                await context.bot.send_photo(chat_id=user_id, photo=photo, caption=update.message.caption)
            elif ad_type == "ad_video":
                video = update.message.video.file_id
                await context.bot.send_video(chat_id=user_id, video=video, caption=update.message.caption)
            await asyncio.sleep(0.1)
            sent += 1
        except:
            continue

    await update.message.reply_text(f"✅ Yuborildi: {sent} foydalanuvchiga")
    context.user_data["ad_type"] = None

# Statistika
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, via_callback=False):
    if update.effective_user.id != ADMIN_ID:
        if not via_callback:
            await update.message.reply_text("Siz admin emassiz.")
        return

    users_count = len(users)
    groups_count = len(groups)
    learned_phrases = len(memory)

    msg = (
    f"📊 <b>Statistika</b>:\n"
    f"👤 Foydalanuvchilar: <b>{users_count}</b>\n"
    f"👥 Guruhlar: <b>{groups_count}</b>\n"
    f"🧠 Yodlangan so‘zlar: <b>{learned_phrases}</b>"
)
    if via_callback:
        await update.callback_query.message.reply_text(msg, parse_mode="HTML")
    else:
        await update.message.reply_text(msg, parse_mode="HTML")

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CommandHandler("statistika", show_stats))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(MessageHandler(filters.ALL & filters.User(ADMIN_ID), handle_ad_content))
app.run_polling()
