from simple_conversation import SimpleConversation
from greeting_aiml import GreetingAiml
from personal_aiml import PersonalAiml
import json
import random
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-l', '--lang', dest='language', help='set bot language', default='de')
    parser.add_argument('-v', "--verbose", dest="verbose", default=False,
                        help="don't print warning messages to stdout")

    args = parser.parse_args()

    verbose = args.verbose
    lang = args.language

    dialogs = [GreetingAiml(verbose), PersonalAiml(verbose)]
    conversation = SimpleConversation(dialogs)

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
