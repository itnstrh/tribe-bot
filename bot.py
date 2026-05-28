from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8815394744:AAEW7W3kXzGxv0QjgRKpF_2iXOVwaj3vG7A"
ADMIN_ID = 387155012

# режим ответа клиенту
reply_mode = {}


def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Племя", callback_data="tribe")],
        [InlineKeyboardButton("Індивідуальна практика", callback_data="individual")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Мене цікавить:",
        reply_markup=start_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    # ===== ПЛЕМЯ =====
    if query.data == "tribe":

        text = (
            "Племя — це спільнота тих, хто разом йде на страх. "
            "Для того, щоб здобути свою справжню силу, свободу, "
            "перестати залежати від думки інших і жити своє найкраще життя.\n\n"
            "Щоденні завдання, обмін рефлексією і практичні "
            "онлайн-зустрічі протягом 4х тижнів."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Хочу в племя",
                callback_data="apply_tribe"
            )]
        ])

        await query.message.reply_text(
            text,
            reply_markup=keyboard
        )

    # ===== ИНДИВИДУАЛЬНАЯ =====
    elif query.data == "individual":

        text = (
            "Індивідуальне пропрацювання страхів та"
            "зажимів з щоденними завданнями та супроводом.\n\n"
            "Також можливо це поєднати з просуванням вашого блогу."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Хочу",
                callback_data="apply_individual"
            )]
        ])

        await query.message.reply_text(
            text,
            reply_markup=keyboard
        )

    # ===== ЗАЯВКА ПЛЕМЯ =====
    elif query.data == "apply_tribe":

        username = (
            f"@{user.username}"
            if user.username
            else "немає username"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Ответить клиенту",
                callback_data=f"reply_{user.id}"
            )]
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
            "Заявка відправлена."
        )

    # ===== ЗАЯВКА ИНДИВИДУАЛЬНАЯ =====
    elif query.data == "apply_individual":

        username = (
            f"@{user.username}"
            if user.username
            else "немає username"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Ответить клиенту",
                callback_data=f"reply_{user.id}"
            )]
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
            "Заявка відправлена."
        )

    # ===== ОТВЕТ КЛИЕНТУ =====
    elif query.data.startswith("reply_"):

        client_id = int(
            query.data.split("_")[1]
        )

        reply_mode[ADMIN_ID] = client_id

        await query.message.reply_text(
            "Напиши сообщение клиенту."
        )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.message.from_user.id

    # только админ может отвечать
    if (
        user_id == ADMIN_ID
        and user_id in reply_mode
    ):

        client_id = reply_mode[user_id]

        await context.bot.send_message(
            chat_id=client_id,
            text=update.message.text
        )

        await update.message.reply_text(
            "Сообщение отправлено ✅"
        )

        del reply_mode[user_id]


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Бот запущен...")

    app.run_polling()


if __name__ == "__main__":
    main()