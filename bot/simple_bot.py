from simple_conversation import SimpleConversation
from greeting import Greeting
import json
import random

if __name__ == '__main__':
    dialogs = [Greeting()]
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
                print('BOT: {}'.format(response))
            else:
                print('BOT: {}'.format(random.choice(templates[lang]['dont-understand-not-sure'])))
        except EOFError:
            print("Bye!")
            sys.exit(0)
