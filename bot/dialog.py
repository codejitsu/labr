import abc

class Dialog(abc.ABC):
    def listen(self, text, response=True, **kwargs):
        sents = self.parse(text)
        sents, confidence, kwargs = self.interpret(sents, **kwargs)

        if response:
            reply = self.respond(sents, confidence, **kwargs)
        else:
            reply = None

        return reply, confidence

    @abc.abstractmethod
    def parse(self, text):
        return []

    @abc.abstractmethod
    def interpret(self, sents, **kwargs):
        return sents, 0.0, kwargs

    @abc.abstractmethod
    def reply(self, sents, confidence, **kwargs):
        return None        
