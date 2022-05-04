import requests
from environs import Env
from google.cloud import dialogflow

env = Env()
env.read_env()


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
    project_id = env('GC_PROJECT_ID')
    url = env('FILE_URL')
    response = requests.get(url)
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


if __name__ == '__main__':
    main()
