import os
import sys

from nlquery import NLQueryEngine

def main(argv):
    lang = 'de'
    engine = NLQueryEngine(properties = {'lang': lang})

    while True:
        try:
            line = input("Enter line: ")
            print(engine.query(line, format_='plain'))
        except EOFError:
            print("Bye!")
            sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
