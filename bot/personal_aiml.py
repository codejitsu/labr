from dialog import Dialog
import aiml_bot

class PersonalAiml(Dialog):
    '''
        mood = excited | good | ok | bad | grumpy | bitch
    '''
    def __init__(self, verbose, mood):
        if verbose:
            print('Mood: {}'.format(mood))

        self.bot = aiml_bot.Bot(learn='personal.aiml', verbose=verbose)
        self.bot.set_predicate('mood', mood)

    def parse(self, text):
        return text

    def interpret(self, sents, **kwargs):
        res = self.bot.respond(sents)
        if not res:
            return res, 0.0, kwargs
        else:
            return res, 1.0, kwargs

    def respond(self, sents, confidence, **kwargs):
        return sents

if __name__ == '__main__':
    dialog = PersonalAiml(True, 'grumpy')
    #import pdb;pdb.set_trace()
    print(dialog.listen("Wie gehts")[0])
    print(dialog.listen("Wie heißt du?")[0])
    print(dialog.listen("Wie alt bist du?")[0])
    print(dialog.listen("Was kannst du machen?")[0])
