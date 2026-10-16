import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ВНИМАНИЕ: Обязательно замените значения ниже на свои внутри кавычек/чисел!
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"  
ADMIN_ID = 123456789                  
CHANNEL_ID = -1001234567890           

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Привет! Отправь мне любое сообщение, и я анонимно передам его админу. 🤫")
    else:
        await message.answer("Привет, админ! Я готов принимать сообщения.")

@dp.message(F.text)
async def handle_anonymous_text(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return

    first_name = message.from_user.first_name or "Нет имени"
    last_name = message.from_user.last_name or ""
    nickname = f"{first_name} {last_name}".strip()
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    user_text = message.text

    admin_report = (
        f"📩 **Новое анонимное сообщение!**\n\n"
        f"👤 **Имя/Никнейм:** {nickname}\n"
        f"🔗 **Юзернейм:** {username}\n"
        f"🆔 **ID:** `{message.from_user.id}`\n\n"
        f"📝 **Текст сообщения:**\n{user_text}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="📢 Опубликовать в канал", callback_data="publish"))

    await bot.send_message(chat_id=ADMIN_ID, text=admin_report, parse_mode="Markdown", reply_markup=builder.as_markup())
    await message.answer("Отлично! Твое сообщение доставлено. 🕵️‍♂️")

@dp.callback_query(F.data == "publish")
async def process_publish_callback(callback: types.CallbackQuery):
    original_text = callback.message.text
    if "Текст сообщения:" in original_text:
        post_text = original_text.split("Текст сообщения:")[-1].strip()
    else:
        post_text = original_text

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=f"📢 **Анонимное сообщение:**\n\n{post_text}", parse_mode="Markdown")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Успешно опубликовано в канал!")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
