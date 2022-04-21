import logging

from environs import Env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from google.cloud import dialogflow

env = Env()
env.read_env()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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
    reply = detect_intent_texts(project_id, session_id, update.message.text, language_code)
    update.message.reply_text(reply)


def main() -> None:
    tg_token = env("TG_TOKEN")
    env('GOOGLE_APPLICATION_CREDENTIALS')
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, response))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
