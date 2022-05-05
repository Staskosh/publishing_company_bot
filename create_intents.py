import logging
import os

import requests
from dotenv import load_dotenv
from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )


def main() -> None:
    load_dotenv()
    project_id = os.getenv('GC_PROJECT_ID')
    url = os.getenv('FILE_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        intents_text = response.json()
        for display_name, phrases in intents_text.items():
            training_phrases_parts = phrases['questions']
            message_texts = [phrases['answer']]
            create_intent(
                project_id,
                display_name,
                training_phrases_parts,
                message_texts
            )
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        logging.warning(e)


if __name__ == '__main__':
    main()
