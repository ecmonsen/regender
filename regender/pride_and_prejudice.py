# One-off script to gender-swap "Pride and Prejudice" by Jane Austen.
# What makes it specific to that text is the replacement of P&P character
# names with hand-selected, gender-swapped names that were fairly popular,
# according to name indexes, in the late 1800s when Austen was writing.

import argparse
from regender import PatternGenderSwapper
import sys
import io

name_replacements = {
    "William": "Willa",
    "Sarah": "Simon",
    "Sally": "Samuel",
    "Mary": "Michael",
    "Maria": "Martin",
    "Lydia": "Lee",
    "Louisa": "Louis",
    "Lizzy": "Ernie",
    "Kitty": "Kenny",
    "Jane": "John",
    "James": "Julia",
    "Harriet": "Harry",
    "Georgiana": "Gilbert",
    "George": "Grace",
    "Elizabeth": "Ernest",
    "Eliza": "Ern",
    "Denny": "Daisy",
    "Charlotte": "Chester",
    "Charles": "Clara",
    "Catherine": "Clarence",
    "Caroline": "Carl",
    "Anne": "Albert",
    "Fitzwilliam": "Florence",
}

def preprocess(line):
    """
    Preprocess a line of Jane Austen text.

    * insert spaces around double dashes -- 
    :param line: 
    :return: 
    """
    return line.replace("--", " -- ")

def postprocess_word(word):
    return name_replacements.get(word, word)

def postprocess(line):
    for k, v in name_replacements.iteritems():
        line = line.replace(k, v)
    return line


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Text file to gender-swap")
    args = parser.parse_args()

    swapper = PatternGenderSwapper(preprocess=lambda x: preprocess(x),
                                   postprocess_word=lambda y: postprocess_word(y))
    close_fp = False

    if not args.file:
        fp = sys.stdin
    else:
        fp = io.open(args.file, 'r', encoding='utf-8 sig')
        close_fp = True

    for line in swapper.swap_gender(fp):
        print(line.encode('utf-8'))

    if close_fp:
        fp.close()

if __name__ == "__main__":
    main()

