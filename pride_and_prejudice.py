import argparse
from regender import PatternGenderSwapper
import sys

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

def postprocess(line):
    for k, v in name_replacements.iteritems():
        line = line.replace(k, v)
    return line


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Text file to gender-swap")
    args = parser.parse_args()

    swapper = PatternGenderSwapper(preprocess=lambda x: preprocess(x),
                                   postprocess=lambda y: postprocess(y))
    close_fp = False

    if not args.file:
        fp = sys.stdin
    else:
        fp = open(args.file, 'r')
        close_fp = True

    for line in swapper.swap_gender(fp):
        print(line)

    if close_fp:
        fp.close()

if __name__ == "__main__":
    main()

