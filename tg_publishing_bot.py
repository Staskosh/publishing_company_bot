import logging

import environs
import google
import telegram
from dotenv import load_dotenv

from dialogflow_api import detect_intent_texts
from environs import Env
from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)


env = Env()

tg_logger = logging.getLogger("tg_publishing_bot")


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def get_response(update: Update, context: CallbackContext) -> None:
    project_id = env('GC_PROJECT_ID')
    user = update.effective_user
    session_id = user.id
    language_code = env('LANGUAGE_CODE')
    try:
        dialogflow_response = detect_intent_texts(
            project_id,
            session_id,
            update.message.text,
            language_code
        )
        update.message.reply_text(dialogflow_response.fulfillment_text)
    except google.auth.exceptions.DefaultCredentialsError as e:
        tg_logger.warning(e)


def main() -> None:
    load_dotenv()
    tg_token = env("TG_TOKEN")
    bot = telegram.Bot(token=tg_token)
    tg_chat_id = env('TG_LOGS_CHAT_ID')
    tg_logger.setLevel(logging.INFO)
    tg_logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    try:
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, get_response))
    except environs.EnvError as e:
        tg_logger.warning(e)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
