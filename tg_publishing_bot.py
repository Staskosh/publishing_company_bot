import logging

import environs
import google
import telegram
from environs import Env
from google.cloud import dialogflow
from telegram import ForceReply, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)


env = Env()
env.read_env()

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


def detect_intent_texts(project_id, session_id, texts, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=texts, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def response(update: Update, context: CallbackContext) -> None:
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
        if not dialogflow_response.intent.is_fallback:
            update.message.reply_text(dialogflow_response.fulfillment_text)
    except google.auth.exceptions.DefaultCredentialsError as e:
        tg_logger.warning(e)
        pass


def send_tg_message(error):
    tg_token = env("TG_TOKEN")
    tg_chat_id = env('TG_LOGS_CHAT_ID')
    bot = telegram.Bot(token=tg_token)
    tg_logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    tg_logger.warning(error)
    updater = Updater(tg_token)
    updater.idle()


def main() -> None:
    tg_token = env("TG_TOKEN")
    bot = telegram.Bot(token=tg_token)
    tg_chat_id = env('TG_LOGS_CHAT_ID')
    tg_logger.setLevel(logging.INFO)
    tg_logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    try:
        env('GOOGLE_APPLICATION_CREDENTIALS')
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, response))
    except environs.EnvError as e:
        tg_logger.warning(e)
        pass

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
