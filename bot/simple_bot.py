from simple_conversation import SimpleConversation
from greeting_aiml import GreetingAiml
import json
import random

if __name__ == '__main__':
    dialogs = [GreetingAiml()]
    conversation = SimpleConversation(dialogs)

    lang = 'de'

    templates = {}

    with open('templates.json') as templ_file:
        templates = json.load(templ_file)

    while True:
        try:
            line = input('> ')
            response, confidence = conversation.listen(line)

            if confidence == 1.0:
                print('BOT: {} (confidence: {})'.format(response, confidence))
            else:
                print('BOT: {} (confidence: {})'.format(random.choice(templates[lang]['dont-understand-not-sure']),
                confidence))
        except EOFError:
            print("Bye!")
            sys.exit(0)
