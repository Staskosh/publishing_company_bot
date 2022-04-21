import random

from environs import Env
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from tg_publishing_bot import detect_intent_texts

env = Env()
env.read_env()




def response(event, vk_api):
    project_id = env('GC_PROJECT_ID')
    session_id = event.user_id
    language_code = env('LANGUAGE_CODE')
    reply = detect_intent_texts(project_id, session_id, event.text, language_code)
    if reply.intent.is_fallback:
        pass
    else:
        vk_api.messages.send(
        user_id=event.user_id,
        message=reply.fulfillment_text,
        random_id=random.randint(1,1000)
        )


def main() -> None:
    vk_session = vk.VkApi(token=env('VK_GROUP_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            response(event, vk_api)


if __name__ == '__main__':
    main()