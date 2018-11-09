from dialog import Dialog
import aiml_bot

class GreetingAiml(Dialog):
    def __init__(self, verbose):
        self.bot = aiml_bot.Bot(learn='greeting.aiml', verbose=verbose)

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
    dialog = GreetingAiml()
    dialog.bot.set_predicate('USERNAME', 'Alex')
    print(dialog.listen("Hallo!")[0])
    print(dialog.listen("Bis dann")[0])
