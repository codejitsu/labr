import pytest
from dialog import Dialog
from greeting import Greeting

class TestGreetingDialog(object):
    @pytest.mark.parametrize("text", ["Hello!", "hello", "hey", "hi"])
    @pytest.mark.parametrize("user", [None, "jay"], ids=["w/ user", "w/o user"])
    def test_greeting_intro(self, user, text):
        g = Greeting()
        reply, confidence = g.listen(text, user=user)

        assert confidence == 1.0
        assert reply is not None
        assert reply == "Hello, what is your name?"

    @pytest.mark.xfail(reason="a case that must be handled")
    @pytest.mark.parametrize("text", ["My name is Jake", "Hello, I'm Jake."])
    @pytest.mark.parametrize("user", [None, "jkm"], ids = ["w/ user", "w/o user"])
    def test_initial_intro(self, user, text):
        g = Greeting()
        reply, confidence = g.listen(text, user=user)

        assert confidence == 1.0
        assert reply is not None
        assert reply == "Hello, Jake!"

        if user is None:
            user = "jake"

        assert user in g.participants
        assert g.participants[user] == 'Jake'
