import pytest
from dialog import Dialog

class TestBaseClasses(object):
    @pytest.mark.parametrize("text", [
        "Gobbledeguk", "Gibberish", "Wingdings"
    ])
    def test_dialog_abc(self, text):
        class SampleDialog(Dialog):
            def parse(self, text):
                return []

            def interpret(self, sents):
                return sents, 0.0, {}

            def respond(self, sents, confidence):
                return None

        sample = SampleDialog()
        reply, confidence = sample.listen(text)
        assert confidence == 0.0
        assert reply is None
