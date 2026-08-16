import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

ADMIN_ID = 387155012

reply_mode = {}

BASE_DIR = Path(__file__).resolve().parent
TRIBE_MATERIALS = {
    "uk": {
        "pdf": BASE_DIR / "materials" / "uk" / "tribe_presentation.pdf",
        "videos": [
            BASE_DIR / "materials" / "uk" / f"tribe_circle_{number}.mp4"
            for number in range(1, 4)
        ],
    },
    "ru": {
        "pdf": BASE_DIR / "materials" / "ru" / "tribe_presentation.pdf",
        "videos": [BASE_DIR / "materials" / "ru" / "tribe_circle_1.mp4"],
    },
}

TEXTS = {
    "uk": {
        "interest": "Тебе цікавить:",
        "tribe_button": "племя",
        "individual_button": "індивідуальна практика",
        "tribe_description": (
            "Племя дарує справжніх друзів, з якими вас об'єднує "
            "спільний трансформаційний досвід. Щоденні завдання, обмін "
            "рефлексією та практичні онлайн-зустрічі протягом 4 тижнів. "
            "Після завершення за бажанням вас додадуть до чату всіх Племен "
            "(їх уже було 5), і ви зможете продовжити свій шлях там"
        ),
        "individual_description": (
            "Індивідуальне пропрацювання страхів та "
            "зажимів з щоденними завданнями та супроводом.\n\n"
            "Також можливо це поєднати з просуванням вашого блогу."
        ),
        "individual_details": "Тут усі деталі та ціни: https://itnstrh.com/",
        "apply_tribe_button": "хочу в племя",
        "apply_individual_button": "хочу",
        "courage": (
            "Радий твоїй сміливості йти на страх. "
            "Можеш розповісти, будь ласка, кружечком про себе і свої запити/страхи?"
        ),
        "materials": "Також надсилаю тобі презентацію та програму племені",
        "final": "Тепер чекаю на твій кружечок) Якщо є якісь питання — пиши",
        "auto_reply": "Дякую дуже! Згодом відпишу)",
    },
    "ru": {
        "interest": "Тебя интересует:",
        "tribe_button": "племя",
        "individual_button": "индивидуальная практика",
        "tribe_description": (
            "Племя дарует настоящих друзей, с которыми вас объединяет "
            "общий трансформационный опыт. Ежедневные задания, обмен рефлексией "
            "и практические онлайн-встречи в течение 4 недель. После прохождения "
            "по желанию вы будете добавлены в чат всех Племен (их уже было 5) "
            "и сможете продолжать путь там"
        ),
        "individual_description": (
            "Индивидуальная проработка страхов и зажимов с ежедневными "
            "заданиями и сопровождением.\n\n"
            "Также это можно совместить с продвижением вашего блога."
        ),
        "individual_details": "Тут все детали и цены: https://itnstrh.com/",
        "apply_tribe_button": "хочу в племя",
        "apply_individual_button": "хочу",
        "courage": (
            "Рад твоей смелости идти навстречу страху. "
            "Можешь, пожалуйста, рассказать кружочком о себе и своих запросах/страхах?"
        ),
        "materials": "Также отправляю тебе презентацию и программу племени",
        "final": "Теперь жду твой кружочек) Если есть какие-то вопросы — пиши",
        "auto_reply": "Спасибо большое! Позже отвечу)",
    },
}

START_INTRO = (
    "Это бот для прохождения отбора в Племя. Племя — это сообщество тех, "
    "кто вместе идет на страх, чтобы обрести легкость, свободу от чужого "
    "мнения и свой внутренний стержень. Также если вы супер-пупер "
    "нарцисс-индивидуалист — здесь можно записаться на индивидуальную "
    "практику...\n\n"
    "______________________________\n\n"
    "Це бот для проходження відбору в Племя. Племя — це спільнота тих, "
    "хто разом іде на страх, щоб здобути легкість, свободу від чужої думки "
    "та свій внутрішній стрижень. Також якщо ви супер-пупер "
    "нарцис-індивідуаліст — тут можна записатися на індивідуальну "
    "практику..."
)


def get_language(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data.get("language", "uk")


async def send_tribe_materials(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    language: str,
):
    texts = TEXTS[language]
    materials = TRIBE_MATERIALS[language]

    await context.bot.send_message(
        chat_id=chat_id,
        text=texts["materials"]
    )

    with materials["pdf"].open("rb") as pdf:
        await context.bot.send_document(
            chat_id=chat_id,
            document=pdf,
            filename="племя.pdf"
        )

    for video_note_path in materials["videos"]:
        with video_note_path.open("rb") as video_note:
            await context.bot.send_video_note(chat_id=chat_id, video_note=video_note)

    await asyncio.sleep(60)

    await context.bot.send_message(
        chat_id=chat_id,
        text=texts["final"]
    )


async def send_tribe_sequence(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    language: str,
):
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(5)
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(5)

    await send_tribe_materials(chat_id, context, language)


def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("українська", callback_data="language_uk")],
        [InlineKeyboardButton("русский", callback_data="language_ru")],
    ])


def start_keyboard(language: str):
    texts = TEXTS[language]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(texts["tribe_button"], callback_data="tribe")],
        [InlineKeyboardButton(texts["individual_button"], callback_data="individual")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(START_INTRO)

    await update.message.reply_text(
        "Обери мову / Выбери язык:",
        reply_markup=language_keyboard()
    )


# ===================== BUTTONS =====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    language = get_language(context)
    texts = TEXTS[language]

    if query.data.startswith("language_"):
        language = query.data.removeprefix("language_")
        context.user_data["language"] = language
        texts = TEXTS[language]

        await query.message.reply_text(
            texts["interest"],
            reply_markup=start_keyboard(language)
        )
        return

    # ===== ПЛЕМЯ =====
    if query.data == "tribe":

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(texts["apply_tribe_button"], callback_data="apply_tribe")]
        ])

        await query.message.reply_text(texts["tribe_description"], reply_markup=keyboard)

    # ===== ИНДИВИДУАЛЬНАЯ =====
    elif query.data == "individual":

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(texts["apply_individual_button"], callback_data="apply_individual")]
        ])

        await query.message.reply_text(texts["individual_description"], reply_markup=keyboard)
        await query.message.reply_text(texts["individual_details"])

    # ===================== APPLY TRIBE =====================

    elif query.data == "apply_tribe":

        username = f"@{user.username}" if user.username else "немає username"

        reply_mode[user.id] = True

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ответить клиенту", callback_data=f"reply_{user.id}")]
        ])

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🔥 ПЛЕМЯ\n\n"
                f"Имя: {user.first_name}\n"
                f"Username: {username}\n"
                f"ID: {user.id}"
            ),
            reply_markup=keyboard
        )

        await query.message.reply_text(
            texts["courage"]
        )

        context.application.create_task(
            send_tribe_sequence(user.id, context, language),
            update=update
        )

    # ===================== APPLY INDIVIDUAL =====================

    elif query.data == "apply_individual":

        username = f"@{user.username}" if user.username else "немає username"

        reply_mode[user.id] = True

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ответить клиенту", callback_data=f"reply_{user.id}")]
        ])

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🔥 ІНДИВІДУАЛЬНА ПРАКТИКА\n\n"
                f"Имя: {user.first_name}\n"
                f"Username: {username}\n"
                f"ID: {user.id}"
            ),
            reply_markup=keyboard
        )

        await query.message.reply_text(
            texts["courage"]
        )

    # ===================== ADMIN REPLY MODE =====================

    elif query.data.startswith("reply_"):

        client_id = int(query.data.split("_")[1])

        reply_mode[ADMIN_ID] = client_id

        await query.message.reply_text("Напиши сообщение клиенту.")


# ===================== UNIVERSAL MESSAGE HANDLER =====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    user_id = user.id

    # ===== ADMIN REPLY =====
    if user_id == ADMIN_ID and user_id in reply_mode:

        client_id = reply_mode[user_id]

        await update.message.copy(chat_id=client_id)

        await update.message.reply_text("Сообщение отправлено ✅")

        del reply_mode[user_id]
        return

    # ===== CLIENT MESSAGE (TEXT / VOICE / VIDEO_NOTE / AUDIO / ANYTHING) =====

    if user_id != ADMIN_ID:

        # отправка админу ВСЕХ сообщений
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "📩 НОВОЕ СООБЩЕНИЕ\n\n"
                f"Имя: {user.first_name}\n"
                f"Username: @{user.username if user.username else 'нет'}\n"
                f"ID: {user.id}"
            )
        )

        await update.message.forward(chat_id=ADMIN_ID)

        # авто-ответ клиенту
        await update.message.reply_text(
            TEXTS[get_language(context)]["auto_reply"]
        )


# ===================== MAIN =====================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # важно: ловим ВСЁ
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("Бот запущен...")

    app.run_polling()


if __name__ == "__main__":
    main()
