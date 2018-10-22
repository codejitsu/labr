import pytest
from nlquery import NLQueryEngine

lang = 'en'
engine = NLQueryEngine(properties = {'lang': lang})

class TestNLQueryEngineEn(object):
    @pytest.mark.parametrize("question,answer", [
        ("Who is Donald Trump?", "45th President of the United States"),
        ("How tall is Donald Trump?", "75.0"),
        ("Where was Trump born?", "Jamaica Hospital"),
        ("When was Donald Trump born?", "June 14, 1946"),
        ("How old is Donald Trump?", "72"),
        ("Who did Trump marry?", "Marla Maples, Melania Trump, Ivana Trump"),
        ("Who is Trump\'s wife?", "Marla Maples, Melania Trump, Ivana Trump"),
        ("Who is Donald Trump\'s wife?", "Marla Maples, Melania Trump, Ivana Trump"),
        ("What is the birthday of Trump?", "June 14, 1946"),
        ("Who married Trump?", "Marla Maples, Melania Trump, Ivana Trump"),
        ("How many books are written by George Orwell?", "13"),
        ("Which books are written by Douglas Adams?", "The Hitchhiker\'s Guide to the Galaxy")
    ])
    def test_query(self, question, answer):
        reply = engine.query(question, format_='plain')
        assert reply is not None
        assert answer in reply
