import os
import sys
from lango.matcher import *
from lango.matcher import logging
from nltk.parse.stanford import StanfordParser
from collections import OrderedDict

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

MODELS_PATHS = {
    'en':'../tools/stanford/stanford-parser-full-2015-04-20/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz',
    'de': '../tools/stanford/stanford-parser-full-2015-04-20/edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz'
}

def fun(subject, art):
    print("%s,%s" % (subject, art))

def fun2(subject, action, qtype):
    print("%s,%s,%s" % (subject, action, qtype))

def perform_action(action, item, subject, relation=None,
    item_addon=None, item_in=None):

    entity = subject
    if entity == "my":
        entity = "me"
    if relation:
        entity = '{0}.{1}'.format(entity, relation)

    item_props = {'item': item}
    if item_in and item_addon:
        item_props[item_in] = item_addon

    return '{0}.{1}({2})'.format(entity, action, item_props)

def main(argv):
    properties = {
        'lang': 'de'
    }
    parser = StanfordParser(model_path=MODELS_PATHS[properties['lang']])

    qtype_rules = {
        'qtype_t': OrderedDict([
            # What/where/who
            ('( PWS:qtype-o )', {})
        ])
    }
# (S (PWS Wer) (VAFIN ist) (NP (NE Donald) (NN Trump)) ($. ?))
    rules = {
        '( ROOT ( S ( PWS:qtype-o ) ( VAFIN:action-o ) ( NN:subject-o ) ) )': {}
    }

    tree = next(parser.raw_parse('Die Katze'))
    for e in tree:
        print(str(e))
    match_rules(tree, { '( ROOT ( NUR ( NP ( ART:art-o ) ( NN:subject-o ) ) ) )':{} }, fun)

    tree = next(parser.raw_parse('Wer ist Trump?'))
    for e in tree:
        print(str(e))
    match_rules(tree, rules, fun2)

    subj_obj_rules = {
        'subj_t': OrderedDict([
            # my brother / my mother
            ('( NP ( PRP$:subject-o=my ) ( NN:relation-o ) )', {}),
            # Sam's dog
            ('( NP ( NP ( NNP:subject-o ) ( POS ) ) ( NN:relation-o ) )', {}),
            # me
            ('( NP:subject-o )', {}),
        ]),
        'obj_t': OrderedDict([
            # pizza with onions
            ('( NP ( NP:item-O ) ( PP ( IN:item_in-O ) ( NP:item_addon-O ) ) )', {}),
            # pizza
            ('( NP:item-O )', {}),
        ])
    }

    rules2 = {
        # Get me a pizza
        '( ROOT ( S ( VP ( VB:action-o ) ( S ( NP:subj_t ) ( NP:obj_t ) ) ) ) )': subj_obj_rules,
        # Get my mother flowers
        '( ROOT ( S ( VP ( VB:action-o ) ( NP:subj_t ) ( NP:obj_t ) ) ) )': subj_obj_rules,
    }

    tree = next(parser.raw_parse('Find me a pizza with extra cheese.'))

    for e in tree:
        print(str(e))

    print(match_rules(tree, rules2, perform_action))

if __name__ == "__main__":
    main(sys.argv[1:])
