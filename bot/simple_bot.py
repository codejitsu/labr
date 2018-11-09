from simple_conversation import SimpleConversation
from greeting_aiml import GreetingAiml
from personal_aiml import PersonalAiml
import json
import random

if __name__ == '__main__':
    dialogs = [GreetingAiml(), PersonalAiml()]
    conversation = SimpleConversation(dialogs)

    lang = 'de'
    verbose = False

    templates = {}

    with open('templates.json') as templ_file:
        templates = json.load(templ_file)

    while True:
        try:
            line = input('> ')
            response, confidence = conversation.listen(line)

            if confidence == 1.0:
                if verbose:
                    print('BOT: {} (confidence: {})'.format(response, confidence))
                else:
                    print('BOT: {}'.format(response, confidence))
            elif confidence <= 0.8 and confidence > 0:
                if verbose:
                    print('BOT: {} (confidence: {})'.format(response, confidence))
                else:
                    print('BOT: {}'.format(response, confidence))    
            else:
                if verbose:
                    print('BOT: {} (confidence: {})'.format(random.choice(templates[lang]['dont-understand-not-sure']),
                    confidence))
                else:
                    print('BOT: {}'.format(random.choice(templates[lang]['dont-understand-not-sure']),
                    confidence))
        except EOFError:
            print("Bye!")
            sys.exit(0)
