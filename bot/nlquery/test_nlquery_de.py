import pytest
from nlquery import NLQueryEngine

lang = 'de'
engine = NLQueryEngine(properties = {'lang': lang})

class TestNLQueryEngineDe(object):
    @pytest.mark.parametrize("question,answer", [
        ("Wer ist Trump?", "45. Präsident der Vereinigten Staaten"),
        ("Wer ist Donald Trump?", "45. Präsident der Vereinigten Staaten"),
        ("Wer ist Jennifer Lopez?", "US-amerikanische Sängerin, Tänzerin, Schauspielerin und Designerin"),
        ("Was ist ein Smoothie?", "alkoholfreies Fruchtgetränk"),
        ("Wie hoch ist die Zugspitze?", "2962.06"),
        ("Wie alt ist Donald Trump?", "72"),
        ("Wie alt ist Trump?", "72"),
        ("Wann wurde Amazon gegründet?", "July 5, 1994"),
        ("Was ist das Geschäft von Amazon?", "elektronischer Handel"),
        ("Wie heißt die Frau von Trump?", "Marla Maples, Melania Trump, Ivana Trump"),
        #("Wer hat Hitler getötet?", "Test")
        ("Wann wurde Donald Trump geboren?", "June 14, 1946"),
        ("Wann wurde Trump geboren?", "June 14, 1946"),
        ("Wie alt ist Apple?", "42"),
        #("Wie alt ist München?", "42"),
        ("Was ist die Vorwahl von München?", "089"),
        ("Welche Sprache spricht man in Sweden?", "Schwedisch, Jiddisch, Romani, Finnisch, samische Sprachen, Meänkieli"),
        #In welchen Filmen ist Arnold Schwarzenegger zu sehen?
        ("Wo wurde Leibniz geboren?", "Leipzig"),
        ("Wo wurde Amazon gegründet?", "Seattle"),
        ("Wo wurde Apple gegründet?", "Los Altos"),
        ("Wo wurde Donald Trump geboren?", "Jamaica Hospital"),
        ("Stoner Rock", "Musikstil"),
        ("Donald Trump", "45. Präsident der Vereinigten Staaten"),
        ("Wer ist Donald Duck", "Comic- und Zeichentrick-Figur aus dem Disney-Studio"),
        ("Motto von USA", "In God We Trust, E Pluribus Unum")
    ])
    def test_query(self, question, answer):
        reply = engine.query(question, format_='plain')
        assert reply is not None
        assert answer in reply
