import logging
import random

import google
import telegram
import vk_api as vk
from dotenv import load_dotenv

from dialogflow_api import detect_intent_texts
from environs import Env
from vk_api.longpoll import VkEventType, VkLongPoll

from telegram_handler import TelegramLogsHandler


env = Env()

vk_logger = logging.getLogger('vk_logger')


def response(event, vk_api):
    project_id = env('GC_PROJECT_ID')
    session_id = event.user_id
    language_code = env('LANGUAGE_CODE')
    try:
        dialogflow_response = detect_intent_texts(
            project_id,
            session_id,
            event.text,
            language_code
        )
        if not dialogflow_response.intent.is_fallback:
            vk_api.messages.send(
                user_id=event.user_id,
                message=dialogflow_response.fulfillment_text,
                random_id=random.randint(1, 1000)
            )
    except google.auth.exceptions.DefaultCredentialsError as e:
        vk_logger.warning(e)


def main() -> None:
    load_dotenv()
    vk_session = vk.VkApi(token=env('VK_GROUP_TOKEN'))
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_LOGS_CHAT_ID')
    bot = telegram.Bot(token=tg_token)
    vk_logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            response(event, vk_api)


if __name__ == '__main__':
    main()
