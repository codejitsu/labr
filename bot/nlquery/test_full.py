import pytest
import os
import sys

from nlquery import NLQueryEngine

lang = 'en'
query_engine = NLQueryEngine(properties = {'lang': lang})

class TestFull(object):
    def test_get_property(self):
        qa = [
            ('Who is Obama?', '44th President of the United States'),
            ('How tall is Yao Ming?', '2.286'),
            ('Where was Obama born?', 'Kapiolani Medical Center for Women and Children'),
            ('When was Obama born?', 'August 4, 1961'),
            ('Who did Obama marry?', 'Michelle Obama'),
            ('Who is Obama\'s wife?', 'Michelle Obama'),
            ('Who is Barack Obama\'s wife?', 'Michelle Obama'),
            ('Who was Malcolm Little known as?', 'Malcolm X'),
            ('What is the birthday of Obama?', 'August 04, 1961'),
            ('What religion is Obama?', 'Christianity'),
            ('Who did Obama marry?', 'Michelle Obama'),
            ('Who married Obama?', 'Michelle Obama'),
        ]
        for quest, ans in qa:
            resp = query_engine.query(quest)
            assert ans in resp
            print("{}, {}, {}".format(quest, ans, resp))

    def test_find_entity(self):
        qa = [
            ('How many countries are there?', '19'),
            ('Which countries have a population over 1000000000?',
                'People\'s Republic of China, India'),
            ('Which books are written by Douglas Adams?',
                'The Hitchhiker\'s Guide to the Galaxy'),
            ('Who was POTUS in 1945?', 'Truman'),
            ('Who was Prime Minister of Canada in 1945?', 'William'),
            ('Who was CEO of Apple Inc in 1980?', 'Steve Jobs'),
        ]

        for quest, ans in qa:
            resp = query_engine.query(quest)
            assert ans in resp
            print("{}, {}, {}".format(quest, ans, resp))
