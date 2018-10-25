from collections import OrderedDict
from lango.matcher import match_rules
from nltk.parse.stanford import StanfordParser
from pattern.en import singularize
from wikidata import WikiData
from utils import first
from api_adapter import LoggingInterface
from answer import Answer

from threading import local

MODELS_PATHS = {
    'en':'../../tools/stanford/stanford-parser-full-2015-04-20/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz',
    'de': '../../tools/stanford/stanford-parser-full-2015-04-20/edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz'
}

"""
Rule for matching a subject and/or property of NP
Matches:
- subject            : Subject to get property of
- prop     (optional): Propert to get of subject

Examples:
- Obama born
- Obama
- Obama's birthday
- Barack Obama's wife
"""
SUBJ_RULES = {
    'en': {
        'subj_rules': OrderedDict([
            # When was (Obama born)
            ('( NP ( NP:subject-o ) ( VP:prop-o ) )', {}),
            # What is (the birth day of Obama)
            ('( NP ( NP:prop-o ) ( PP ( IN ) ( NP:subject-o ) ) )', {}),
            # What is (Obama's birthday)
            ('( NP ( NP:subject-o ( NNP ) ( POS ) ) ( NN/NNS:prop-o ) $ )', {}),
            # What is (Obama's birth day)
            ('( NP ( NP:subject-o ( NNP ) ( POS ) ) ( NN/JJ:prop-o ) ( NN/NNS:prop2-o ) )', {}),
            # What is (Barrack Obama's birthday)
            ('( NP ( NP:subject-o ( NNP ) ( NNP ) ( POS ) ) ( NN/NNS:prop-o ) $ )', {}),
            # What is (Barack Obama's birth day)
            ('( NP ( NP:subject-o ( NNP ) ( NNP ) ( POS ) ) ( NN/JJ:prop-o ) ( NN/NNS:prop2-o ) )', {}),
            ('( NP:subject-o )', {}),
        ])
    },

#(NE Donald) (NN Trump)
    'de': {
        'subj_rules': OrderedDict([
            ('( NE:subject-o) ( NN:prop-o )', {}),

            # When was (Obama born)
            ('( NP ( NP:subject-o ) ( VP:prop-o ) )', {}),
            # What is (the birth day of Obama)
            ('( NP ( NP:prop-o ) ( PP ( IN ) ( NP:subject-o ) ) )', {}),
            # What is (Obama's birthday)
            ('( NP ( NP:subject-o ( NNP ) ( POS ) ) ( NN/NNS:prop-o ) $ )', {}),
            # What is (Obama's birth day)
            ('( NP ( NP:subject-o ( NNP ) ( POS ) ) ( NN/JJ:prop-o ) ( NN/NNS:prop2-o ) )', {}),
            # What is (Barrack Obama's birthday)
            ('( NP ( NP:subject-o ( NNP ) ( NNP ) ( POS ) ) ( NN/NNS:prop-o ) $ )', {}),
            # What is (Barack Obama's birth day)
            ('( NP ( NP:subject-o ( NNP ) ( NNP ) ( POS ) ) ( NN/JJ:prop-o ) ( NN/NNS:prop2-o ) )', {}),
            ('( NP:subject-o )', {}),
        ])
    }
}

"""
'subject_prop_rules' =>

Rule for matching subject property query
Matches:
- qtype               : Question type (who, where, what, when)
- subject             :  Subject to get property of
- prop      (optional): Property to get of subject
- prop2     (optional): Second part of property
- prop3     (optional): Overwrite property
- jj        (optional): Adjective that will be property (e.g. many/tall/high)

Examples:
- What religion is Obama?
- Who did Obama marry?
- Who is Obama?
- Who is Barack Obama's wife?
- How tall is Mt. Everest?
"""

"""
'prop_rules' =>

Rule for getting property of NP or VP
Matches:
prop : Property of instance to match
op   : Operation to match property
value: Value of property

Examples:
- born in 1950
- have population over 100,000
"""

"""
'find_entity_rules' =>

Rules for finding entity queries
Matches:
qtype                   : question type (how many, which)
inst                    : instance of entity to match
prop_match_t  (optional): Parse tree for first property match
prop_match2_t (optional): Parse tree for second property match

Examples:
- How many POTUS are there?
- Which POTUS are born in 1950?
- How many books are written by George Orwell?
- How many countries are in Asia and have population over 100,000?
"""

RULES = {
    'en': {
        'subject_prop_rules': {
            '( ROOT ( SBARQ ( WHNP/WHADVP/WHADJP:qtype_t ) ( SQ:sq_t ) ) )': {
                'qtype_t': OrderedDict([
                    # What religion
                    ('( WHNP ( WDT:qtype-o=what ) ( NN:prop3-o ) )', {}),
                    # How many/tall
                    ('( WHADJP ( WRB:qtype-o ) ( JJ:jj-o ) )', {}),
                    # What/where/who
                    ('( WHNP/WHADVP:qtype-o )', {}),
                ]),
                'sq_t': {
                    # What ethnicity is Obama
                    '( SQ ( VP ( ADVP:prop-o ) ) ( VBZ ) ( VP:suject-o ) )': {},
                    # Who did Obama marry
                    '( SQ ( VBD:action-o ) ( NP:subj_t ) ( VP:prop-o ) )': {
                        'subj_t': SUBJ_RULES['en']['subj_rules']
                    },
                    # Who did
                    '( SQ ( VP ( VBZ/VBD/VBP:action-o ) ( NP:subj_t ) ) )': {
                        'subj_t': SUBJ_RULES['en']['subj_rules']
                    },
                    # Who is Edward Thatch known as
                    '( SQ ( VBZ:action-o ) ( NP:subj_t ) ( VP:prop-o ) )': {
                        'subj_t': SUBJ_RULES['en']['subj_rules'],
                    },
                    # What is Obama
                    '( SQ ( VBZ/VBD/VBP:action-o ) ( NP:subj_t ) )': {
                        'subj_t': SUBJ_RULES['en']['subj_rules']
                    }
                }
            }
        },

        'prop_rules': OrderedDict([
            #
            ('( SQ/VP ( VB/VBP/VBD ) ( VP ( VBN:prop-o ) ( PP ( IN:op-o ) ( NP:value-o ) ) ) )', {}),
            # are in Asia
            ('( SQ/VP ( VB/VBP/VBD=are ) ( PP ( IN:op-o ) ( NP:value-o ) ) )', {}),
            # died from laryngitis
            ('( SQ/VP ( VB/VBP/VBD:prop-o ) ( PP ( IN:op-o ) ( NP:value-o ) ) )', {}),
            # have population over 1000000
            ('( SQ/VP ( VB/VBP/VBD ) ( NP ( NP:prop-o ) ( PP ( IN:op-o ) ( NP/CD/JJ:value-o ) ) ) )', {}),
            ('( SQ/VP ( VB/VBP/VBD ) ( NP:prop-o ) ( NP ( QP ( JJR:op-o ) ( IN ) ( CD:value-o ) ) ) )', {}),
            ('( SQ/VP ( VB/VBP/VBD ) ( NP ( QP ( JJR:op-o ) ( IN=than ) ( NP/CD/JJ:value-o ) ) ( NNS:value_units-o ) ) )', {}),
            ('( PP ( IN:op-o ) ( NP ( NP:value-o ) ( PP:pp_t ) ) )', {}),
            ('( PP ( IN:op-o ) ( NP:value-o ) )', {}),
        ]),

        'find_entity_rules': OrderedDict([
            ('( ROOT ( SBARQ ( WHNP ( WHNP ( WHADJP:qtype-o ) ( NNS:inst-O ) ) ( PP:prop_match_t ) ) ) )', {}),
            ('( ROOT ( SBARQ ( WHNP:qtype-o=who ) ( SQ:sq_t ) ) )', {
                'sq_t': {
                    '( SQ ( VBD/VBZ ) ( NP ( NP:inst-O ) ( PP:prop_match_t ) ) )': {}
                },
            }),
            ('( ROOT ( SBARQ ( WHNP ( WHADJP/WDT/WHNP:qtype-o ) ( NNS/NN/NP:inst-O ) ) ( SQ:sq_t ) ) )', {
                'sq_t': OrderedDict([
                    # are there
                    ('( SQ ( VBP ) ( NP ( EX=there ) ) )', {}),
                    # are in Asia and have population over 100,000
                    ('( SQ ( VP ( VP:prop_match_t ) ( CC ) ( VP:prop_match2_t ) ) )', {}),
                    ('( SQ ( VP:prop_match_t ) )', {}),
                    ('( SQ:prop_match_t )', {}),
                ])
            }),
        ])
    },

    'de': {
        'subject_prop_rules': OrderedDict([
            #Welche Sprache spricht man in Sweden?
            ('( ROOT ( S ( NP ( PWAT:qtype_t ) ( NN:prop-o ) ) ( VVFIN:action-o ) ( PIS ) ( PP:sq_t ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAT:qtype-o )', {})
                ]),
                'sq_t': OrderedDict([
                    ('( PP ( APPR ) ( NN/NE:subject-o ) )', {}),
                    ('( PP ( APPR ) ( ART ) ( NN/NE:subject-o ) )', {})
                ])
            }),

            #Wie heißt die Frau von Trump?
            ('( ROOT ( S ( PWAV/PWS:qtype_t ) ( VVFIN/VAFIN:action-o ) ( NP ( ART ) ( NN/NE:prop-o ) ) ( PP ( APPR ) ( NN/NE:subject-o ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            #Wer ist die Frau von Trump?
            ('( ROOT ( S ( PWS:qtype_t ) ( VAFIN:action-o ) ( NP ( ART ) ( NN/NE:prop-o ) ( PP ( APPR ) ( FM/NN/NE:subject-o ) ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            #Wer ist CEO von Oracle?
            ('( ROOT ( S ( PWAV/PWS:qtype_t ) ( VAFIN:action-o ) ( NN/NE:prop-o ) ( PP ( APPR ) ( NN/NE/FM:subject-o ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            #Wie heißen Kinder von Trump?
            ('( ROOT ( S ( PWAV/PWS:qtype_t ) ( VVFIN/VAFIN:action-o ) ( NP ( NN/NE:prop-o ) ( PP ( APPR ) ( FM/MPN/NN/NE:subject-o ) ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            #Wann wurde Amazon gegründet?
            ('( ROOT ( S ( PWAV/PWS:qtype_t ) ( VAFIN:action-o ) ( NE:subject-o ) ( VP ( VVPP:prop-o ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            #Wann wurde Donald Trump geboren?
            ('( ROOT ( S ( PWAV/PWS:qtype_t ) ( VAFIN:action-o ) ( NP/MPN:subject-o ) ( VP ( VVPP:prop-o ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            #Wann wurde Trump geboren?
            ('( ROOT ( S ( PWAV/PWS:qtype_t ) ( VAFIN:action-o ) ( VP ( NN:subject-o ) ( VVPP:prop-o ) ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV/PWS:qtype-o )', {})
                ])
            }),

            # Wie hoch ist die Zugspitze?
            ('( ROOT ( S ( AP ( PWAV:qtype_t ) ( ADJD:jj-o ) ) ( VAFIN:action-o ) ( MPN/NP/NN:sq_t ) ) )', {
                'qtype_t': OrderedDict([
                    # Wie
                    ('( PWAV:qtype-o )', {})
                ]),
                'sq_t': OrderedDict([
                    # Was ist ein Smoothie?
                    ('( NP ( ART ) ( NN:subject-o ) )', {}),
                    ('( NP:subject-o )', {}),
                    ('( NN:subject-o )', {}),
                    ('( MPN:subject-o )', {}),
                ])
            }),

            # Wer is Trump?
            ('( ROOT ( S ( PWS/PWAV:qtype_t ) ( VAFIN/VVFIN:action-o ) ( MPN/NN/NP/AP:sq_t ) ) )', {
                'qtype_t': OrderedDict([
                    # Was/wo/wer
                    ('( PWS/PWAV:qtype-o )', {})
                ]),
                'sq_t': OrderedDict([
                    # Was ist ein Smoothie?
                    ('( NP ( ART ) ( NN:subject-o ) )', {}),
                    ('( MPN/NN/NP:subject-o )', {}),
                    ('( AP/NP:subject-o )', {})
                ])
            })
        ]),

        'prop_rules': OrderedDict([
            #
            ('( SQ/VP ( VB/VBP/VBD ) ( VP ( VBN:prop-o ) ( PP ( IN:op-o ) ( NP:value-o ) ) ) )', {}),
            # are in Asia
            ('( SQ/VP ( VB/VBP/VBD=are ) ( PP ( IN:op-o ) ( NP:value-o ) ) )', {}),
            # died from laryngitis
            ('( SQ/VP ( VB/VBP/VBD:prop-o ) ( PP ( IN:op-o ) ( NP:value-o ) ) )', {}),
            # have population over 1000000
            ('( SQ/VP ( VB/VBP/VBD ) ( NP ( NP:prop-o ) ( PP ( IN:op-o ) ( NP/CD/JJ:value-o ) ) ) )', {}),
            ('( SQ/VP ( VB/VBP/VBD ) ( NP:prop-o ) ( NP ( QP ( JJR:op-o ) ( IN ) ( CD:value-o ) ) ) )', {}),
            ('( SQ/VP ( VB/VBP/VBD ) ( NP ( QP ( JJR:op-o ) ( IN=than ) ( NP/CD/JJ:value-o ) ) ( NNS:value_units-o ) ) )', {}),
            ('( PP ( IN:op-o ) ( NP ( NP:value-o ) ( PP:pp_t ) ) )', {}),
            ('( PP ( IN:op-o ) ( NP:value-o ) )', {}),
        ]),

        'find_entity_rules': OrderedDict([
            ('( ROOT ( SBARQ ( WHNP ( WHNP ( WHADJP:qtype-o ) ( NNS:inst-O ) ) ( PP:prop_match_t ) ) ) )', {}),
            ('( ROOT ( SBARQ ( WHNP:qtype-o=who ) ( SQ:sq_t ) ) )', {
                'sq_t': {
                    '( SQ ( VBD/VBZ ) ( NP ( NP:inst-O ) ( PP:prop_match_t ) ) )': {}
                },
            }),
            ('( ROOT ( SBARQ ( WHNP ( WHADJP/WDT/WHNP:qtype-o ) ( NNS/NN/NP:inst-O ) ) ( SQ:sq_t ) ) )', {
                'sq_t': OrderedDict([
                    # are there
                    ('( SQ ( VBP ) ( NP ( EX=there ) ) )', {}),
                    # are in Asia and have population over 100,000
                    ('( SQ ( VP ( VP:prop_match_t ) ( CC ) ( VP:prop_match2_t ) ) )', {}),
                    ('( SQ ( VP:prop_match_t ) )', {}),
                    ('( SQ:prop_match_t )', {}),
                ])
            }),
        ])
    }
}

class NLQueryEngine(LoggingInterface):
    """
    Grammar mapping for knowledge queries of the form:
    - What is the X of Y
    - What is X's Y
    """

    def __init__(self, properties={'lang':'en'}):
        LoggingInterface.__init__(self)
        self.parser = StanfordParser(model_path=MODELS_PATHS[properties['lang']])
        self.wd = WikiData()
        self.wd.set_properties(properties)
        self.properties = properties

    def subject_query(self, qtype, subject, action, jj=None, prop=None, prop2=None, prop3=None):
        """Transforms matched context into query parameters and performs query

        Args:
            qtype: Matched type of query (what, who, where, etc.)
            subject: Matched subject (Obama)
            action: Matched verb action (is, was, ran)
            jj (optional): Matched adverb
            prop (optional): Matched prop
            prop2 (optional): Matched prop
            prop3 (optional): Matched prop

        Returns:
            Answer: Answer from query, or empty Answer if None
        """
        if (self.properties['lang'] == 'en'):
            if jj == 'old':
                # How old is Obama?
                prop = 'age'

            if jj in ['tall', 'high']:
                # How tall is Yao Ming / Eifel tower?
                prop = 'height'
        elif (self.properties['lang'] == 'de'):
            if jj == 'alt':
                # Wie alt ist Obama?
                prop = 'age'

            if jj in ['hoch', 'groß']:
                # Wie hoch ist die Zugspitze?
                prop = 'height'

            if prop in ['sprache', 'sprachen']:
                # Welche Sprache spricht man in Sweden?
                prop = 'language official'

        if prop2:
            prop = prop + ' ' + prop2

        if prop3 and not prop:
            prop = prop3

        if not prop:
            if self.properties['lang'] == 'en' and action not in ['is', 'was']:
                prop = action
            elif self.properties['lang'] == 'de' and action not in ['ist', 'sind', 'war', 'hat', 'wurde', 'bedeutet']:
                prop = action

        ans = self.get_property(qtype, subject, prop)
        if not ans:
            ans = Answer()

        ans.params = {
            'qtype': qtype,
            'subject': subject,
            'prop': prop,
        }
        return ans

    def get_prop_tuple(self, prop=None, value=None, op=None, value_units=None, pp_t=None):
        """Returns a property tuple (prop, value, op). E.g. (population, 1000000, >)

        Args:
            prop (str): Property to search for (e.g. population)
            value (str): Value property should equal (e.g. 10000000)
            op (str): Operator for value of property (e.g. >)

        Returns:
            tuple: Property tuple, e.g: (population, 10000000, >)
        """

        self.info('Prop tuple: {0},{1},{2},{3},{4}', prop, value, op, value_units, pp_t)

        if op in ['in', 'by', 'of', 'from']:
            oper = op
        elif op in ['over', 'above', 'more', 'greater']:
            oper = '>'
        elif op in ['under', 'below', 'less']:
            oper = '<'
        else:
            self.error('NO OP {0}', op)
            return None

        # Infer property to match value
        if prop is None:
            if value_units is not None:
                if value_units in ['people']:
                    prop = 'population'
                if not prop:
                    return None

        props = [(prop, value, oper)]

        if pp_t:
            prop_tuple = match_rules(pp_t, RULES[properties['lang']]['prop_rules'], self.get_prop_tuple)
            if not prop_tuple:
                return None
            props += prop_tuple

        return props

    def find_entity_query(self, qtype, inst, prop_match_t=None, prop_match2_t=None):
        """Transforms matched context into query parameters and performs query for
        queries to find entities

        Args:
            qtype (str): Matched type of query (what, who, where, etc.)
            inst (str): Matched instance of entity to match (Obama)
            action (str): Matched verb action (is, was, ran)
            prop_match_t (Tree): Matched property Tree
            prop_match2_t (Tree): Matched property Tree

        Returns:
            Answer: Answer from query, or empty Answer if None
        """

        props = []
        if prop_match_t:
            prop = match_rules(prop_match_t, RULES[self.properties['lang']]['prop_rules'], self.get_prop_tuple)

            if not prop:
                return

            props += prop

        if prop_match2_t:
            prop = match_rules(prop_match2_t, RULES[self.properties['lang']]['prop_rules'], self.get_prop_tuple)

            if not prop:
                return

            props += prop

        if not inst.isupper():
            inst = singularize(inst)

        ans = self.wd.find_entity(qtype, inst, props)
        if not ans:
            ans = Answer()

        ans.params = {
            'qtype': qtype,
            'inst': inst,
            'props': props,
        }
        return ans

    def get_property(self, qtype, subject, prop):
        """Gets property of a subject
        Example:
            get_property('who', 'Obama', 'wife') = 'Michelle Obama'

        Args:
            subject: Subject to get property of
            prop: Property to get of subject

        Todo:
            * Add other APIs here

        Returns:
            Answer: Answer from query
        """
        return self.wd.get_property(qtype, subject, prop)

    def preprocess(self, sent):
        """Preprocesses a query by adding punctuation"""
        if sent[-1] != '?':
            sent = sent + '?'
        return sent

    def cleanup(self, sent):
        """Remove some stop words"""
        stopwords = ['der', 'die', 'das', 'ein', 'eine', 'einen']
        words = sent.split()

        result = [word for word in words if word.lower() not in stopwords]

        return ' '.join(result)

    def query(self, sent, format_='plain'):
        """Answers a query

        If format is plain, will return the answer as a string
        If format is raw, will return the raw context of query

        Args:
            sent: Query sentence
            format_: Format of answer to return (Default to plain)

        Returns:
            dict: Answer context
            str: Answer as a string

        Raises:
            ValueError: If format_ is incorrect
        """

        sent = self.preprocess(sent)
        sent = self.cleanup(sent)
        tree = next(self.parser.raw_parse(sent))

        pos = [tag for word, tag in tree.pos()]

        if self.properties['lang'] == 'de':
            if len(set(['PWS', 'PWAV', 'PWAT']) & set(pos)) == 0:
                print("Tree before:")
                for e in tree:
                    print(str(e))

                sent = "Was ist " + sent
                tree = next(self.parser.raw_parse(sent))
        # TODO
        #elif self.properties['lang'] == 'en':
        #    if len(set(['WHNP']) & set(pos)) == 0:
        #        print("Tree before:")
        #        for e in tree:
        #            print(str(e))
        #
        #        sent = "What is " + sent
        #        tree = next(self.parser.raw_parse(sent))

        context = {'query': sent, 'tree': tree}

        for e in tree:
            print(str(e))

        ans = first([
            match_rules(tree, RULES[self.properties['lang']]['find_entity_rules'], self.find_entity_query),
            match_rules(tree, RULES[self.properties['lang']]['subject_prop_rules'], self.subject_query),
        ])

        print("-> " + str(ans))

        if not ans:
            ans = Answer()

        ans.query = sent
        ans.tree = str(tree)

        if format_ == 'raw':
            return ans.to_dict()
        elif format_ == 'plain':
            return ans.to_plain()
        else:
            raise ValueError('Undefined format: %s' % format_)
