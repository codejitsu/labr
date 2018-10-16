import os
import json
import inflect

from nltk.stem.snowball import SnowballStemmer
from nltk.parse.stanford import StanfordParser
from nltk.tree import Tree
from nltk.util import breadth_first

from dialog import Dialog
import humanize

CONVERSION_PATH = "conversions.json"
MODELS_PATH = '../tools/stanford/stanford-parser-full-2015-04-20/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz'

class Converter(Dialog):
    def __init__(self, conversion_path=CONVERSION_PATH):
        with open(conversion_path, 'r') as f:
            self.metrics = json.load(f)

        self.inflect = inflect.engine()
        self.stemmer = SnowballStemmer('english')
        self.parser = StanfordParser(model_path=MODELS_PATH)

    def parse(self, text):
        parsed = self.parser.raw_parse(text)
        return list(parsed)

    def interpret(self, sents, **kwargs):
        measures = []
        confidence = 0
        results = dict()

        root = sents[0]

        if "WRB" in [tag for word, tag in root.pos()]:
            confidence += .2

            for clause in breadth_first(root, maxdepth=8):
                if isinstance(clause, Tree):
                    if clause.label() in ["S", "SQ", "WHNP"]:
                        for token, tag in clause.pos():
                            if tag in ["NN", "NNS"]:
                                measures.append(token)
                            elif tag in ["CD"]:
                                results["quantity"] = token

            measures = list(set([self.stemmer.stem(mnt) for mnt in measures]))

            if len(measures) == 2:
                confidence += .4
                results["src"] = measures[0]
                results["dst"] = measures[1]

                if results["src"] in self.metrics.keys():
                    confidence += .2
                    if results["dst"] in self.metrics[results["src"]]:
                        confidence += .2

        return results, confidence, kwargs


    def convert(self, src, dst, quantity=1.0):
        src, dst = tuple(map(self.stemmer.stem, (src,dst)))

        if dst not in self.metrics:
            raise KeyError("cannot convert to '{}' units".format(src))
        if src not in self.metrics[dst]['Destination']:
            raise KeyError("cannot convert from {} to '{}'".format(src, dst))

        units = self.metrics.get(dst).get('Units')[
          self.metrics.get(dst).get('Destination').index(src)
        ]

        return units * float(quantity), src, dst

    def round(self, num):
        num = round(float(num), 4)
        if num.is_integer():
            return int(num)
        return num

    def pluralize(self, noun, num):
        return self.inflect.plural_noun(noun, num)

    def numericalize(self, amt):
        if amt > 100.0 and amt < 1e6:
            return humanize.intcomma(int(amt))
        if amt >= 1e6:
            return humanize.intword(int(amt))
        elif isinstance(amt, int) or amt.is_integer():
            return humanize.apnumber(int(amt))
        else:
            return humanize.fractional(amt)

    def respond(self, sents, confidence, **kwargs):
        if confidence < 0.5:
            return "Sorry, I don't know that one."

        try:
            quantity = sents.get('quantity', 1)
            amount, source, target = self.convert(**sents)

            amount = self.round(amount)
            quantity = self.round(quantity)

            source = self.pluralize(source, quantity)
            target = self.pluralize(target, amount)
            verb = self.inflect.plural_verb("is", amount)

            quantity = self.numericalize(quantity)
            amount = self.numericalize(amount)

            return "There {} {} {} in {} {}".format(
                verb, amount, target, quantity, source
            )
        except KeyError as e:
            return "I'm sorry I {}".format(str(e))

if __name__ == "__main__":
    dialog = Converter()
    print(dialog.listen("How many cups are in a gallon?"))
    print(dialog.listen("How many gallons are in 2 cups?"))
    print(dialog.listen("How many tablespoons are in a cup?"))
    print(dialog.listen("How many tablespoons are in 10 cups?"))
    print(dialog.listen("How many tablespoons are in a teaspoon?"))
